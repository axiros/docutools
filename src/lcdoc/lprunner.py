"""
Runs the literate programming blocks within a markdown document.

We open tmux (requirement) and show in one pane the markdown plus the commands to run.
If the commands open a session themselves, we attach in split panes, so that you can
follow the output.

"""

import os
import sys
import time
import traceback
import httpx

from lcdoc.const import lprunner_sep as sep
from lcdoc.mkdocs.tools import split_off_fenced_blocks
from lcdoc.tools import app, dirname, exists, read_file, write_file

env = os.environ


class FLG:
    class tmx_ctrl_color:
        n = 'Color of the controlling TMUX pane (fg/bg)'
        v = '7;16'
        s = 'cc'

    class tmx_lp_color:
        n = 'Color of the LP TMUX pane(s)'
        v = '243;17'
        s = 'cl'

    class confirm_all:
        n = 'Assume yes on all questions'
        v = False
        s = 'y'


class S:
    # fmt:off
    auto_confirm_all = False
    exit_after_run   = False
    fn               = None
    help_shown       = False
    # fmt:on


a = sys.argv
# we are started like this inside tmux:
if len(a) > 1 and a[1] == 'TMXID':
    our_tmx_id = a[2]
    a.pop(1)
    a.pop(1)
else:
    our_tmx_id = str(os.getpid())
OurTmux = 'tmux -S /tmp/lprunner.tmux.%s ' % our_tmx_id
hl = lambda msg: '\x1b[32m%s\x1b[0m' % msg


def restart_in_tmux():
    if env.get('TMUX'):
        del env['TMUX']  # otherwise we could not attach to lp tmux from inside
        return  # we are started inside
    cmd = ['"%s"' % s for s in sys.argv]
    cmd.insert(1, str(os.getpid()))
    cmd.insert(1, 'TMXID')
    err = os.system(OurTmux + 'new -s lprunner ' + ' '.join(cmd))
    sys.exit(err)


class Unconfirmed(Exception):
    pass


have_sessions = set()


def show_tmux(session_name):
    """
    In lp a tmux session was created or is attached to
    We have our session, and attach to that in a split pane,
    then get focus back to this app here
    """
    s = session_name
    if s in have_sessions:
        return
    # found no other way to get focus back to original pane:
    os.system('( sleep 0.1 && %s select-pane -t 1 ) &' % OurTmux)
    cmd = OurTmux + 'split-window -h \'unset TMUX; tmux att -t "%s"\'' % s
    os.system(cmd)
    set_tmx_col('tmux', FLG.tmx_lp_color)
    time.sleep(0.2)
    have_sessions.add(s)


def set_tmx_col(tmx, col):
    c = col.v
    if not c:
        return
    if ';' in c:
        s = 'fg=colour%s,bg=colour%s' % tuple(c.split(';', 1))
    else:
        s = 'bg=colour%s' % c
    os.system(tmx + ' set -g window-style %s' % s)


help_msg = 'a:yes for all e:yes for all, then exit q:quit s:shell y:confirm'


def confirm(msg):
    if S.auto_confirm_all:
        return
    print(hl(msg))
    try:
        if not S.help_shown:
            os.system(OurTmux + 'display-message -p "%s"' % help_msg)
            S.help_shown = True
        r = input('[a|e|h|q|s|Y(default)] ? ')
    except KeyboardInterrupt as ex:
        r = 'q'
    r = r.lower()
    print()
    if r == 's':
        print('entering shell - ctrl+d to exit')
        os.system('bash')
        return confirm(msg)
    if r == 'a':
        S.auto_confirm_all = True
    elif r == 'e':
        S.auto_confirm_all = True
        S.exit_after_run = True
    elif r in ('q', 'n'):
        raise Unconfirmed()


def extract_md_src_from_url(url):
    a = url
    a = (a + '/') if not a.endswith('/') else a
    a += 'runner.md'
    src = httpx.get(a).text
    S.fn = a.split('/', 3)[3].replace('/', '_')
    return src


