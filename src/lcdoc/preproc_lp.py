#!/usr/bin/env python
"""
LP Preprocessor of Markdown

"""
import json
import os
import sys
import time
import traceback
from ast import literal_eval
from functools import partial
from hashlib import md5

from devapp.app import app
from devapp.app import do as app_do

# from operators.testing.auto_docs import dir_pytest_base
from devapp.tools import FLG, project, read_file, walk_dir, write_file
from theming.formatting import markdown

from lcdoc import lp as lit_prog


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

    class lit_prog_evaluation:
        n = 'Evaluate literal programming stanzas in all matching md.lp source files, '
        n += 'generating secondary .md files. Say md to match all.'
        d = ''

    class lit_prog_evaluation_step_mode:
        n = 'Pause before and after each evaluation block, waiting for user input'
        d = False

    class lit_prog_evaluation_monitor:
        'Sets lit_prog_on_err_keep_running to True'
        n = 'Enable the file monitor for re-eval runs of any matching changed .mp.lp file'
        d = False

    class lit_prog_skip_existing:
        """Intended for CI or to prevent unwanted re-evaluation in general:
        When secondary .md pages had been committed, i.e. are present on the filesystem
        (built while authoring), we will NOT re-evaluate those pages at presence of that
        flag.
        In order to get on-demand eval, just run lp w/o that flag and possibly a match
        on your source file (-lpe=mysourcefile instead -lpe=md). Or delete the md.
        """

        n = 'Only eval when there are no .md files'
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


# --------------------------------------------------------------------- tools/  actions
class S:
    class stats:
        blocks_total = 0
        blocks_skipped_transferred_previous_res = 0
        blocks_skipped_no_previous_res = 0
        blocks_evaled = 0
        blocks_max_time = 0
        blocks_longer_2_sec = 0
        blocks_longer_10_sec = 0
        pages_evaluated = 0
        pages_transferred = 0


S.lp_files = {}
S.lp_stepmode = False
S.lp_evaluation_timeout = 1
S.lp_on_err_keep_running = True


exists = os.path.exists
now = time.time
dirname = os.path.dirname


