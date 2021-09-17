"""
## Literate Programming

[org babel](https://orgmode.org/worg/org-contrib/babel/intro.html) inspired dyanamic code evaluation plugin.

```bash
 ```<bash|python> lp <header args> 
 echo "Hello World"
 ```
```

Details see [here](../features/lp/)

"""
import contextlib
import hashlib
import json
import traceback
from ast import literal_eval
from functools import partial
from pprint import pformat

import coverage

from lcdoc import lp as lit_prog
from lcdoc.mkdocs import markdown
from lcdoc.mkdocs.tools import (
    MDPlugin,
    app,
    config_options,
    link_assets,
    now,
    split_off_fenced_blocks,
)
from lcdoc.tools import dirname, exists, os, project, read_file, sys, write_file

md5 = lambda s: hashlib.md5(bytes(s, 'utf-8')).hexdigest()


def add_assets_to_page(page, d):
    """
    d like {'md': {'mermaid': ..., 'header': {'chartist': ...}, 'footer': ...}
    """
    m = getattr(page, 'lp_page_assets', None)
    if not m:
        m = page.lp_page_assets = {'header': {}, 'footer': {}, 'md': {}}
    # lp_page_assets_md lp_page_assets_header lp_page_assets_footer
    for mode, v in d.items():
        for k1, v1 in v.items():
            try:
                m[k1][mode] = v1
            except Exception as ex:
                print('breakpoint set')
                breakpoint()
                keep_ctx = True


# :docs:hashed_headers
# those header params will prevent to use caching when changed, they go into the hash of
# a block which is the cache key:
hashed_headers = [
    'asserts',
    'chmod',
    'cwd',
    'delim',
    'dir',
    'expect',
    'mode',
    'new_session',
    'pdb',
    'post',
    'pre',
    'session',
    'timeout',
]
# :docs:hashed_headers

lp_res_ext = '.res.py'  # when opened the ide will format

env_args = {}

# :docs:eval_parameter_values
class Eval:
    never = 'never'  # not even when not cached
    always = 'always'  # even when cached. except skipped
    on_change = 'on_change'  # only when block changed
    on_page_change = 'on_page_change'  # whan any block (md irrelevant) on page changed
    # Default: anything else would confuse user. e.g. cat <filename> would show old still when it changed but no lp change involved:
    default = 'always'


# :docs:eval_parameter_values


eval_modes = {k for k in dir(Eval) if not k[0] == '_'}

int_env_vars = ['DOCU', 'DOCU_FILE']