def exit_help(flgs, shts):
    print(__doc__)
    for k, v in flgs.items():
        print('%4s | %s: %s [%s]' % ('-' + v.s, k.ljust(18), v.n, v.v))

    sys.exit(0)


def chck_book(flg, flags):
    if not flags[flg].v in (True, False):
        return False
    flags[flg].v = not flags[flg].v
    return True


def parse_cli(g=getattr):
    args = list(sys.argv[1:])
    flgs = {'--' + k: g(FLG, k) for k in dir(FLG) if not k.startswith('_')}
    shts = {'-' + v.s: v for k, v in flgs.items()}
    if '-h' in args or '--help' in args or not args:
        exit_help(flgs, shts)
    while args:
        a = args.pop(0)
        if a in flgs:
            if not chck_book(a, flgs):
                flgs[a].v = args.pop(0)
        elif a in shts:
            if not chck_book(a, shts):
                shts[a].v = args.pop(0)
        elif exists(a):
            S.fn = a
        elif a.startswith('http'):
            src = extract_md_src_from_url(a)
            write_file(S.fn, src)
    S.fn = os.path.abspath(S.fn)
    app.name = os.path.basename(S.fn)
    S.auto_confirm_all = FLG.confirm_all.v
    from lcdoc import log

    f = open('/tmp/tmux.log.%s' % our_tmx_id, 'w')
    w = lambda msg, f=f: f.write(msg + '\n')
    log.outputter[0] = w


class mock:
    def page():
        class page:
            src_path = abs_src_path = S.fn
            stats = {}

        return page

    def config():
        return {'docs_dir': dirname(S.fn)}


def show_md(md):
    md = [md] if isinstance(md, str) else md
    for m in md:
        print(m)


def run_lp(spec):
    src = spec['kwargs'].get('source', '')
    show_md(src)
    if not spec['kwargs'].get('runner'):
        return
    try:
        res = LP.run_block(spec)
    except Unconfirmed as ex:
        print('unconfirmed - bye')
        sys.exit(1)


def run_fn():
    markdown = read_file(S.fn)
    LP.page = mock.page()
    LP.config = mock.config()
    LP.previous_results = {}
    LP.cur_results = {}
    LP.fn_lp = S.fn
    mds, lp_blocks = split_off_fenced_blocks(
        markdown, fc_crit=LP.is_lp_block, fc_process=LP.parse_lp_block
    )
    l = lp_blocks
    while mds:
        show_md(mds.pop(0))
        run_lp(lp_blocks.pop(0)) if lp_blocks else None


def setup_our_tmux():
    set_tmx_col(OurTmux, FLG.tmx_ctrl_color)


def main():
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
        parse_cli()  # will exit
    restart_in_tmux()
    try:
        run_in_tmux()
    except SystemExit as ex:
        print('Tmux runner exitted with Error')
        breakpoint()
        print('Hit q to exit')


def run_in_tmux():
    # we are in a subprocess now, running within tmux:
    global LP
    from lcdoc.mkdocs.lp import LP
    from lcdoc import lp

    lp.is_lprunner[0] = True
    try:
        parse_cli()
        setup_our_tmux()
        if not S.fn:
            app.die('Require filename or URL')
        run_fn()
        if not S.exit_after_run:
            S.auto_confirm_all = False
    except Exception as ex:
        traceback.print_exc()
        print(ex)
        print('Error - entering debug mode')
        breakpoint()  # FIXME BREAKPOINT
        print('? for help')
        sys.exit(1)
    try:
        confirm('All done. Exit Tmux.')
        while True:
            if os.system('tmux detach'):
                break
        os.system(OurTmux + 'kill-session')
    finally:
        os.unlink(OurTmux.rsplit(' ', 1)[-1])


if __name__ == '__main__':
    main()