class LP:
    """literate programming feature"""

    eval_lock = '.evaluation_locked'
    skipped_on_lock = set()
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
    ids_by_fn        = {}
    # fmt:on

    def handle_skips(blocks):
        def skip(b):
            b['kwargs']['skip_this'] = True

        for b in blocks:
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

    def exception(cmd, exc, tb, kw):
        c = markdown.Mkdocs.py % {'cmd': cmd, 'kw': kw, 'trb': str(tb)}
        app.error('LP evaluation error', exc=exc)
        if not S.lp_on_err_keep_running:
            app.die(LP.err_admon, cmd=cmd, lp_file=S.cur_fn_lp, exc=exc, **kw)
        return markdown.Mkdocs.admon(LP.err_admon + ': %s' % str(exc), c, 'error')

    run_file = lambda fn_lp: LP.run_md(read_file(fn_lp), fn_lp, write=True)

    def run_md(md, fn_lp, write=False, raise_on_errs=None):
        """
        fn_lp required for filenames of async lp results
        raise_on_errs intended for temporarily changing behviour, e.g. for tests
        Else use the FLG.
        """
        if os.path.exists(fn_lp):
            os.environ['DT_DOCU'] = os.path.dirname(fn_lp)
            os.environ['DT_DOCU_FILE'] = fn_lp
        S.cur_fn_lp = fn_lp
        lp_blocks, dest = LP.extract_lp_blocks(md=md, fn_lp=fn_lp)
        have_skips = LP.handle_skips(lp_blocks)
        # the file is only in this set if the .md is present and the source file
        # changed - we replace then results by id from the .md:
        md_dest = None
        if fn_lp in LP.skipped_on_lock:
            for b in lp_blocks:
                b['kwargs']['skip_this'] = True
            have_skips = True
        if have_skips:
            LP.current_dest_md = read_file(fn_lp.split('.lp', 1)[0], dflt='')
        else:
            LP.current_dest_md = None

        app.warn(fn_lp)
        app.info('%s lit prog blocks' % len(lp_blocks))
        res = []
        # the doc file:
        fnd = LP.fn_lp(fn_lp)
        [
            res.append(LP.run_block(block, fnd, raise_on_errs=raise_on_errs))
            for block in lp_blocks
        ]
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

    def run_block(block, fnd, raise_on_errs=None):
        """
        fnd: '/home/gk/repos/blog/docs/ll/vim/vim.md'
        block.keys: ['nr', 'code', 'lang', 'args', 'kwargs', 'indent', 'source', 'source_id', 'fn']
        """
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
            kw['lang'] = block.get('lang')
            kw['sourceblock'] = block.get('source')
            S.lp_stepmode and LP.confirm('Before running', page=fnd, cmd=cmd, **kw)
            run_lp = partial(lit_prog.run, fn_doc=fnd)
            kw['timeout'] = kw.get('timeout', S.lp_evaluation_timeout)
            S.stats.blocks_total += 1
            id = '<!-- id: %(source_id)s -->' % block
            res = None
            if kw.get('skip_this'):
                m = LP.current_dest_md
                l = m.split(id)
                if len(l) == 3:
                    res = l[1][:-1]
                    S.stats.blocks_skipped_transferred_previous_res += 1
                else:
                    S.stats.blocks_skipped_no_previous_res += 1

            if not res:
                if not kw.get('skip_this'):
                    S.stats.blocks_evaled += 1
                t0 = now()
                res = run_lp(cmd, *args, **kw)
                dt = now() - t0
                if dt > S.stats.blocks_max_time:
                    S.stats.blocks_max_time = round(dt, 3)
                if dt > 2:
                    S.stats.blocks_longer_2_sec += 1
                if dt > 10:
                    S.stats.blocks_longer_10_sec += 1

            res = '%s%s\n%s' % (id, res, id)

            # inteded for the last block of a big e.g. cluster setup page:
            sol = block['fn'] in LP.skipped_on_lock
            if (kw.get('lock_page') and not kw.get('skip_this')) or sol:
                LP.write_lock_file(fnd)

        except Exception as e:
            # intended for pytesting lp itself:
            if raise_on_errs:
                raise
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

    def write_lock_file(fnd, have=set()):
        """When we hit a lock_page header arg, we write this file with a timestamp of
        the source in first line. That prevents re-eval of LP blocks. On md changes of
        the .lp file we transfer the previous result"""
        if fnd in have:
            return
        have.add(fnd)
        fnl = fnd + '.lp'
        with open(fnl + LP.eval_lock, 'w') as fd:
            s = '%s\n\nA "lock_page" attribute was set in a successfully evaluated '
            s = s % int(os.stat(fnl).st_mtime)
            s += 'literate programming block - this file prevents automatic '
            s += 're-evaluation.\n\nRemove file to re-evaluate or specify a single match in -lpe arg.'
            fd.write(s)
        app.warn('Successful evaluation - page locked.', details=s)
        app.info('(This is NOT an error)')

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
        err, res = lit_prog.parse_header_args(H, fn_lp=fn_lp, dir_project=project.root())
        if not err:
            return res

        return (
            LP.header_parse_err,
            {LP.py_err: res[0], LP.easy_args_err: res[1], 'header': H},
        )

    def extract_lp_blocks(md, fn_lp):
        s = md.splitlines()

        lps = []
        end = '```'
        lpnr = -1
        dest = []
        LP.ids_by_fn.setdefault(fn_lp, {})

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
            src_header = dest[-1].strip()
            lpnr += 1
            lp_header = dest.pop(-1)
            dest.append(LP.PH(lpnr))  # placeholder
            n = [l[len(ind) :] for l in n[:-1]]
            source = src_header + '\n' + '\n'.join(n) + '\n```'
            id = md5(bytes(source, 'utf-8')).hexdigest()
            reg = LP.ids_by_fn.get(fn_lp)
            while id in reg:
                id += '_'
            reg[fn_lp] = id
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
                'source': source,
                'source_id': id,
                'fn': fn_lp,
            }

            lps.append(spec)
        return lps, dest

    def is_lp(d, fn, match='', _msged=set()):
        """
        We get all files in the docs dir matching match (md)

        """
        # and fm in fn
        # and not fn.endswith('.lp.md')
        # and LP.fn_lp(fn) in mkdocs
        if not fn.endswith('.md.lp'):
            return
        r = ''
        if S.lp_evaluation_skip_existing and exists(d + '/' + fn.rsplit('.lp', 1)[0]):
            r = '.md exists, skip_existing set'
        ffn = d + '/' + fn
        if not match in ffn:
            r = 'Not matching %s' % match
        else:
            l = ffn + LP.eval_lock
            if exists(l) and exists(l.rsplit('.lp', 1)[0]):
                r = 'Evaluation lockfile present (%s).'
                r = r % l
                r += ' Remove lock to re-eval lp blocks.'
                LP.skipped_on_lock.add(ffn)
        if r:
            if not ffn in _msged:
                app.info('LP: skipping %s' % fn, reason=r, dir=d)
                _msged.add(ffn)
            return

        return True

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
        os.environ['DT_PROJECT_ROOT'] = project.root()
        for fn in files:
            t = os.stat(fn)[8]
            if t == S.lp_files.get(fn):
                continue
            do_files.append(fn)
            S.lp_files[fn] = t
        skips, fn_single_skipped = LP.skipped_on_lock, None
        if do_files:
            app.info('Re-evaluating lp files', files=do_files, of=files)
        else:
            if len(skips) == 1:
                fn_single_skipped = fn = list(skips)[0]
                skips.remove(fn)
                app.warn('Removing skip on locked file, due to single match', fn=fn)
                do_files.append(fn)

        S.stats.pages_evaluated = len(do_files)
        [do(LP.run_file, fn_lp=fn) for fn in do_files]

        if skips:
            app.info('Handling skipped on lock files', fns=skips)

        for f in skips:
            h = str(int(os.stat(f).st_mtime))
            l = f + LP.eval_lock
            s = read_file(l).split('\n', 1)[0].strip()
            if str(h) != s and s.isnumeric():
                S.stats.pages_transferred += 1
                msg = 'Source changed, md present, transferring updated md content'
                app.warn(msg, fn=f)
                do(LP.run_file, fn_lp=f)
            else:
                app.info('Source unchanged, leaving', fn=f)
        return do_files
