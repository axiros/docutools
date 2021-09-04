from lcdoc import lp
from lcdoc.lp_session import srun

multi_line_to_list = True


def run(cmd, kw):
    session_name = kw['session_name']

    if session_name:
        return srun(cmd, **kw)

    # os.system style:
    if not isinstance(cmd, list):
        cmd = [cmd]

    res = []
    for c in cmd:
        c = lp.check_inline_lp(c, fn_lp=kw['fn_doc']) or c
        lp.run_if_present_and_is_dict(c, 'pre')
        c1 = c['cmd'] if isinstance(c, dict) else c
        rcmd = c1
        prompt = '$'
        if kw.get('root'):
            rcmd = 'sudo %s' % rcmd
            rcmd = rcmd.replace(' && ', ' && sudo ')
            prompt = '#'
        # for k, v in aliases.items(): rcmd = rcmd.replace(k, v)
        # return sp.check_output(['sudo podman ps -a'], shell=True)
        r = lp.sprun(rcmd)
        r = r.decode('utf-8').rstrip()
        if isinstance(c, dict):
            lp.check_assert(c.get('assert', c.get('asserts')), r)
        if not kw.get('hide_cmd'):
            r = ''.join([prompt, ' ', c1, '\n', r])
        lp.run_if_present_and_is_dict(c, 'post')
        # res = '%s %s\n' % (prompt, cmd) + res

        res.append({'cmd': c1, 'res': r})
    return res
