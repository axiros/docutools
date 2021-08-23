from mkdocs.config import config_options
from ast import literal_eval
import json
from functools import partial
from lcdoc.mkdocs import markdown
from lcdoc.mkdocs.tools import MDPlugin, app, link_assets, split_off_fenced_blocks, now
from lcdoc.tools import dirname, os, project, sys
import traceback


def on_config_add_extra_css_and_js(plugin, config):
    """
        extra_css:
          - lp/css/xterm.min.css
          - lp/css/asciinema-player.css

        extra_javascript:
          - lp/javascript/tables.js
          - lp/javascript/tablesort.min.js
            # 4.9.0 -> TODO: rename
          - lp/javascript/Rx.min.js
          - lp/javascript/xterm.4.9.0.min.js
          - lp/javascript/xterm-addon-fit.min.js
          - lp/javascript/xterm-addon-search.min.js
          - lp/javascript/lc.js
          - lp/javascript/fa_all.js
          - lp/javascript/asciinema-player.js
    """

    for da in 'css', 'javascript':
        i = 0
        d = plugin.d_assets + '/' + da
        l = config.setdefault('extra_' + da, [])
        for a in os.listdir(d):
            l.append('lcd/lp/%s/%s' % (da, a))
            i += 1
        app.debug('Added assets', typ=da, count=i, dir=d)


from hashlib import md5
from lcdoc import lp as lit_prog


