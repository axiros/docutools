#!/usr/bin/env python
"""
Add various autogeneratable pages to the docs

See the Flags (-h) regarding possibilities.
"""
import os
from functools import partial


import time, json
from devapp.tools import FLG, project, gitcmd, parse_kw_str
from devapp.app import app, run_app, system, do as app_do

from pymdownx import slugs
from theming.formatting import markdown
from inflection import humanize
from devapp.tools import deindent, cast
from lcdoc.auto_docs import mark_auto_created

from devapp.testing.auto_docs import func_title


# from operators.testing.auto_docs import dir_pytest_base
from devapp.tools import project, read_file, write_file
from hashlib import md5
import shutil


def do(action, *a, track=False, **kw):
    if track:
        S.actions.add(action.__qualname__)
    return app_do(action, *a, **kw)


class Flags:
    """After test runs with write_build_log on we create images and copy to docs folder
    See the duties of this repo regarding usage.
    """

    # activated via: main = partial(run_app, run, flags=Flags)

    autoshort = ''

    class gen_theme_link:
        """Link additional assets (e.g. termcast) to docs/theme"""

        d = False

    class gen_change_log:
        n = 'Create a changelog (using git-changelog)'
        d = False

    class gen_mod_docs:
        n = 'Supply list of module files to insert into "# :automodocs:" block in mkdocs.yml'
        d = []

    class gen_last_modify_date:
        n = 'Add a modified date into index.md.'
        d = False

    class gen_dev_version_warning:
        n = 'Inform prominently in index.md about development versions of libs in $PYTHONPATH, at time of docs generation.'
        d = True

    class kroki_server:
        d = 'https://kroki.io'

    class plantuml_style:
        t = ['dark_blue', 'default']
        d = 'dark_blue'

    class gen_auto_docs:
        """
        Requires
        - a completed pytest run with autodocs generation done, into build/autodocs
        - a mkdocs section telling us where to insert generated pages
        On autoinsertion we sort by name.
        Insertion marker: Two lines with '# :autodocs:'
        """

        n = 'scan build/autodocs directory for pytest result pages, link to docs, add to mkdocs.yml'
        d = False

    class lit_prog_evaluation:
        n = 'Evaluate literal programming stanzas in all matching md.lp source files, generating secondary .md files. Say md to match all.'
        d = ''

    class lit_prog_evaluation_step_mode:
        n = 'Pause before and after each evaluation block, waiting for user input'
        d = False

    class lit_prog_evaluation_monitor:
        'Sets lit_prog_on_err_keep_running to True'
        n = 'Enable the file monitor for re-eval runs of any matching changed .mp.lp file'
        d = False

    class lit_prog_skip_existing:
        n = 'Intended for CI: When seconary .md pages had been committed, e.g. built while authoring, CI will not re-evaluate those pages at presence of that flag'
        d = False

    class lit_prog_on_err_keep_running:
        'default is to exit and analyse errors in terminal'
        n = 'Set this to True if you want rendering errors to be displayed in the markdown file'
        d = False

    class lit_prog_evaluation_timeout:
        n = 'Global evaluation timeout. On busy build servers  you might want to set higher, e.g. 5'
        d = 1

    class lit_prog_debug_matching_blocks:
        """Hint: You can add a matching not interpreted keyword with that value at every block you want to have run."""

        n = 'Evaluate only blocks whose headers contain given subtring and print eval result on stdout'
        d = ''

    class add_pyproject_infos_to_mkdocs:
        n = 'Repository and homepage from pyproject.toml into mkdocs.yml'
        d = False

    class gen_credits_page:
        n = 'Scans poetry.lock file and creates a page with all packages'
        d = False


# --------------------------------------------------------------------- tools/  actions
class S:
    d_root = None
    graph_easy = None
    operators = {}
    actions = set()
    lp_files = {}
    lp_stepmode = False
    lp_evaluation_timeout = 1
    lp_on_err_keep_running = True

    class stats:
        count_plantuml = 0
        count_graph_easy = 0
        count_built = 0
        count_operators = 0
        count_lp_blocks = 0
        build_time = 0


stats = lambda: {k: getattr(S.stats, k) for k in dir(S.stats) if not k.startswith('_')}
hsh = lambda src: md5(src.encode('utf-8')).hexdigest()
exists = os.path.exists


now = time.time
dirname = os.path.dirname


get_graph_easy = lambda: 'graph-easy'  # must be in path