class LP:
    lpnr = 0
    blocks_on_page = None
    page = None  # current page
    config = None  # the mkdocs config
    config_lp_plugin = None  # the mkdocs lp plugin config
    page_initted = False
    dflt_evaluation_timeout = 5
    on_err_keep_running = False
    previous_results = None
    cur_results = None
    break_on_err = False
    fn_lp = None
    cov = None  # current coverage context
    create_coverage_backrefs = False
    docs_repo_base = ''  # e.g. 'https://github.com/AXGKl/docutools/docs'
    # fmt:off
    texc             = '!!! error "LP exception"'
    py_err           = 'Python args parse error'
    err_admon        = 'LP error'
    interrupted      = 'LP continuation stopped by user'
    easy_args_err    = 'Easy args parse error'
    header_parse_err = 'Header_parse_error'
    # page global args. base from env. settable via ```page lp foo=bar
    dflt_args = None
    # fmt:on

    def init_page():
        """run only at first fc block found"""
        LP.lpnr = 0
        LP.blocks_on_page = []
        LP.page_initted = True
        LP.spec_by_id = {}
        LP.stats = s = LP.page.stats
        LP.dflt_args = dict(env_args)
        LP.previous_results_missing = []
        s['blocks_total'] = 0
        s['blocks_page'] = 0
        s['blocks_evaled'] = 0
        s['blocks_cached'] = 0
        s['blocks_skipped_prev_result'] = 0
        s['blocks_skipped_no_result'] = 0
        s['blocks_max_time'] = 0
        s['blocks_longer_2_sec'] = 0
        s['blocks_longer_10_sec'] = 0
        LP.set_page_env_vars()

    def set_page_env_vars():
        # useable in evaluated blocks:
        os.environ['LP_DOCU_FILE'] = LP.fn_lp or 'init'
        os.environ['LP_DOCU_DIR'] = dirname(LP.fn_lp or 'init')
        os.environ['LP_DOCU_ROOT'] = LP.config['docs_dir']
        os.environ['LP_PROJECT_ROOT'] = project.root(LP.config)

    def configure_from_env():
        """run at startup (on_configure hook)"""
        s = {'LP_', 'lp_'}
        LP.set_page_env_vars()
        env_vars = [(f[3:], os.environ[f]) for f in os.environ if f[:3] in s]
        for k, v in env_vars:
            v = lit_prog.cast(v)
            app.debug('From environ', key=k, value=v)
            env_args[k] = v
        LP.stats['LP_env_vars'] = len(env_args)

    def is_lp_block(header_line):
        l = header_line.split(' ', 2)
        return len(l) > 1 and (l[1] == 'lp' or l[1].startswith('lp:'))

    def parse_lp_block(lines):
        """
        Done for ALL LP blocks on the page, BEFORE the first block is evaluated!

        {'args': (),
         'code': ['echo "Hello World!"'],
         'fn': '/home/gk/repos/docutools/docs/features/literate_programming.md.lp',
         'indent': '',
         'kwargs': {'addsrc': 1,
                    'asserts': 'Hello',
                    'fmt': 'xt_flat',
                    'session': 'foo'},
         'lang': 'bash',
         'nr': 0,
         'source': '```bash lp addsrc=1 asserts=Hello fmt=xt_flat session=foo\n'
                   'echo "Hello World!"\n'
                   '```',
         'source_id': 'f688f2633ae97209c5c0a5a0fdb93384'}
        """
        if not LP.page_initted:
            LP.init_page()
        h = lines[0].rstrip()
        src_header = h.lstrip()
        lang = src_header.split('```', 1)[1].split(' ', 1)[0]
        ind = len(h) - len(src_header)
        # for the hash we take the undindent version, i.e. we allow to shift it in /
        # out and still take result from cache:
        source = [l[ind:] for l in lines]
        code = source[1:-1]
        source = '\n'.join(source)
        # if "rm foobar" in source: breakpoint()  # FIXME BREAKPOINT
        a, kw = LP.extract_header_args(src_header)
        # support "bash lp:mermaid" ident to "bash lp mode=mermaid":
        if not 'mode' in kw:
            l = src_header.split(' ', 2)
            l = (l[1] + ':').split(':', 2)
            if l[1]:
                kw['mode'] = l[1]
        # these header args may change eval result, need to go into the hash:
        hashed = ','.join(['%s:%s' % (k, kw.get(k)) for k in hashed_headers if kw.get(k)])
        hashed += '\n'.join(code)
        sid = md5(hashed)
        reg = LP.spec_by_id
        # if lang == 'page': breakpoint()  # FIXME BREAKPOINT
        # eval result of same block could change, sideeffects in other evals in between:
        while sid in reg:
            sid += '_'
        # if 'Alice' in str(code): breakpoint()  # FIXME BREAKPOINT
        spec = {
            'nr': LP.lpnr,
            'code': code,
            'lang': lang,
            'args': a,
            'kwargs': kw,
            'indent': ind * ' ',
            'source': source,
            'source_id': sid,
            'fn': LP.fn_lp,
        }
        LP.lpnr += 1
        reg[sid] = spec
        return spec

    def extract_header_args(lp_header):
        H = ' '.join(lp_header.split()[2:])
        r = project.root()
        presets = {'dir_repo': r, 'dir_project': r}  # dir_repo: an alias
        err, res = lit_prog.parse_header_args(H, fn_lp=LP.fn_lp, **presets)
        if not err:
            return res

        return (
            LP.header_parse_err,
            {LP.py_err: res[0], LP.easy_args_err: res[1], 'header': H},
        )

    fn_previous_results = lambda: LP.fn_lp + lp_res_ext  # when opened the ide will format

    def load_previous_results():
        LP.cur_results = {}
        # If no change we don't write it, so
        # mkdocs wont rebuild (i.e. prevent looping on serve)
        fn = LP.fn_previous_results()
        r = read_file(fn, dflt='{}')
        try:
            r = literal_eval(r)
            app.debug('Loaded previous results', lp_blocks=len(r))
        except Exception as ex:
            msg = 'Err eval previous result'
            app.warning(msg, exc=ex, content_start=r[:100], fn=fn)
            r = {}
        LP.previous_results = r
        missing = [id for id in LP.spec_by_id if not id in r]
        if not missing:
            return app.debug('All eval results found in previous run')
        LP.previous_results_missing = missing
        missing = [LP.spec_by_id[id]['source'] for id in missing]
        app.info('New lp blocks', json=missing)

    def handle_skips(blocks):
        """
        Skips are never evaluated, even when missing.

        Returning true when there are skips - telling LP that we need to check the
        .md for old results
        """
        skip_tags = ['skip_this', 'skip_other', 'skip_below', 'skip_above']

        def check_skip_syntax(b, h=skip_tags):
            l = [k for k in b['kwargs'].keys() if k.startswith('skip_')]
            n = [k for k in l if not k in h]
            if n:
                app.die('Not understood skip statment', unknown=n, allowed=h)

        def skip(b):
            b['kwargs']['skip_this'] = True

        for b in blocks:
            check_skip_syntax(b)
            if b['kwargs'].get('skip_other'):
                for c in blocks:
                    skip(c)
                b['kwargs'].pop('skip_this')
                return True
            if b['kwargs'].get('skip_below'):
                s = False
                for c in blocks:
                    if c == b:
                        s = True
                        continue
                    if s:
                        skip(c)
                return True

            if b['kwargs'].get('skip_above'):
                for c in blocks:
                    if c == b:
                        return True
                    skip(c)

            if b['kwargs'].get('skip_this'):
                return True

    def run_blocks(lp_blocks, raise_on_errs=None):
        LP.blocks_on_page = lp_blocks  # mermaid needs to know if its the last one
        LP.stats['blocks_total'] += len(lp_blocks)
        have_skips = LP.handle_skips(lp_blocks)
        res = []
        [res.append(LP.run_block(block)) for block in lp_blocks]
        return res

    def run_block(spec):
        """
        fnd: '/home/gk/repos/blog/docs/ll/vim/vim.md'
        block.keys: ['nr', 'code', 'lang', 'args', 'kwargs', 'indent', 'source', 'source_id', 'fn']
        """
        # if 'show_src' in str(spec): breakpoint()  # FIXME BREAKPOINT
        kw = spec['kwargs']
        sid = spec['source_id']
        # handle page level parametrization already here - this is never skipped:
        # we allow change of default args mid-page:
        is_page = False
        if spec['lang'] == 'page':
            # if 'param' in LP.fn_lp: breakpoint()  # FIXME BREAKPOINT
            is_page = True
            LP.stats['blocks_page'] += 1
            m = {k: v for k, v in kw.items() if not k.startswith('skip_')}
            LP.dflt_args.update(m)
            kw['silent'] = True
            kw['lang'] = 'bash'
            kw['addsrc'] = False

        lp_runner = partial(lit_prog.run, fn_doc=LP.fn_lp)

        # set the default args, they might be updated from page level params:
        # if 'param' in LP.fn_lp: breakpoint()  # FIXME BREAKPOINT
        m = dict(LP.dflt_args)
        m.update(kw)
        kw = spec['kwargs'] = m
        # those kw will parametrize lp.py:run -> add more infos about the spec:
        # some plugins may need that, why not:
        kw['LP'] = LP
        kw['lang'] = spec.get('lang')
        kw['sourceblock'] = spec.get('source')
        LP.spec = spec

        # When ANY block changed, we re-eval all, except those skipped:
        # This is usually when editing a page, user may change md but as soon as he
        # changes lp source we re-eval the whole page. If critical user has to use skips:
        any_change = LP.previous_results_missing
        # is THIS one missing?
        prev_res = LP.previous_results.get(sid)

        def skip(b, kw=kw):
            kw['skip_this'] = True if b else kw.get('skip_this', False)

        evl_policy = kw.get('eval', Eval.default)
        # block level eval set?:
        if ':' in evl_policy:
            if not evl_policy.split(':', 1)[1] in spec['source']:
                app.warning('Skipping block, not eval match', eval=evl_policy)
                skip(True)
            else:
                skip(False)
        elif is_page:
            skip(False)
        elif evl_policy == Eval.never:
            skip(True)
        elif evl_policy == Eval.on_change:
            if prev_res:
                skip(True)
            else:
                skip(False)
        elif evl_policy == Eval.on_page_change:
            if any_change:
                skip(False)
            elif not prev_res:
                skip(False)
            else:
                # no change on page, have prev_res:
                skip(True)
        elif evl_policy == Eval.on_change:
            skip(bool(prev_res))
        page_assets = None
        if kw.get('skip_this'):
            # if "lessinger" in str(spec["source"]): breakpoint()  # FIXME BREAKPOINT
            if prev_res:
                LP.stats['blocks_skipped_prev_result'] += 1
                LP.cur_results[sid] = prev_res  # no adding of skipped indicators to res
                res = lp_runner(spec, use_prev_res=prev_res, **kw)
                try:
                    page_assets = res['raw']['page_assets']
                except:
                    pass
                res = res['formatted']
                res = mark_as_previous_result(res)
            else:
                LP.stats['blocks_skipped_no_result'] += 1
                res = skipped(spec)
        else:
            LP.stats['blocks_evaled'] += 1
            ret = LP.eval_block(spec, lp_runner=lp_runner)
            LP.cur_results[sid] = r = ret['raw']
            if isinstance(r, dict) and 'page_assets' in r:
                page_assets = r.get('page_assets')
            res = ret['formatted']
        if page_assets:
            add_assets_to_page(LP.page, page_assets)
        ind = spec.get('indent')
        if ind:
            res = ('\n' + res).replace('\n', '\n' + ind)
        return res

    def eval_block(spec, lp_runner):
        fn_lp = LP.fn_lp
        if LP.cov:
            # h = ':%s:%s' % (spec['nr'], spec['source'].split('\n', 1)[0][3:])
            f = LP.page.file.src_path
            if not LP.create_coverage_backrefs:
                h = f
            else:
                s = LP.docs_repo_base + '/' + f
                l = spec.get('linenr', 1)
                # plain is for gh, otherwise they render. should not hurt elsewhere
                h = '<a href="%s?plain=1#%s">%s</a>' % (s, l, f)
            LP.cov.switch_context(h)

        sid = spec['source_id']
        cmd, kw = '', ''
        try:
            args, kw = spec['args'], spec['kwargs']
            if args == LP.header_parse_err:
                raise Exception(
                    '%s %s %s. Failed header: "%s"'
                    % (args, kw[LP.py_err], kw[LP.easy_args_err], kw['header'])
                )
            # filter comments:
            cmd = '\n'.join([l for l in spec['code']])  # if not l.startswith("# ")])
            j = cmd.strip()
            if j and (j[0] + j[-1]) in ('[]', '{}'):
                try:
                    cmd = literal_eval(cmd)
                except Exception as exle:
                    try:
                        cmd = json.loads(cmd)
                    except Exception as ex:
                        ex.args += ('LP: Expression to deserialize was: %s' % cmd,)
                        ex.args += (
                            'LP: Before json.loads we tried literal eval but got Exception: %s'
                            % exle,
                        )
                        raise
            # cmd = block['code']
            kw.get('pdb') and LP.confirm('Before running', page=fn_lp, cmd=cmd, **kw)
            kw['timeout'] = kw.get('timeout', LP.dflt_evaluation_timeout)
            stats = LP.stats
            id = '<!-- id: %s -->' % sid

            t0 = now()
            ret = lp_runner(cmd, *args, **kw)

            dt = now() - t0
            if dt > stats['blocks_max_time']:
                stats['blocks_max_time'] = round(dt, 3)
            if dt > 2:
                stats['blocks_longer_2_sec'] += 1
            if dt > 10:
                stats['blocks_longer_10_sec'] += 1

            ret['formatted'] = '%s%s\n%s' % (id, ret['formatted'], id)

            # inteded for the last block of a big e.g. cluster setup page:
            # sol = block['fn'] in LP.skipped_on_lock
            # if (kw.get('lock_page') and not kw.get('skip_this')) or sol:
            #     LP.write_lock_file(fnd)

        except Exception as e:
            if LP.interrupted in str(e):
                app.die('Unconfirmed')  # only generated by interactive dialog
            if not LP.on_err_keep_running:
                if LP.break_on_err and sys.stdin.isatty():
                    j = {'cmd': cmd, 'kw': kw, 'got err': e}
                    app.warning('Could not eval - step into?', json=j)
                    breakpoint()  # FEATURE! Do not reomve!
                    ret = {'raw': 'n.a.', 'formatted': lp_runner(cmd, *args, **kw)}
                else:
                    raise
            else:
                tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                ret = {'raw': 'n.a.', 'formatted': LP.exception(cmd, e, tb, kw=kw)}

        if kw.get('pdb'):
            _ = ret['formatted'].splitlines()
            LP.confirm('After running', page=fn_lp, cmd=cmd, json=_)
        return ret

    def exception(cmd, exc, tb, kw):
        c = markdown.Mkdocs.py % {'cmd': cmd, 'kw': kw, 'trb': str(tb)}
        app.error('LP evaluation error', exc=exc)
        if not LP.on_err_keep_running:
            app.die(LP.err_admon, cmd=cmd, lp_file=LP.fn_lp, exc=exc, **kw)
        return markdown.Mkdocs.admon(LP.err_admon + ': %s' % str(exc), c, 'error')

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
            LP.lit_prog_evaluation_step_mode = False
            return
        if i == 'b':
            print('Entering pdb...')
            return breakpoint()

    def write_eval_results():
        if LP.previous_results == LP.cur_results:
            return app.debug('No results change, skipping write')
        r = LP.cur_results
        rs = pformat(r)  # making diffs look better
        # we write the results as linesplitted list, so that the autoformatter can
        # nicely reformat a result file opened in an editor:
        write_file(LP.fn_previous_results(), rs)


