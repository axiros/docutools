from lcdoc import lp
import sys
from io import StringIO

multi_line_to_list = False


def run(cmd, kw):
    """
    interpret the command as python:
    no session, lang = python:
    """
    kw['fmt'] = kw.get('fmt', 'mk_console')
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