class Credits:
    TP = '''
    |Package | Description | Version | License
    |- | - | - | -
    %s
    '''
    TC = '''
    # Credits

    Listed below all the python dependencies of _ME_

    ## Run Dependencies

    _RD_

    ## Dev  Dependencies

    _DD_

    ## Indirect Dependencies

    _ID_


    These projects were used to *build* _PN_

    [`python`](https://www.python.org/) |
    [`poetry`](https://poetry.eustace.io/) |
    [`copier-poetry`](https://github.com/pawamoy/copier-poetry)

    **Many thanks to all authors, for all these brilliant software packages!**


    '''

    def fetch_pypi(pkg, attrs):
        import httpx

        app.info('from pypi', pkg=pkg)
        p = httpx.get('https://pypi.python.org/pypi/%s/json' % pkg)
        p = p.json()['info']
        p['home-page'] = p['home_page'] or p['project_url'] or p['package_url']
        p = {_: p[_] for _ in attrs}
        return p

    def create_credits_page(page):
        from jinja2 import StrictUndefined
        from jinja2.sandbox import SandboxedEnvironment
        from pip._internal.commands.show import search_packages_info  # noqa

        import toml
        from itertools import chain

        def get_credits_data() -> dict:
            """
            Return data used to generate the credits file.

            Returns:
                Data required to render the credits template.
            """
            project_dir = S.d_root
            # metadata = toml.load(project_dir + "/pyproject.toml")["tool"]["poetry"]

            lock_data = project.lock_data()
            project_name = project.name()

            direct_dependencies = {dep.lower() for dep in project.dependencies()}
            dev_dependencies = {dep.lower() for dep in project.dev_dependencies()}
            'python' in direct_dependencies and direct_dependencies.remove('python')
            indirect_dependencies = {
                pkg['name'].lower() for pkg in lock_data['package']
            }
            indirect_dependencies -= direct_dependencies
            indirect_dependencies -= dev_dependencies
            dependencies = (
                direct_dependencies | dev_dependencies | indirect_dependencies
            )

            packages = {}
            attrs = ('name', 'home-page', 'license', 'version', 'summary')
            for pkg in search_packages_info(dependencies):
                pkg = {_: pkg[_] for _ in attrs}
                packages[pkg['name'].lower()] = pkg
            ds = dependencies
            for dependency in dependencies:
                if dependency not in packages:
                    pkg = Credits.fetch_pypi(dependency, attrs)
                    packages[pkg['name'].lower()] = pkg
                else:
                    app.info('found', dependency=dependency)

            for d in indirect_dependencies:
                if not d in packages:
                    app.warn('Not found in packages', dependency=d)
                    continue
                packages[d]['for'] = [
                    packages[k['name']]
                    for k in lock_data['package']
                    if d in k.get('dependencies', ())
                ]

            lnk = lambda p: '[`%(name)s`](%(home-page)s)' % p
            lico = lambda p: (p.get('license') or 'n.a.').replace('UNKNOWN', 'n.a.')

            def lic(p):
                l = lico(p)
                if l.startswith('http'):
                    l = '[%s](%s)' % ((l + '///').split('/')[3], l)
                for k in 'license', 'License', 'version', 'Version':
                    l = l.replace(k, '')
                return l

            def smry(p):
                s = p['summary']
                f = ' '.join([lnk(k) for k in p.get('for', ())])
                return s + ' ' + f

            def tbl(what, all=packages):
                ps = [packages[n] for n in what if n in packages]
                ps = [['', lnk(p), smry(p), p['version'], lic(p)] for p in ps]
                r = ['|'.join(l) for l in ps]
                return Credits.TP % '\n'.join(r)

            t = Credits.TC
            t = t.replace('_ME_', '`%s`' % project_name)
            t = t.replace('_RD_', tbl(sorted(direct_dependencies)))
            t = t.replace('_DD_', tbl(sorted(dev_dependencies)))
            t = t.replace('_ID_', tbl(sorted(indirect_dependencies)))
            t = t.replace('_PN_', project_name)
            return t

        app.info('Regenerating', page=page)  # noqa: WPS421 (print)
        b = get_credits_data()
        app.info('writing', page=page)
        b = mark_auto_created(b)
        write_file(page, b)


Credits.TP = deindent(Credits.TP)
Credits.TC = deindent(Credits.TC)
import sys
from devapp.tools import walk_dir

d_autodocs = lambda: project.root() + '/docs/autodocs'
fn_autodocs_refs = lambda: d_autodocs() + '/references.md'


