import string
import time
from ast import literal_eval
from contextlib import contextmanager
from functools import partial
from hashlib import md5

from devapp.tools import walk_dir

from lcdoc.mkdocs.tools import MDPlugin, app, config_options, find_md_files
from lcdoc.tools import (
    OD,
    dirname,
    exists,
    flatten,
    os,
    project,
    read_file,
    unflatten,
    write_file,
)


def find_pages(find, config, stats):
    ev = [i.strip() for i in os.environ.get('find_pages', '').split(',')]
    ev = [i for i in ev if i]
    find.extend(ev)
    find = list(set(find))
    stats['find_terms'] = len(find)
    if not find:
        return
    fnd = []
    for m in find:
        found = find_md_files(match=m, config=config)
        if not found:
            app.info('No pages found', match=m)
        else:
            fnd.extend(found)
    stats['matching'] = len(fnd)
    return fnd


class autodocs:
    def do_spec(pconfig, name, spec, config, stats):
        """entry point from mkdocs.yml config"""
        d_src = project.root() + '/' + spec.get('src-dir', 'build/autodocs')
        if not exists(d_src):
            return app.warning('No autodocs source', name=name, **spec)
        d_target = project.root() + '/docs/autodocs/' + name
        autodocs.link_over(d_src, d_target)
        d = 'autodocs/%s:follow' % name
        found = find_pages([d], config, stats)
        if not found:
            return
        s = spec.get('nav', 'autodocs')
        autodocs.insert_nav_plain(config['nav'], found, s)
        S.dir = d_target
        S.spec = spec
        S.plugin_conf = pconfig
        S.stats = stats
        S.build()

    def link_over(d_src, d_target):
        if exists(d_target):
            if os.readlink(d_target) == d_src:
                return
            os.unlink(d_target)
        d = os.path.dirname(d_target)
        if not exists(d):
            os.makedirs(d, exist_ok=True)
        os.symlink(d_src, d_target)
        app.info('Created symlink', d_src=d_src, d_target=d_target)

    def insert_nav_plain(nav, found, ins):
        if isinstance(nav, str):
            return
        if isinstance(nav, dict):
            return [autodocs.insert_nav_plain(v, found, ins) for v in nav.values()]
        if ins in nav:
            i = nav.index(ins)
            nav.pop(i)
            return [nav.insert(i, k) for k in reversed(found)]
        [autodocs.insert_nav_plain(i, found, ins) for i in nav]


hsh = lambda src: md5(src.encode('utf-8')).hexdigest()


def scan_d_autodocs(typ):
    files = walk_dir(S.dir, crit=lambda d, fn: fn.endswith(typ))
    app.info('have %s files' % typ, json=files)
    return files


now = time.time

from lcdoc.mkdocs.lp.plugs.kroki import run as kroki


class S:
    dir = spec = plugin_conf = stats = None

    def build():
        S.graph_easy.build()
        S.plant.build()

    @contextmanager
    def has_changed(fn, ext):
        src = read_file(fn)
        fnb = fn.rsplit(ext, 1)[0]
        sfn, fnhsh, skip = '%s.svg' % fnb, '%s%s.md5' % (fnb, ext), False
        cur_hash = hsh(src)
        if exists(sfn):
            if read_file(fnhsh, dflt='') == cur_hash:
                app.debug('graph up to date', fn=fn)
                sfn, src = (None, None)
        yield (sfn, src)
        write_file(fnhsh, cur_hash)

    class graph_easy:
        cmd = lambda: 'graph-easy'

        def build():
            S.stats['graph_easy_count'] = 0
            S.stats['graph_easy_built_count'] = 0
            S.stats['graph_easy_build_time'] = 0
            S.graph_easy.files = fs = scan_d_autodocs('.graph_easy.src')
            if not fs:
                return app.info('no .graph_easy.src files')
            if not S.graph_easy.cmd():
                app.die('have no graph_easy resource')

            [S.graph_easy.create(f) for f in fs]

        def create(fn):
            """check if the src changed via a hash written at last create"""
            S.stats['graph_easy_count'] += 1
            with S.has_changed(fn, '.graph_easy.src') as nfos:
                if not nfos[0]:
                    return
                fn_svg, src = nfos
                app.info('rebuilding', fmt='svg', fn=fn_svg)
                cmd = '"%s" --as %s --output "%s" "%s"'
                cmd = cmd % (S.graph_easy.cmd(), 'svg', fn_svg, fn,)
                t0 = now()
                err = os.system(cmd)
                if err:
                    app.die('svg creation failed', fn=fn, cmd=cmd)
                S.stats['graph_easy_built_count'] += 1
                S.stats['graph_easy_build_time'] += now() - t0

    class plant:
        def build():
            S.stats['plantuml_count'] = 0
            S.stats['plantuml_built_count'] = 0
            S.stats['plantuml_build_time'] = 0
            S.plant.files = fs = scan_d_autodocs('.plantuml')
            if not fs:
                return app.info('no .plantuml files')
            # import base64, zlib, requests
            # import httpx as requests

            # st = None
            # if FLG.plantuml_style != 'default':
            #     # also in use there for the 'normal' mkdocs plantuml_markdown inline plants:
            #     fn_st = d_assets() + '/mkdocs/lcd/assets/plantuml/%s' % FLG.plantuml_style
            #     if not exists(fn_st):
            #         app.die('Style not found', fn=fn_st)
            #     st = read_file(fn_st, dflt='')

            for f in fs:
                with S.has_changed(f, '.plantuml') as nfos:
                    S.stats['plantuml_built_count'] += 1
                    if not nfos[0]:
                        continue
                    fn_svg, src = nfos
                    t0 = now()

                    S.stats['plantuml_count'] += 1
                    res = kroki(
                        src,
                        {
                            'mode': 'kroki:plantuml',
                            'puml': 'dark_blue',
                            'get_svg': True,
                        },
                    )
                    # g = base64.urlsafe_b64encode(zlib.compress(s.encode('utf-8')))
                    write_file(fn_svg, res)
                    app.info('created plant svg', fn=fn_svg)
                    S.stats['plantuml_build_time'] += now() - t0

            # now, insert the svgs INTO the md files, inline. Then mouse overs work:
            # the md files got placeholders for the svgs, while pytesting:
            all_mds_with_plants = set([fnp.rsplit('/', 2)[0] for fnp in fs])
            dir_autodocs = S.dir + '/'
            for md in all_mds_with_plants:
                s = read_file(md + '.md')
                for f in [i for i in fs if i.startswith(md)]:
                    fsvg = f.replace('.plantuml', '.svg')
                    svg = (
                        read_file(fsvg).split('>', 1)[1].strip().split('<!--MD5', 1)[0]
                    )
                    if not svg.endswith('</svg>'):
                        svg += '</g></svg>'
                    # testname (e.g. test02_foo) for links building in js
                    n_test = fsvg.rsplit('/', 2)[-2]
                    id = '<svg pth_rel="%s/" id="%s" class="call_flow_chart" '
                    id = id % (n_test, n_test)
                    svg = svg.replace('<svg ', id)
                    fsvg = fsvg.rsplit(dir_autodocs, 1)[1]
                    app.info('Embedding svg into md', md=md, svg=f)
                    tsvg = '[svg_placeholder:%s]' % fsvg
                    s = s.replace(tsvg, svg)
                write_file(md + '.md', s)
