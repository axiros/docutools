import os, time
from lcdoc import lp
from functools import partial as p

env = os.environ
wait = time.sleep
now = time.time
I = lp.I


def init_prompt(n):
    """run before each command"""
    # -R reset terminal state:
    lp.sprun('tmux send-keys -R -t %s:1' % n)
    # if not mode == 'python':
    #     sprun('tmux send-keys -t %s:1 "clear" Enter' % n)
    #     while b'clear' in sprun('tmux capture-pane -ep -t %s:1' % n):
    #         wait(0.05)
    # else:
    #     pass
    #     # sprun('tmux send-keys -t %s:1 "%s" Enter' % (n, begin_cmd))

    lp.sprun('tmux clear-history -t %s:1' % n)
    lp.sprun("tmux send-keys -t %s:1 '' Enter" % n)


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
        # new session:
        s = session_name
        # path is set new. bash (if executing user's shell is fish we'd be screwed)
        lp.sprun('export SHELL=/bin/bash; export p="$PATH"; tmux new -s %s -d' % s)
        dt = []
        for k in [i for i in env if i[:3] == 'LP_']:
            dt.append('%s="%s"' % (k, env[k]))
        dt = ' '.join(dt)
        a = 'tmux send-keys -t %(session)s:1 \'export PATH="$p" PS1="%(prompt)s" '
        a += "%(dt)s' Enter"

        b = {'prompt': kw.get('prompt', '$ '), 'session': s, 'dt': dt}
        for i in (1, 2):
            try:
                lp.sprun(a % b)
                # the reset in init prompt needs thate time before
                # otherwise you have the command 2 times in
                time.sleep(0.2)
                break
            except Exception as ex:
                # on new systems it maybe just missing or the user / runner does
                # not care. Lets do it:
                fn = env.get('HOME', '') + '/.tmux.conf'
                if not lp.exists(fn) and i == 1:
                    print('!! Writing %s to set base index to 1 !!' % fn)
                    r = 'set-option -g base-index 1\nset-window-option '
                    r += '-g pane-base-index 1\n'
                    with open(fn, 'w') as fd:
                        fd.write(r)
                    continue
                # everybody has 1 and its a mess to detect or change

                msg = 'tmux session start failed. Do you have tmux, configured with'
                msg += 'base index 1? 0 is default but will NOT work!!'
                raise Exception(msg)

        init_prompt(s)
        if kw.get('root'):
            lp.sprun('tmux send-keys -t %s "sudo bash" Enter' % s)
            wait(0.1)

    res = p(srun_in_tmux, session_name=session_name)
    return res


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
        kill(session_name)
    return res


def srun_in_tmux(cmd, session_name, expect=None, timeout=1, **kw):
    n = session_name

    # TODO: clean up
    assert_ = None
    silent = kw.get('silent')
    # undocumented
    wait_after = kw.get('wait_after')

    c = lp.check_inline_lp(cmd, fn_lp=kw.get('fn_doc'))
    if c:
        cmd = c
    do_post = None
    if isinstance(cmd, dict):
        h = handle_cwd_pre_post
        [h(k, cmd, session_name, **kw) for k in ('cwd', 'pre')]
        if 'post' in cmd:
            do_post = p(h, 'post', cmd, session_name, **kw)

        timeout = cmd.get('timeout', timeout)
        expect = cmd.get('expect', expect)
        assert_ = cmd.get('asserts') or cmd.get('assert', assert_)
        silent = cmd.get('silent', silent)
        wait_after = cmd.get('wait_after', wait_after)
        cmd = cmd.get('cmd')  # if not given: only produce output
    if cmd.startswith('wait '):
        time.sleep(float(cmd.split()[1]))
        return 'silent'

    sk = 'send-keys:'
    if cmd.startswith('send-keys:'):
        lp.spresc('tmux send-keys -t %s:1 %s' % (n, cmd.split(sk, 1)[1].strip()))
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
        expectb = b'sollte nie vorkommen, we want timeout'
    else:
        expectb = expect.encode('utf-8')
    if cmd:
        init_prompt(n)
        # send the sequence as hex (-H):
        seq = ' '.join([hex(ord(b))[2:] for b in cmd])
        seq += ' a'
        # if is_multiline:
        #     breakpoint()  # FIXME BREAKPOINT
        #     for line in cmd.splitlines():
        #         spresc("tmux send-keys -t %s:1 '%s' Enter" % (n, line))
        # else:
        #     spresc("tmux send-keys -t %s:1 '%s' Enter" % (n, cmd))
        print(' cmd to tmux: ', I(cmd))
        print('\x1b[38;5;250m', end='')
        lp.spresc('tmux send-keys -t %s:1 -H %s' % (n, seq))
        print('\x1b[0m', end='')

    t0 = now()
    wait_dt = 0.1
    last_msg = 0
    max_wait = 2

    while True:
        res = lp.sprun('tmux capture-pane -epJS -1000000 -t %s:1' % n)
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
            print('%ss[%s] Inspect:  tmux att -t %s' % (round(dt, 1), timeout, n))
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

    print('----------')
    print(res)
    print('----------')
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


def kill(session_name):
    os.system('tmux kill-session -t %s' % session_name)