def scan_d_autodocs(typ):
    files = walk_dir(d_autodocs(), crit=lambda d, fn: fn.endswith(typ))
    app.info('have %s files' % typ, json=files)
    return files


from contextlib import contextmanager


class SVGs:
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

    def create_graph_easy_svg(fn):
        """check if the src changed via a hash written at last create"""
        S.stats.count_graph_easy += 1
        with SVGs.has_changed(fn, '.graph_easy.src') as nfos:
            if not nfos[0]:
                return
            fn_svg, src = nfos
            app.info('rebuilding', fmt='svg', fn=fn_svg)
            cmd = '"%s" --as %s --output "%s" "%s"' % (S.graph_easy, 'svg', fn_svg, fn)
            t0 = now()
            err = os.system(cmd)
            if err:
                app.die('svg creation failed', fn=fn, cmd=cmd)
            S.stats.count_built += 1
            S.stats.build_time += now() - t0

    def create_if_present():
        SVGs.create_graph_easy_svgs()
        SVGs.create_plantuml_svgs()

    def create_graph_easy_svgs():
        S.graph_easy_files = fs = scan_d_autodocs('.graph_easy.src')
        if not fs:
            return app.info('no .graph_easy.src files')
        S.graph_easy = g = get_graph_easy()
        if not g:
            app.die('have no graph_easy resource')

        [SVGs.create_graph_easy_svg(f) for f in fs]

    def create_plantuml_svgs():
        S.plantuml_files = fs = scan_d_autodocs('.plantuml')
        if not fs:
            return app.info('no .plantuml files')
        # import base64, zlib, requests
        import httpx as requests

        st = None
        if FLG.plantuml_style != 'default':
            # also in use there for the 'normal' mkdocs plantuml_markdown inline plants:
            fn_st = d_assets() + '/mkdocs/lcd/assets/plantuml/%s' % FLG.plantuml_style
            if not exists(fn_st):
                app.die('Style not found', fn=fn_st)
            st = read_file(fn_st, dflt='')

        for f in fs:
            with SVGs.has_changed(f, '.plantuml') as nfos:
                if not nfos[0]:
                    continue
                fn_svg, src = nfos

                S.stats.count_plantuml += 1
                if st:
                    src = src.replace('@startuml', '@startuml\n' + st)
                # g = base64.urlsafe_b64encode(zlib.compress(s.encode('utf-8')))
                try:
                    res = None
                    # res = requests.post('https://kroki.io/plantuml/svg', data=s)
                    res = requests.post(FLG.kroki_server + '/plantuml/svg', data=src)
                    # res = requests.get(
                    #    FLG.kroki_server + '/plantuml/svg/' + g.decode('utf-8')
                    # )
                    if not res.status_code < 300:
                        raise Exception(
                            'kroki_server: [%s] not [200]' % res.status_code
                        )
                except Exception as ex:
                    app.die(
                        'No svg from kroki', exc=ex, resp=getattr(res, 'text', 'n.a.')
                    )
                write_file(fn_svg, res.text)
                app.info('created plant svg', fn=fn_svg)

        # now, insert the svgs INTO the md files, inline. Then mouse overs work:
        # the md files got placeholders for the svgs, while pytesting:
        all_mds_with_plants = set([fnp.rsplit('/', 2)[0] for fnp in fs])
        dir_autodocs = d_autodocs() + '/'
        for md in all_mds_with_plants:
            try:
                s = read_file(md + '.md')
            except Exception as ex:
                print('breakpoint set')
                breakpoint()
                keep_ctx = True
            for f in [i for i in fs if i.startswith(md)]:
                fsvg = f.replace('.plantuml', '.svg')
                svg = read_file(fsvg).split('>', 1)[1].strip().split('<!--MD5', 1)[0]
                if not svg.endswith('</svg>'):
                    svg += '</g></svg>'
                # testname (e.g. test02_foo) for links building in js
                n_test = fsvg.rsplit('/', 2)[-2]
                id = '<svg id="%s" class="call_flow_chart" ' % n_test
                svg = svg.replace('<svg ', id)
                fsvg = fsvg.rsplit(dir_autodocs, 1)[1]
                app.info('Embedding svg into md', md=md, svg=f)
                tsvg = '[svg_placeholder:%s]' % fsvg
                s = s.replace(tsvg, svg)
            write_file(md + '.md', s)


