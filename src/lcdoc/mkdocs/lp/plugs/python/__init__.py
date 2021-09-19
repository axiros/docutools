"""
###  `python`

This runs the block within a python session.

All context available in the `ctx` dicts.

Result will be what is printed on stdout.

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied.
"""

from pprint import pformat
from io import StringIO
from lcdoc import lp
from lcdoc.tools import os, project, read_file, dirname

multi_line_to_list = False
fmt_default = 'mk_console'

sessions = S = {}


def new_session_ctx():
    return {'out': []}


class Session(lp.SessionNS):
    name = None
    cur = None
    kw = None

    @classmethod
    def delete(cls, ns, kw):
        sessions.pop(ns, 0)

    @classmethod
    def pre(cls, session_name, kw):
        Session.name, Session.kw = session_name, kw
        Session.cur = sessions.setdefault(session_name, new_session_ctx())
        # we support pre param to run system stuff before python
        lp.SessionNS.pre(session_name, kw)

    @classmethod
    def post(cls, session_name, kw):
        if cls.name is None:
            sessions.pop(None)  # forget it, no name was given
        # we support post param to run system stuff before python
        lp.SessionNS.post(session_name, kw)


def out(s, t=None, innerkw=None):
    Session.cur['out'].append([t, s, innerkw])


def printed(s, **innerkw):
    out(s, 'printed', innerkw=innerkw)


def show(s, **innerkw):
    out(s, 'md', innerkw=innerkw)


config = lambda: Session.kw['LP'].config
page = lambda: Session.kw['LP'].page


def matplotlib_pyplot(plt, kw):
    fn = config()['site_dir'] + '/' + page().file.src_path
    fn = fn.rsplit('.md', 1)[0] + '/img'
    os.makedirs(fn, exist_ok=True)
    fn += '/plot.svg'
    plt.savefig(fn, transparent=True)
    return False, '![](./img/plot.svg)'


fmts = {'matplotlib.pyplot': matplotlib_pyplot}


def fmt(t, s, kw):
    o = None
    for k in fmts:
        if k in str([s, s.__class__]):
            o = fmts[k](s, kw)
            break
    if not o:
        o = (False, s) if t == 'md' else (True, pformat(s))
    return o


def run(cmd, kw):
    """
    interpret the command as python:
    no session, lang = python:
    """

    # when a breakpoint is in a python block redirection sucks, user wants to debug:
    # TODO: write cmd to a file for better debugging
    res = exec(cmd, {'print': printed, 'show': show, 'ctx': kw})
    o = Session.cur['out']
    if res:
        out(res, 'result')
    res = [fmt(*i) for i in o]
    fncd = False
    r = []
    add = r.append
    while res:
        is_fenced, o = res.pop(0)
        if is_fenced and not fncd:
            add('```python')
            fncd = True
        elif not is_fenced and fncd:
            add('```')
        add(o)
    if fncd:
        add('```')
    return {'res': '\n\n'.join(r), 'formatted': True}
