"""
###  `python`

This runs the block within a python session.

All context available in the `ctx` dicts.

Result will be what is printed on stdout.

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied.
"""


import sys
from io import StringIO

from lcdoc import lp

multi_line_to_list = False
fmt_default = 'mk_console'


def run(cmd, kw):
    """
    interpret the command as python:
    no session, lang = python:
    """
    h = sys.stdout
    # when a breakpoint is in a python block redirection sucks, user wants to debug:
    # TODO: write cmd to a file for better debugging
    redir = True if not 'breakpoint()' in cmd else False
    if redir:
        sys.stdout = StringIO()
    else:
        msg = '"breakpoint()" found -> not redir stdout. Result will be this message'
        print(msg)
        res = msg
    try:
        exec(cmd, {'ctx': kw})
    except Exception as ex:
        if redir:
            sys.stdout = h

    finally:
        if redir:
            try:
                res = sys.stdout.getvalue()
            except AttributeError as ex:
                res = ''  # nothing printed
            sys.stdout = h
    return {'cmd': cmd, 'res': res}