class Refs:
    def read_flow_json(fn_flow):

        """Create a page with all ops with reference to examples where it occurs in flows.json"""
        s = json.loads(read_file(fn_flow))
        names = [n.get('name') for n in s if n.get('name')]
        all = S.operators

        def mklnk(n, fn=fn_flow):
            # fn '/home/gk/repos/lc-python/docs/autodocs/tests/operators/test_op_ax_socket/SingleOperator.test01_simple/_prebuild_.graph_easy.src.flow.json'
            # want link to:
            # http://127.0.0.1:8000/autodocs/tests/operators/test_op_ax_socket/#tests/operators/test_op_ax_socket/SingleOperator.test01_simple
            # (the anchor jump mark was set by call_flow_logging, when creating the .md)

            # which is in md, as seen from refs page in autodocs: [../tests/operators/test_op_ax_socket/#tests/operators/test_op_ax_socket/SingleOperator.test01_simple]

            p = fn.split(d_autodocs(), 1)[1]
            p1 = p.rsplit('/', 1)[0]
            md, tn = p1.rsplit('/', 1)
            r = '[`%s`](..%s/#%s)' % (tn, md, p1[1:])
            return r

        [all.setdefault(n, []).append(mklnk(n)) for n in names]

    def create_if_present():
        S.flow_files = fs = scan_d_autodocs('.flows.json')
        if not fs:
            return app.info('no flow files')
        [do(Refs.read_flow_json, f) for f in fs]

    def make_examples_refs_page_if_operators_present():
        all = S.operators
        if not all:
            return app.info('no operators')
        fn = fn_autodocs_refs()

        app.info('building refs page', fn=fn)
        r = ['# Operators']
        ns = set([k.split('.', 1)[0] for k in all if '.' in k])
        have = set()

        def do_all(ops, ns, have=have, r=r):
            r += ['## Namespace %s' % ns]
            for op in sorted(ops):
                have.add(op)
                r += ['### %s' % op]
                links = set(all[op])
                r += [' '.join(sorted(links))]

        for n in sorted(ns):
            nd = n + '.'
            ops = [op for op in all if op.startswith(nd)]
            do_all(ops, ns=n)
        ops = [op for op in all if not op in have]
        do_all(ops, ns='project/misc')

        r = '\n'.join(r)
        write_file(fn, r)
        S.stats.count_ops = len(have)
        app.info('Have written reference page', fn=fn)

    def make_all_ops_page(page):
        """This scans the FUNCS"""

        T = markdown.Mkdocs
        from operators import list_ops

        spec = list_ops()
        S.stats.count_operators = len(spec)
        r, ns = [], ''
        for k, v in sorted(spec.items()):
            n = k.split('.', 1)[0]
            if n != ns:
                ns = n
                r.append('## Namespace **`%s`**' % ns)
            r.append('##### ' + k)
            n = v['doc'].split('\n', 1)[0]
            c = T.py % v['source']
            exmpl = S.operators.get(k)
            if exmpl:
                n += ' (%s)' % len(exmpl)
                exmpl = ' '.join(exmpl)
                exmpl = exmpl.replace('(../', '(../../autodocs/')
                c = c + '\n' + exmpl

            r.append(T.admon(n, c, 'dev'))

        app.info('writing', page=page)
        write_file(page, '\n'.join(r))


def find_heading(fn):
    head = ''
    with open(fn) as fd:
        h = next(fd)
        if h.startswith('#'):
            return h.split('# ', 1)[1].strip().split('`', 1)[0]


def add_to_mkdocs_yml(pages, sep='# :autodocs:', md_dir=None):
    """Modifying mkdocs.yml, inserting pages refs within insertation markers (sep)"""
    fnm = S.d_root + '/mkdocs.yml'
    s = read_file(fnm).split(sep)
    if not len(s) == 3:
        return app.warn(
            'no autodoc seps in mkdocs',
            seperator=sep,
            hint='thats ok if you reference your pages manually - otherwise include 2 seperators',
        )
    if pages == 'check':
        return True

    pre, ad, post = s
    indent = ' ' * len(pre.rsplit('\n', 1)[-1])

    def entry(p, md_dir=md_dir):
        if md_dir:
            fn = md_dir + '/' + p
        fn = p.split(S.d_root + '/docs/', 1)[1]
        try:
            title = find_heading(p)
        except Exception as ex:
            title = ''
        if not title:
            l = fn.rsplit('/', 1)[-1].split('.')
            title = humanize(l[-2])
        return '"%s": %s' % (title, fn)

    pages = '\n'.join([indent + '- ' + entry(p) for p in pages])
    s = pre + sep + '\n' + pages + '\n' + indent + sep + post
    write_file(fnm, s)
    app.warn('have changed mkdocs config', fn=fnm)


