"""
###  `python`

This runs the block within a python session.

All context available in the `ctx` dicts.

Result will be what is printed on stdout.

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied.
"""

from importlib import import_module
from io import StringIO
from pprint import pformat

from lcdoc import lp
from lcdoc.tools import app, dirname, exists, os, project, read_file, write_file

err = lp.err
multi_line_to_list = False
fmt_default = 'unset'

sessions = S = {}

config = lambda: Session.kw['LP'].config
page = lambda: Session.kw['LP'].page
lpkw = lambda: Session.kw
stats = lambda: page().stats


def new_session_ctx():
    return {'out': [], 'locals': {}, 'assets': {}}


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
        Session.cur['out'].clear()
        if cls.name is None:
            Session.cur['locals'].clear()
            sessions.pop(None)  # forget it, no name was given
        # we support post param to run system stuff before python
        lp.SessionNS.post(session_name, kw)


def out(s, t=None, innerkw=None):
    Session.cur['out'].append([t, s, innerkw])


def printed(s, **innerkw):
    out(s, 'printed', innerkw=innerkw)


def show(s, **innerkw):
    f = matching_pyplug(s, innerkw)
    if f:
        s = f(s, **innerkw)
        # need this for call_flow_logging :-/
        if isinstance(s, dict):
            if 'nocache' in s:
                lpkw()['nocache'] = s['nocache']
            s = s['res']
    out(s, 'md', innerkw=innerkw)


# keys: matching strings on s and s class, with s the argument of `show()`:

fmts = {}


def matching_pyplug(s, innerkw):
    """find rendering pyplug based on type of output"""
    if innerkw.get('md'):
        return  # markdown was forced (show('> foo', md=True)
    if isinstance(s, str) and s in fmts:
        return fmts[s]
    for k in fmts:
        if callable(k):
            r = k(s, innerkw)
            if r:
                return fmts[k]
        elif k in str([s, s.__class__]):
            return fmts[k]
    if not isinstance(s, str):
        app.die('No formatter matched', s=s, **innerkw)


def fmt(t, s, kw):
    if t == 'md':
        o = (False, s)
    elif isinstance(s, str):
        o = (True, s)
    else:
        o = (True, pformat(s))
    return o


D_lp_py = lambda: project.root() + '/build/autodocs/lp_python/'

import sys


def cmd_to_module_file(cmd, kw):
    dr = D_lp_py()
    fn = dr + dirname(kw['LP'].page.file.src_path) + '/%(id)s.py' % kw
    h = 'from lcdoc.mkdocs.lp.plugs import python'
    h += '\nprint  = python.printed'
    h += '\nshow = python.show'
    h += '\ndef run_lp_flow():'
    cmd = ('\n' + cmd).replace('\n', '\n    ')
    write_file(fn, h + '\n' + cmd, mkdir=1)
    sys.path.insert(0, dirname(fn)) if not dirname(fn) in sys.path else 0
    return fn


import importlib


def run(cmd, kw):
    """
    interpret the command as python
    """
    # short form convenience: `lp:python show=project_dependencies`
    # set if not yet done:
    project.root(kw['LP'].config)
    shw = kw.pop('show', '')
    if shw and isinstance(cmd, str):
        cmd = 'show("%s")' % shw + cmd
    if kw.get('cfl'):
        modfn = cmd_to_module_file(cmd, kw)
        m = importlib.import_module(kw['id'])
        m.run_lp_flow()
    else:
        loc = Session.cur['locals']
        g = {'print': printed, 'show': show, 'ctx': kw}
        loc.update(g)
        exec(cmd, loc)
    o = Session.cur['out']
    res = [fmt(*i) for i in o]
    fncd = False
    r = ['']
    add = lambda k: r.append(k) if k is not None else 0
    # if the fmt is given (mk_console usually), then we show the command (python code)
    # and the output within the usual lp fenced code block.
    # if it was unset then we open and close fenced code only for print outs
    fstart, fstop = (None, None)
    if kw['fmt'] == 'unset':
        fstart = '```python'
        fstop = '```'
    while res:
        is_fenced, o = res.pop(0)
        if is_fenced and not fncd:
            add(fstart)
            fncd = True
        elif not is_fenced and fncd:
            add(fstop)
            fncd = False
        add(o)
    if fncd:
        add(fstop)
    res = '\n\n'.join(r)
    r = {'res': res}
    # python code may explicitly set a result as object, ready to process e.g. in a mode pipe
    rslt = Session.cur['locals'].get('result')
    if rslt:
        r['result'] = rslt
    # was fmt given by user?
    if kw['fmt'] == 'unset':
        r['formatted'] = True
    if 'nocache' in kw:
        r['nocache'] = kw['nocache']
    r.update(Session.cur['assets'])
    return r


def import_pyplugs(frm):
    m = import_module(frm)
    for k in [i for i in dir(m) if not i.startswith('_')]:
        v = getattr(m, k)
        if hasattr(v, 'register'):
            v.register(fmts)


import_pyplugs('lcdoc.mkdocs.lp.plugs.python.pyplugs')
try:
    import_pyplugs('lp_python_plugins')  # allow customs
except ModuleNotFoundError as ex:
    pass