def on_config_add_extra_css_and_js(plugin, config):
    """
        extra_css:
          - lp/css/xterm.min.css
          (..)
        extra_javascript:
          - lp/javascript/xterm.4.9.0.min.js
          - lp/javascript/xterm-addon-fit.min.js
          (...)
    """

    for da in 'css', 'javascript':
        i = 0
        d = plugin.d_assets + '/' + da
        l = config.setdefault('extra_' + da, [])
        for a in os.listdir(d):
            l.append('lcd/lp/%s/%s' % (da, a))
            i += 1
        app.debug('Added assets', typ=da, count=i, dir=d)


T_skipped = '''

SKIPPED:
```
%s
```

'''

skipped = lambda s: T_skipped % s


def mark_as_previous_result(s):
    return (
        '''
%s

<hr/>
    '''
        % s
    )


# :docs:patching_mkdocs
def patch_mkdocs_to_ignore_res_file_changes():
    """sad. we must prevent mkdocs serve to rebuild each time we write a result file
    And we want those result files close to the docs, they should be in that tree.
    """
    import mkdocs

    fn = mkdocs.__file__.rsplit('/', 1)[0]
    fn += '/livereload/__init__.py'

    if not exists(fn):
        return app.warning('Cannot patch mkdocs - version mismatch', missing=fn)

    s = read_file(fn)
    S = 'event.is_directory'
    if not S in s:
        return app.warning('Cannot patch mkdocs - version mismatch', missing=fn)
    k = "'%s'" % lp_res_ext
    if k in s:
        return app.info('mkdocs is already patched to ignore %s' % k, fn=fn)
    os.system('cp "%s" "%s.orig"' % (fn, fn))
    new = S + ' or event.src_path.endswith(%s)' % k
    s = s.replace(S, new)
    write_file(fn, s)
    diff = os.popen('diff "%s.orig" "%s"' % (fn, fn)).read().splitlines()
    app.info('Diff', json=diff)
    msg = 'Have patched mkdocs to not watch %s  files. Please restart.' % k
    app.die(msg, fn=fn)
    # :docs:patching_mkdocs