def link_autogened_mds_over(frm, to):
    """Clearing destination dir, then creating a symlink from the source
    (which resides usually in the build dir) over to docs.
    This allows to build the docs w/o the sources spamming the repo (build dir is git ignored).
    """
    d = frm
    if not exists(d):
        os.makedirs(d)
        write_file(d + '/index.md', '!!! error "No autodocs created"')
        return app.error(
            'No pytest results', hint='run pytest with $pytest_auto_doc=true'
        )
    os.system('/bin/rm -f "%s"' % to)
    do(system, 'ln -s "%s" "%s"' % (d, to))
    app.info('linked pytest results', frm=d, to=to)


# def make_release_announce_header(file):
#     if not exists(file):
#         return app.warn('No template file found', file=file)
#     s = read_file(file)
#     tag = os.popen('git describe --tags --abbrev=0').read().strip()
#     pre, post = s.split('<b>', 1)
#     post = post.split('</b>', 1)[1]
#     s = pre + '<b>%s</b>' % tag + post
#     write_file(file, s)
#     app.info('Written', file=file)

d_assets_mkdocs_theme = '/assets/mkdocs/lcd'

d_assets = lambda: dirname(dirname(dirname(__file__))) + '/assets'


def add_theme_link():
    to = S.d_root + '/docs/lcd'
    if exists(to):
        return app.info('theme exists', location=to)
    import lcdoc

    f = dirname(lcdoc.__file__)
    f += d_assets_mkdocs_theme
    do(system, 'ln -s "%s" "%s"' % (f, to))
    if not exists(to):
        app.die('link creation failed', frm=f, to=to)
    app.warn('mkdocs add. themes enabled via link', frm=f, to=to)


import importlib, inspect


def is_func(obj, fn, src):
    f = getattr(obj, fn)
    if not ('def %s(' % fn in src and not '%s = ' % fn in src):
        return
    try:
        return type(f).__name__ == 'function'
    except:
        return


def is_cls(obj, cn, src):
    if not 'class %s' % cn in src:
        return
    c = getattr(obj, cn)
    try:
        return isinstance(c, type)
    except:
        return


class ModDocs:
    """
    Generates Markdown Files from given modules.

    Right now this is considered not much of a benefit compared to browsing the source
    in an editor.

    But we plan to deliver more information generated while running, comparable to the flows
    when documenting tests.


    """

    def mkdoc(res, hir=0):
        # if res['title'] == 'ModDocs':
        #     breakpoint()  # FIXME BREAKPOINT
        T = markdown.Mkdocs
        source = lambda src: T.details % ('Source code', T.py % src)
        r = ['#' * (hir + 1) + ' ' + res['title']]
        r += [deindent(res['doc'] or '')]
        r += [source(res['source'])]
        for k in 'classes', 'funcs':
            objs = res.get(k)
            if not objs:
                continue
            r += ['#' * (hir + 2) + ' ' + k.capitalize()]
            for c in res[k]:
                r.append(ModDocs.mkdoc(c, hir=hir + 2))
        return '\n'.join(r)

    def recurse_into(obj):
        g = getattr
        src = inspect.getsource(obj)
        res = {'doc': obj.__doc__, 'title': obj.__name__, 'source': src}
        for n, f in ['classes', is_cls], ['funcs', is_func]:
            objs = [
                g(obj, k) for k in dir(obj) if not k.startswith('_') and f(obj, k, src)
            ]
            res[n] = [ModDocs.recurse_into(c) for c in objs]
        return res

    def gen_mod_doc(mod):
        """Create the documentation for a single module"""
        if '/' in mod:
            app.die('Supply modules to autodoc in importable form (dotted)', fn=mod)
        try:
            mod = importlib.import_module(mod)
        except Exception as ex:
            app.die('could not import module', exc=ex, mod=mod)
        res = ModDocs.recurse_into(mod)
        md = ModDocs.mkdoc(res)
        return md

    def gen_mods_docs(modules):
        """Create the documentation for given modules"""
        l = {mod: do(ModDocs.gen_mod_doc, mod=mod) for mod in modules}
        d = S.d_root + '/build/automoddocs/'
        os.makedirs(d, exist_ok=True)

        fns = []
        for m, md in sorted(l.items()):
            fn = d + '%s.md' % m
            write_file(fn, md)
            # fn = fn.split(d, 1)[1]
            fns.append(fn.replace('/build/', '/docs/'))
        ddocs = S.d_root + '/docs/automoddocs'
        do(link_autogened_mds_over, frm=d, to=ddocs)
        do(add_to_mkdocs_yml, pages=fns, sep='# :automoddocs:', md_dir=ddocs)