class LP:
    lpnr = 0
    page = None
    config = None
    page_initted = False
    ids_by_fn = None
    lp_evaluation_timeout = 5
    lp_stepmode = False
    lp_on_err_keep_running = False

    # fmt:off
    texc             = '!!! error "LP exception"'
    py_err           = 'Python args parse error'
    err_admon        = 'LP error'
    interrupted      = 'LP continuation stopped by user'
    easy_args_err    = 'Easy args parse error'
    header_parse_err = 'Header_parse_error'
    ids_by_fn        = {}
    page_level_headers = {}
    # fmt:on

    def init_page():
        LP.fn_lp = LP.page.file.abs_src_path
        LP.lpnr = 0
        LP.page_initted = True
        LP.hash_by_id = {}
        LP.stats = s = LP.page.stats
        s['blocks_total'] = 0
        s['blocks_evaled'] = 0
        s['blocks_max_time'] = 0
        s['blocks_longer_2_sec'] = 0
        s['blocks_longer_10_sec'] = 0

    def is_lp_block(header_line):
        l = header_line.split(' ', 2)
        return len(l) == 3 and l[1] == 'lp'

    def parse_lp_block(lines):
        """
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
        source = '\n'.join([l[ind:] for l in lines])
        # header goes into hash, could change eval result:
        id = md5(bytes(source, 'utf-8')).hexdigest()
        reg = LP.hash_by_id
        # eval result of same block could change, sideeffects in other evals in between:
        while id in reg:
            id += '_'
        a, kw = LP.extract_header_args(src_header)
        spec = {
            'nr': LP.lpnr,
            'code': lines[1:-1],
            'lang': lang,
            'args': a,
            'kwargs': kw,
            'indent': ind * ' ',
            'source': source,
            'source_id': id,
            'fn': LP.fn_lp,
        }
        LP.lpnr += 1
        reg[id] = spec
        return spec

    def extract_header_args(lp_header):
        H = ' '.join(lp_header.split()[2:])
        r = project.root(LP.config)
        err, res = lit_prog.parse_header_args(H, fn_lp=LP.fn_lp, dir_project=r)
        if not err:
            return res

        return (
            LP.header_parse_err,
            {LP.py_err: res[0], LP.easy_args_err: res[1], 'header': H},
        )

    def handle_skips(blocks):
        """Returning true when there are skips - telling LP that we need to check the
        .md for old results"""

        def check_skip_syntax(b):
            h = ['skip_this', 'skip_other', 'skip_below', 'skip_above']
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
        have_skips = LP.handle_skips(lp_blocks)
        res = []
        fnd = LP.fn_lp
        [
            res.append(LP.run_block(block, fnd, raise_on_errs=raise_on_errs))
            for block in lp_blocks
        ]
        return res

    def run_block(block, fnd, raise_on_errs=None):
        """
        fnd: '/home/gk/repos/blog/docs/ll/vim/vim.md'
        block.keys: ['nr', 'code', 'lang', 'args', 'kwargs', 'indent', 'source', 'source_id', 'fn']
        """
        if block['lang'] == 'page':
            m = {k: v for k, v in block['kwargs'].items() if not k.startswith('skip_')}
            LP.page_level_headers.update(m)
            return ''
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
            for k, v in LP.page_level_headers.items():
                if not k in kw:
                    kw[k] = v
            kw['lang'] = block.get('lang')
            kw['sourceblock'] = block.get('source')
            # S.lp_stepmode and LP.confirm('Before running', page=fnd, cmd=cmd, **kw)
            run_lp = partial(lit_prog.run, fn_doc=fnd)
            kw['timeout'] = kw.get('timeout', LP.lp_evaluation_timeout)
            stats = LP.stats
            stats['blocks_total'] += 1
            id = '<!-- id: %(source_id)s -->' % block
            res = None

            # if kw.get('skip_this'):
            #     m = LP.current_dest_md
            #     l = m.split(id)
            #     if len(l) == 3:
            #         res = l[1][:-1]
            #         S.stats.blocks_skipped_transferred_previous_res += 1
            #     else:
            #         S.stats.blocks_skipped_no_previous_res += 1

            if not res:
                if not kw.get('skip_this'):
                    stats['blocks_evaled'] += 1
                t0 = now()
                res = run_lp(cmd, *args, **kw)
                dt = now() - t0
                if dt > stats['blocks_max_time']:
                    stats['blocks_max_time'] = round(dt, 3)
                if dt > 2:
                    stats['blocks_longer_2_sec'] += 1
                if dt > 10:
                    stats['blocks_longer_10_sec'] += 1

            res = '%s%s\n%s' % (id, res, id)

            # inteded for the last block of a big e.g. cluster setup page:
            # sol = block['fn'] in LP.skipped_on_lock
            # if (kw.get('lock_page') and not kw.get('skip_this')) or sol:
            #     LP.write_lock_file(fnd)

        except Exception as e:
            # intended for pytesting lp itself:
            if raise_on_errs:
                raise
            if not LP.lp_on_err_keep_running:
                app.die('Could not eval', exc=e)
            if LP.interrupted in str(e):
                app.die('Unconfirmed')
            tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            res = LP.exception(cmd, e, tb, kw=kw)
        LP.lp_stepmode and LP.confirm(
            'After running', page=fnd, cmd=cmd, json=res.splitlines()
        )
        ind = block.get('indent')
        if ind:
            res = ('\n' + res).replace('\n', '\n' + ind)
        return res

    def exception(cmd, exc, tb, kw):
        c = markdown.Mkdocs.py % {'cmd': cmd, 'kw': kw, 'trb': str(tb)}
        app.error('LP evaluation error', exc=exc)
        if not LP.lp_on_err_keep_running:
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


import contextlib


class LPPlugin(MDPlugin):
    config_scheme = (('join_string', config_options.Type(str, default=' - ')),)

    def on_config(self, config):
        link_assets(self, __file__, config)
        on_config_add_extra_css_and_js(self, config)

    def on_page_markdown(self, markdown, page, config, files):
        LP.page = page
        LP.config = config
        LP.page_initted = False
        mds, lp_blocks = split_off_fenced_blocks(
            markdown, fc_crit=LP.is_lp_block, fc_process=LP.parse_lp_block
        )
        if not lp_blocks:
            return
        with contextlib.redirect_stdout(sys.stderr):
            blocks = LP.run_blocks(lp_blocks)

        MD = ''
        for md in mds:
            MD += '\n'.join(md)
            if blocks:
                res = blocks.pop(0)
                MD += '\n' + res + '\n'
        return MD
