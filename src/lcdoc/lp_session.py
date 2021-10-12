import os
import sys
import time
from functools import partial as p

from lcdoc import lp
from lcdoc.tools import write_file

env = os.environ
wait = time.sleep
now = time.time
exists = lp.exists
I = lp.I
L = lp.L

dbg = lp.dbg

is_lprunner = lp.is_lprunner


def tmux_ver_check(checked=[0]):
    """tmux -H only from 3.0"""
    if checked[0]:
        return
    msg = 'Please install tmux, version >= 3.0'
    t = os.popen('tmux -V').read().replace(' ', '')
    if not t or 'tmux2' in t or 'tmux1' in t:
        lp.app.die(msg)
    checked[0] = 1


def init_prompt(n, kw):
    """run before each command"""
    if not is_lprunner[0]:
        lp.sprun('tmux send-keys -R -t %s:1' % n)  # -R reset terminal state
        lp.sprun('tmux clear-history -t %s:1' % n)
    lp.sprun("tmux send-keys -t %s:1 '' Enter" % n)
    t0 = now()
    p = prompt(kw)
    while now() - t0 < 2:
        res = lp.sprun('tmux capture-pane -epJS -1000000 -t %s:1' % n)
        r = res.decode('utf-8').rstrip()
        if r and (r.endswith(p) or r[-1] in {'#', '$'}):
            return
        dbg('waiting for prompt...', have=r, want=p)
        wait(0.1)
    raise Exception('No Prompt; Have so far: %s' % r)


def get_cwd(session_name):
    res = srun_in_tmux('echo "::$(pwd)::"', session_name=session_name)
    res = res.rsplit('::')[-2]
    assert os.path.exists(res)
    return res


def get(session_name, **kw):
    """
        Starts tmux if not running and delivers a srun_in_tmux function,
        parametrized for that session.
        """
    s = '\n' + os.popen('tmux ls').read()
    if not '\n%s:' % session_name in s:
        create(session_name, kw)
    if is_lprunner[0]:
        global lprunner
        from lcdoc import lprunner

        lprunner.show_tmux(session_name)

    res = p(srun_in_tmux, session_name=session_name)
    return res


# :docs:configure_tmux_base_index_1
def configure_tmux_base_index_1(session_name):
    """
    Seems everybody really using it has 1 (on normal keyboards 0 is far away)
    and its a hard to detect or change, especially when the messed with it outside of
    our control. 

    On clean systems it will be just missing or: the user / runner does not care.

    => Lets create it - when it is NOT present, so that we can have automatic CI/CD.
    While for a normal user (who is using it) we fail if not configured correctly.
    """
    fn = env.get('HOME', '') + '/.tmux.conf'
    if exists(fn):
        return

    lp.app.warning('!!! Writing %s to set base index to 1 !!' % fn)
    r = [
        'set-option -g base-index 1',
        'set-window-option -g pane-base-index 1',
        '',
    ]
    write_file(fn, '\n'.join(r))
    lp.sprun('tmux source-file "%s"' % fn)
    wait(0.5)
    tmux_kill_session(session_name)
    wait(0.5)
    tmux_start(session_name)
    wait(0.5)


# :docs:configure_tmux_base_index_1


def prompt(kw):
    return kw.get('prompt', '$')


def tmux_start(session_name):
    # path is set new. bash (if executing user's shell is fish we'd be screwed)
    s = session_name
    lp.sprun('export SHELL=/bin/bash; export p="$PATH"; tmux new -s %s -d' % s)


def create(session_name, kw):
    # new session:
    tmux_ver_check()
    s = session_name
    tmux_start(s)
    # all lp vars into the session, maybe of use:
    lp_env = ['%s="%s"' % (i, env[i]) for i in env if i[:3] in ('LP_', 'lp_')]
    lp_env = ' '.join(lp_env)
    a = 'tmux send-keys -t %(session)s:1 \'export PATH="$p" PS1="%(prompt)s " '
    a += "%(lp_env)s' Enter"

    b = {'prompt': prompt(kw), 'session': s, 'lp_env': lp_env}
    for try_nr in (1, 2):
        try:
            lp.sprun(a % b)
            # the reset in init prompt needs thate time before
            # otherwise you have the command 2 times in
            time.sleep(0.2)
            break
        except Exception as ex:
            if try_nr == 1:
                configure_tmux_base_index_1(session_name)
                continue

            msg = 'tmux session start failed. Do you have tmux, configured with'
            msg += 'base index 1? 0 is default but will NOT work!!'
            raise Exception(msg)

    init_prompt(s, kw)
    if kw.get('root'):
        lp.sprun('tmux send-keys -t %s "sudo bash" Enter' % s)
        wait(0.1)


def handle_cwd_pre_post(cpp_mode, spec, session_name, timeout=1, **kw):
    t = {'cwd': 'cd "%s"', 'pre': '%s', 'post': '%s'}[cpp_mode]
    cmd = spec.get(cpp_mode)
    if cmd:
        cmd = t % cmd
        sn = session_name
        srun_in_tmux(cmd, session_name=sn, timeout=0.1)