def gen_change_log():
    dr, d = S.d_root, dirname
    cmd = 'cd "%s"; git-changelog -t "path:%s" . > CHANGELOG.md'
    dcl = d_assets() + '/mkdocs/lcd/src/md/keepachangelog'
    cmd = cmd % (dr, dcl)
    err = os.system(cmd)
    if err:
        app.die('changelog creation failed', fn=dcl, cmd=cmd)
    mark_auto_created('CHANGELOG.md')
    app.info('changelog created')


def dev_versions_warning():
    r = ''
    if not FLG.gen_dev_version_warning:
        return r
    apo = '```'
    nu = '- [%(name)s](%(url)s)'
    for k in os.environ.get('PYTHONPATH', '').split(':'):
        ver = gitcmd(k, cmd='git log -n 2')
        if ver:
            l = '\n'.join(['', nu % ver, apo, '%(cmd)s' % ver, apo, ''])
            r += l.replace('\n', '\n    ')

    if not r:
        return ''
    msg = '??? warning "Documentation was built with development versions of libs!"'
    return '\n'.join(['', '', msg, r, '', ''])


def gen_modify_date():
    last_modified = '\n\nLast modified: '
    sep = '\n<!-- pre_proc_marker -->\n'

    fn = S.d_root + '/README.md'
    r = read_file(fn)
    l = r.split(sep)
    if len(l) < 2:
        write_file(fn, r + sep + '\n\n')
        return gen_modify_date()
    r = (
        l[0]
        + sep
        + '\n\n----\n'
        + do(dev_versions_warning)
        + last_modified
        + time.ctime()
    )
    write_file(fn, r)


import toml


def add_pyproject_infos_to_mkdocs():
    # TODO
    raise Exception('TODO: Convert to pdm!')
    fnm = S.d_root + '/mkdocs.yml'
    m = read_file(fnm)
    p = S.d_root + '/pyproject.toml'
    p = toml.load(S.d_root + '/pyproject.toml')['tool']['poetry']

    def into(m, k, w):
        app.warn('Setting', key=k, value=w)
        if w:
            parts = m.split('\n%s: ' % k, 1)
            return parts[0] + '\n%s: ' % k + '"%s"\n' % w + parts[1].split('\n', 1)[1]
        app.warn('Cannot set key - not defined in pyproject', key=k)
        return m

    m = into(m, 'site_url', p.get('homepage'))
    m = into(m, 'repo_url', p.get('repository'))
    app.info('Have written', file=fnm)
    write_file(fnm, m)


from lcdoc import lp as lit_prog

import traceback

from ast import literal_eval


