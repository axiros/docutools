"""
###  make_file

Creates a file and displays it as if we used cat on it.

#### Parameters
- fn
- replace: optional replacements to apply (dict)
- content (the body of the lp block)
- chmod: optional chmod params
"""


import os, json
from lcdoc.lp_session import get_cwd

fmt_default = 'mk_console'


def within_session_dir(session_name, func):
    if not session_name:
        return func()
    here = os.getcwd()
    try:
        os.chdir(get_cwd(session_name))
        return func()
    finally:
        os.chdir(here)


def show_file(cmd, kw):
    """to have it all together we keep this mode here"""

    def f(kw=kw):
        fn = kw['fn']
        with open(fn, 'r') as fd:
            c = fd.read()
        res = {'cmd': 'cat %s' % fn, 'res': c}
        if kw.get('lang') not in ['sh', 'bash']:
            res['cmd'] = '$ ' + res['cmd']
        return res

    return within_session_dir(kw.get('session_name'), f)


def run(cmd, kw):

    kw['content'] = cmd
    session_name = kw.get('session_name')

    def f(kw=kw):
        fn = kw['fn']
        c = kw['content']
        if kw.get('replace'):
            d = dict(os.environ)
            d.update(kw)
            if '%(' in c and ')s' in c:
                c = c % d
            else:
                c = c.format(**d)

        if kw.get('lang') in ('js', 'javascript', 'json'):
            if isinstance(c, (dict, list, tuple)):
                c = json.dumps(c, indent=4)
        with open(fn, 'w') as fd:
            fd.write(str(c))
        os.system('chmod %s %s' % (kw.get('chmod', 660), fn))
        return show_file('', kw)

    return within_session_dir(session_name, f)