def make_plugin_docs(config):
    dd = config['docs_dir'] + '/features/lp/plugs'
    if not exists(dd):
        os.makedirs(dd, exist_ok=True)

    D = dirname(__file__) + '/plugs'
    c = []
    for k in sorted(os.listdir(D)):
        d = D + '/' + k
        fnr, fnp = d + '/README.md', d + '/__init__.py'
        if not exists(fnr) or not exists(fnp):
            continue
        t = dd + '/' + k + '.md'
        if not exists(t):
            f = '../../../../src/lcdoc/mkdocs/lp/plugs/%s/README.md' % k
            os.symlink(f, t)
            c.append([f, t])
    if c:
        app.info('Plugs doc symlink created', json=c)


# ------------------------------------------------------------------------------- Plugin
class LPPlugin(MDPlugin):
    config_scheme = (
        # when given we create those for coverage ctx, using repo_url:
        ('coverage_backrefs', config_options.Type(str, default='blob/master')),
    )

    def on_config(self, config):
        LP.cov = coverage.Coverage().current()  # None if we are not run in coverage
        cbr = self.config['coverage_backrefs']
        if cbr:
            _ = config['repo_url'] + cbr
            _ += config['docs_dir'].split(project.root(config), 1)[1]
            LP.create_coverage_backrefs = True
        LP.docs_repo_base = _  # e.g. 'https://github.com/AXGKl/docutools/docs'

        if 'serve' in sys.argv:
            patch_mkdocs_to_ignore_res_file_changes()
        make_plugin_docs(config)
        LP.config = config
        LP.stats = self.stats
        link_assets(self, __file__, config)
        on_config_add_extra_css_and_js(self, config)
        project.root(config)  # gets root dir from config and caches it
        LP.configure_from_env()

    def on_files(self, files, config):
        """remove all results files from on-change detection and copy over mechs"""
        lpres_files = [f for f in files if f.src_path.endswith(lp_res_ext)]
        [files.remove(f) for f in lpres_files]

    def on_page_markdown(self, markdown, page, config, files):
        eval = env_args.get('eval')
        if eval and eval not in eval_modes:
            # we need to be able to exactly match on docs/index.md
            # -> take all:
            p = page.file.abs_src_path
            # eval is page[:block match] if not in evals
            if not eval.split(':', 1)[0] in p:
                return app.debug('LP: Skipping ($LP_EVAL) %s' % p)
        LP.page = page
        LP.config_lp_plugin = self.config
        LP.page_initted = False
        LP.fn_lp = page.file.abs_src_path
        mds, lp_blocks = split_off_fenced_blocks(
            markdown, fc_crit=LP.is_lp_block, fc_process=LP.parse_lp_block
        )
        if not lp_blocks:
            fn = LP.fn_previous_results()
            return os.unlink(fn) if exists(fn) else None

        LP.load_previous_results()
        blocks = LP.run_blocks(lp_blocks)
        LP.write_eval_results()
        MD = ''
        for md in mds:
            MD += '\n'.join(md)
            if blocks:
                res = blocks.pop(0)
                MD += '\n' + res + '\n'

        pe = getattr(page, 'lp_page_assets', None)
        if pe:
            pe = pe.get('md', {})
            for k, v in pe.items():
                app.info('Page asset', adding='md', for_=k)
                MD += '\n\n' + v
        return MD

    def on_page_content(self, html, page, config, files):
        return incl_page_assets(page, html)

    def on_post_page(self, output, page, config):
        """this is intended for side effects outside the html content
        Note: at https://github.com/squidfunk/mkdocs-material/issues/2338 only inside
        container element is re-evalled at nav.instant events.
        """
        f = getattr(page, 'lp_on_post_page', ())
        [i() for i in f]


def incl_page_assets(page, html):
    PA, o = getattr(page, 'lp_page_assets', None), html
    if not PA:
        return o

    for w in ['header', 'footer']:
        pe = PA.get(w, {})
        if not pe:
            continue

        for k in sorted(pe):
            v = pe[k]
            app.info('Page asset', adding=w, for_=k)
            if isinstance(v, dict):
                r = ''
                for k1, v1 in v.items():
                    if k1 == 'stylesheet':
                        for v2 in to_list(v1):
                            if v2.endswith('.css'):
                                r += T_css_link % v2
                            else:
                                r += '\n<style>\n%s\n</style>\n' % v2
                    elif k1 == 'script':
                        for v2 in to_list(v1):
                            if v2.endswith('.js'):
                                r += T_js_url % v2
                            else:
                                r += '\n<script>\n%s\n</script>\n' % v2
                    else:
                        app.warning('Not supported', mode=k1, val=v1)
                v = r
            v = '\n\n' + v + '\n\n'
            o = (v + o) if w == 'header' else (o + v)
    return o


to_list = lambda s: s if isinstance(s, list) else [s]

T_css_link = '<link rel="stylesheet" href="%s" />'
T_js_url = '<script src="%s"></script>'