class LP:
    """literate programming feature"""

    PH = lambda nr: 'LP_PH: %s.' % nr
    # fn_lp = lambda fn: fn.rsplit('.md', 1)[0] + '.lp.md'
    fn_lp = lambda fn: fn.rsplit('.lp', 1)[0]

    # fmt:off
    texc             = '!!! error "LP exception"'
    py_err           = 'Python args parse error'
    err_admon        = 'LP error'
    interrupted      = 'LP continuation stopped by user'
    easy_args_err    = 'Easy args parse error'
    header_parse_err = 'Header_parse_error'
    # fmt:on

    def exception(cmd, exc, tb, kw):
        c = markdown.Mkdocs.py % {'cmd': cmd, 'kw': kw, 'trb': str(tb)}
        app.error('LP evaluation error', exc=exc)
        if not S.lp_on_err_keep_running:
            app.die(LP.err_admon, cmd=cmd, lp_file=S.cur_fn_lp, exc=exc, **kw)
        return markdown.Mkdocs.admon(LP.err_admon + ': %s' % str(exc), c, 'error')

    run_file = lambda fn_lp: LP.run_md(read_file(fn_lp), fn_lp, write=True)

    def run_md(md, fn_lp, write=False):
        """fn_lp required for filenames of async lp results"""
        S.cur_fn_lp = fn_lp
        lp_blocks, dest = do(LP.extract_lp_blocks, md=md, fn_lp=fn_lp)
        app.info('---------- %s --------------' % fn_lp)
        app.info('Found lit prog stanzas', count=len(lp_blocks))
        res = []
        # the doc file:
        fnd = LP.fn_lp(fn_lp)
        [res.append(LP.run_block(block, fnd)) for block in lp_blocks]
        md = '\n'.join(dest)
        for nr in range(len(res)):
            md = md.replace(LP.PH(nr), res[nr])
        if FLG.lit_prog_debug_matching_blocks:
            fnd = project.root() + '/tmp/lp_debug.md'
        if write:
            write_file(fnd, md)
        if FLG.lit_prog_debug_matching_blocks:
            print('<! ------- Start Debug Matching Blocks Output ------------------->')
            os.system('cat "%s"' % fnd)
            print('<! -------- End Debug Matching Blocks Output -------------------->')
            print('(Evaluated LP Blocks: %s)\n\n' % len(lp_blocks))
        return md

    def run_block(block, fnd):
        cmd, kw = '', ''
        try:
            args, kw = block['args'], block['kwargs']
            if args == LP.header_parse_err:
                raise Exception(
                    '%s %s %s. Failed header: "%s"'
                    % (args, kw[LP.py_err], kw[LP.easy_args_err], kw['header'])
                )
            # filter comments:
            cmd = '\n'.join([l for l in block['code'] if not l.startswith('# ')])
            if (cmd.strip() + ' ')[0] in ('[', '{'):
                try:
                    cmd = literal_eval(cmd)
                except:
                    cmd = json.loads(cmd)
            # cmd = block['code']
            kw['lang'] = block.get('lang')
            S.lp_stepmode and LP.confirm('Before running', page=fnd, cmd=cmd, **kw)
            run_lp = partial(lit_prog.run, fn_doc=fnd)
            kw['timeout'] = kw.get('timeout', S.lp_evaluation_timeout)
            S.stats.count_lp_blocks += 1
            res = run_lp(cmd, *args, **kw)
        except Exception as e:

            if not S.lp_on_err_keep_running:
                app.die('Could not eval', exc=e)
            if LP.interrupted in str(e):
                app.die('Unconfirmed')
            tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            res = LP.exception(cmd, e, tb, kw=kw)
        S.lp_stepmode and LP.confirm(
            'After running', page=fnd, cmd=cmd, json=res.splitlines()
        )
        ind = block.get('indent')
        if ind:
            res = ('\n' + res).replace('\n', '\n' + ind)
        return res

    def confirm(msg, page, cmd, **kw):
        if not sys.stdin.isatty():
            app.die('Must have stdin in interactive mode')
        app.info(msg, page=page, cmd=cmd, **kw)
        print('b=break to enter a pdb debugging session')
        print('c=continue to continue non-interactively')
        i = input('Continue [Y|n/q|b|c]? ').lower()
        if i in ('n', 'q'):
            app.die(LP.interrupted)
        if i == 'c':
            app.info('Continuing without break')
            FLG.lit_prog_evaluation_step_mode = False
            return
        if i == 'b':
            print('Entering pdb...')
            return breakpoint()

    def extract_header_args(lp_header, fn_lp):
        H = ' '.join(lp_header.split()[2:])
        header_kws = LP.header_kws(fn_lp)

        try:
            return (), parse_kw_str(H, header_kws, try_json=False)
        except Exception as ex:
            ex1 = ex
            try:
                return eval('get_args(%s)' % H, header_kws, {})
            except Exception as ex:
                ex2 = ex
        return LP.header_parse_err, {LP.py_err: ex2, LP.easy_args_err: ex1, 'header': H}

    get_args = lambda *a, **kw: [a, kw]  # trick to get python sig args

    def header_kws(fn_lp):
        """constants you can use in headers"""
        return {
            'get_args': LP.get_args,
            'dir_repo': fn_lp.split('/docs/', 1)[0],
            'dir_project': project.root(),
        }

    def extract_lp_blocks(md, fn_lp):
        s = md.splitlines()

        lps = []
        end = '```'
        lpnr = -1
        dest = []

        def pop(s, add=True):
            line = s.pop(0)
            dest.append(line) if add else 0
            return line

        while s:
            line = pop(s)
            ls = line.lstrip()
            if not ls.startswith('```'):
                continue
            # code. Normal or lp
            ind = ' ' * (len(line) - len(ls))
            fragm = (ls + '  ').split(' ', 2)
            # normal code?
            add = not fragm[1] == 'lp'
            n = []
            while True and s:
                n.append(pop(s, add))
                # within code a "```xxx" is not a closer, must be clean
                if n[-1].startswith(ind + '```') and n[-1].strip() == '```':
                    break
            if add:
                continue
            lpnr += 1
            lp_header = dest.pop(-1)
            dest.append(LP.PH(lpnr))  # placeholder
            n = [l[len(ind) :] for l in n[:-1]]
            l = fragm[0].split('```', 1)[1].strip()
            if not FLG.lit_prog_debug_matching_blocks in lp_header:
                continue
            a, kw = LP.extract_header_args(lp_header, fn_lp)
            spec = {
                'nr': lpnr,
                'code': n,
                'lang': l,
                'args': a,
                'kwargs': kw,
                'indent': ind,
            }

            lps.append(spec)
        return lps, dest

    def is_lp(d, fn, match=''):
        # and fm in fn
        # and not fn.endswith('.lp.md')Arbeitsweise
        # and LP.fn_lp(fn) in mkdocs
        if S.lp_evaluation_skip_existing and exists(fn.rsplit('.lp', 1)[0]):
            return
        return fn.endswith('.md.lp') and match in (d + '/' + fn)

    def verify_no_errors(files):
        errs = []
        for f in files:
            fn = f.rsplit('.lp', 1)[0]
            if not exists(fn):
                errs.append(['lp result file missing', fn, []])
            s = read_file(fn)
            e = LP.err_admon
            if e in read_file(fn):
                errs.append(['lp errors', fn, [i for i in s.splitlines() if e in i]])
        return errs

    def gen_evaluation(file_match):
        """Runs in a loop when monitor is set"""
        docs = project.root() + '/docs'
        # just in case he wants only lp without any project mkdocs = read_file(docs + '/../mkdocs.yml')
        os.makedirs(project.root() + '/tmp/tmux', exist_ok=True)
        files = walk_dir(docs, crit=partial(LP.is_lp, match=file_match))
        do_files = []
        for fn in files:
            t = os.stat(fn)[8]
            if t == S.lp_files.get(fn):
                continue
            do_files.append(fn)
            S.lp_files[fn] = t
        if do_files:
            app.debug('Re-evaluating lp files', files=do_files, of=files)
        [do(LP.run_file, fn_lp=fn) for fn in do_files]
        return do_files