def srun(cmds, session_name, **kw):
    S = get(session_name, **kw)
    if kw.get('with_paths'):
        for e in 'PATH', 'PYTHONPATH':
            S('export %s="%s"' % (e, os.environ.get(e, '')), **kw)
    h = handle_cwd_pre_post
    [h(k, kw, session_name, **kw) for k in ('cwd', 'pre')]
    res = [{'cmd': cmd, 'res': S(cmd, **kw)} for cmd in lp.to_list(cmds)]
    h('post', kw, session_name, **kw)
    res = [i for i in res if not i.get('res') == 'silent']  # sleeps removed
    if kw.get('kill_session'):
        tmux_kill_session(session_name)
    return res


def srun_in_tmux(cmd, session_name, expect=None, timeout=1, **kw):
    n = session_name

    # TODO: clean up
    assert_ = None
    silent = kw.get('silent')
    # undocumented
    wait_after = kw.get('wait_after')

    do_post = None
    if isinstance(cmd, dict):
        h = handle_cwd_pre_post
        [h(k, cmd, session_name, **kw) for k in ('cwd', 'pre')]
        if 'post' in cmd:
            do_post = p(h, 'post', cmd, session_name, **kw)

        # fmt:off
        timeout    = cmd.get('timeout', timeout)
        expect     = cmd.get('expect', expect)
        assert_    = cmd.get('asserts') or cmd.get('assert', assert_) # asserts:deprecated
        silent     = cmd.get('silent', silent)
        wait_after = cmd.get('wait_after', wait_after)
        cmd        = cmd.get('cmd')  # if not given: only produce output
        # fmt:on

    if cmd.startswith('wait '):
        time.sleep(float(cmd.split()[1]))
        return 'silent'

    sk = 'send-keys:'
    if cmd.startswith('send-keys:'):
        cmd = cmd.split('#', 1)[0]
        lp.spresc('tmux send-keys -t %s:1 %s' % (n, cmd.split(sk, 1)[1].strip()))
        # at ci seen delays after C-c:
        wait(0.1)
        return 'silent'

    expect_echo_out_cmd = ''
    is_multiline = '\n' in cmd
    if expect is None:
        # we do NOT fail on exit codes, just want to know if the command completed,
        # by scraping the tmux output for a string:
        # if you want the first send set -e
        sep = '\n' if (is_multiline or ' # ' in cmd) else ';'
        # here docs can't have ';echo -n... at last line:
        # not match on the issuing cmd
        expect_echo_out_cmd = sep + 'echo -n ax_; echo -n done'
        cmd += expect_echo_out_cmd
        expect = 'ax_done'

    if expect is False:
        expectb = b'des soid ned bassian - we want timeout'
    else:
        expectb = expect.encode('utf-8')
    if cmd:
        init_prompt(n, kw)
        # send the sequence as hex (-H):
        if is_lprunner[0]:
            lprunner.confirm(cmd)
        seq = ' '.join([hex(ord(b))[2:] for b in cmd])
        seq += ' a'
        # if is_multiline:
        #     breakpoint()  # FIXME BREAKPOINT
        #     for line in cmd.splitlines():
        #         spresc("tmux send-keys -t %s:1 '%s' Enter" % (n, line))
        # else:
        #     spresc("tmux send-keys -t %s:1 '%s' Enter" % (n, cmd))
        _ = expect_echo_out_cmd
        _ = cmd if not _ else cmd.split(_, 1)[0] + L(_)
        symb = '💻'
        lp.nfo(symb, tmux=' ' + _)
        lp.spresc('tmux send-keys -t %s:1 -H %s' % (n, seq))

    t0 = now()
    wait_dt = 0.1
    last_msg = 0
    max_wait = 2

    while True:
        res = lp.sprun('tmux capture-pane -epJS -1000000 -t %s:1' % n)
        dbg(res)
        if expectb in res:
            break
        dt = now() - t0
        if dt > timeout:
            if expect is False:
                # wanted then:
                break
            raise Exception(
                'Command %s: Timeout (> %s sec) expecting "%s"'
                % (cmd, timeout, expectb.decode('utf-8'))
            )

        if now() - last_msg > 5:
            dbg('%ss[%s] Inspect:  tmux att -t %s' % (round(dt, 1), timeout, n))
            lst_msg = now()
        wait(wait_dt)  # fast first
        wait_dt = min(timeout / 10.0, max_wait)
        max_wait = min(5, max_wait + 2)

    res = res.decode('utf-8')
    if expect_echo_out_cmd:
        # when expect was given we include it (expect="Ready to accept Connections")
        # expect_echo_out_cmd is empty then
        res = res.split(expect, 1)[0].strip()
        a = expect_echo_out_cmd
        a = a[1:] if a.startswith('\n') else a  # when \n is the sep we won't see it
        res = res.replace(a, '')
    else:
        # the tmux window contains a lot of white space after the last output when
        # short cmd
        res = res.strip()
    if wait_after:
        time.sleep(float(wait_after))
    lp.check_assert(assert_, res)
    dbg('Have tmux result:', res='\n' + res)
    if do_post:
        do_post()
    return res if not silent else 'silent'


def find_output_range(res, between, ls=b'\n'):
    """default: parse out last range in res between begin and end of between"""
    # todo: regex
    pre, post = res.rsplit(between[0], 1)
    r = pre.rsplit(ls, 1)[-1] + between[0]
    body, post = post.split(between[1], 1)
    r += body
    r += between[1] + post.split(ls, 1)[0]
    return r


def tmux_kill_session(session_name):
    os.system('tmux kill-session -t %s' % session_name)