# ------------------------------------------------------------------------- end actions
def run():
    """Entry point after flags parsing"""
    t0 = now()
    S.d_root = project.root()
    S.proj_config = project.load_config()
    if FLG.lit_prog_evaluation_monitor:
        FLG.lit_prog_on_err_keep_running = True
    # no flags in the lp code (usable from outside devapp or tests w/o init)
    S.lp_stepmode = FLG.lit_prog_evaluation_step_mode
    S.lp_on_err_keep_running = FLG.lit_prog_on_err_keep_running
    S.lp_evaluation_timeout = FLG.lit_prog_evaluation_timeout
    S.lp_evaluation_skip_existing = FLG.lit_prog_skip_existing
    lp = FLG.lit_prog_evaluation
    if lp:
        while True:
            files = LP.gen_evaluation(file_match=lp)
            if not FLG.lit_prog_evaluation_monitor:
                break
            time.sleep(0.4)
        errs = do(LP.verify_no_errors, files=files)
        if errs:
            app.die('LP errors', json=errs)

    if FLG.gen_theme_link:
        do(add_theme_link, track=1)
    if FLG.gen_change_log:
        do(gen_change_log, track=1)
    if FLG.gen_last_modify_date:
        do(gen_modify_date, track=1)

    # page = FLG.release_announce_html
    # if page:
    #    do(make_release_announce_header, file=page)
    d = FLG.gen_mod_docs
    if d:
        do(ModDocs.gen_mods_docs, modules=d, track=1)

    d = FLG.gen_auto_docs
    if d:
        do(add_to_mkdocs_yml, pages='check', track=1)
        d = S.d_root + '/build/autodocs'
        do(link_autogened_mds_over, frm=d, to=d_autodocs())
        do(SVGs.create_if_present)
        do(Refs.create_if_present)
        do(Refs.make_examples_refs_page_if_operators_present)
        pages = sorted(scan_d_autodocs('.md'))
        do(add_to_mkdocs_yml, pages=pages)

    if FLG.add_pyproject_infos_to_mkdocs:
        do(add_pyproject_infos_to_mkdocs)

    cp = FLG.gen_credits_page
    if cp:
        do(Credits.create_credits_page, page='CREDITS.md', track=1)
    # page = FLG.ops_ref_page
    # if page:
    #    do(Refs.make_all_ops_page, page=page)
    S.stats.total_time = now() - t0
    app.info('Have run', json=sorted(list(S.actions)))
    app.info('stats', json=stats())


main = partial(run_app, run, flags=Flags)
