#!/usr/bin/env python
"""
Testing lob.py snippets

"""
from plugins import _tools as tools
from devapp.app import app
import os, sys, json


# ------------------------------------------------------------------------------ config


class Flags(tools.BaseFlags):
    autoshort = ''

    class snippet:
        n = 'Snippet code or file'
        d = """run('ls -lta / --color=always', fmt='xt_flat')"""

    class sh_ansi_file:
        n = 'Output created ansi files'
        d = False


main = lambda: tools.main(runit, Flags)
FLG = tools.FLG
D = tools.D
exists = tools.exists
do = tools.do
system = tools.system
dirname = os.path.dirname
# ----------------------------------------------------------------------------- actions


def set_sys_path():
    pp = os.environ['HOME'] + '/.doom.d/bin'
    if not pp in sys.path:
        sys.path.insert(0, pp)
    app.info('added (like emacs in config.el) to sys.path', dir=pp)


class S:
    pass


import importlib

T = """
import sys, os
pp = os.environ['HOME'] + '/.doom.d/bin'
if not pp in sys.path:
    sys.path.insert(0, pp)
import lob
run= lob.p(lob.run, fn_org="%s/foo.org")
%s """


def run_snippet():
    import lob

    d_test = '/tmp/sniptests'
    s = FLG.snippet
    if os.path.exists(s):
        app.info('snippet is a file', reading=s)
        s = tools.read_file(s)
    S.code = s
    S.mod_code = T % (d_test, S.code)

    os.makedirs(d_test, exist_ok=True)
    if d_test.startswith('/tmp/'):  # fear...
        os.system('/bin/rm -rf "%s/*"' % d_test)
    else:
        raise
    sys.path.insert(0, d_test)

    fnm = d_test + '/test_snippet.py'
    app.info('writing', test_mod_file=fnm)
    tools.write_file(fnm, S.mod_code)
    app.info('importing test_mod_file', content=S.mod_code)
    mod = importlib.import_module('test_snippet')
    app.info('Result', result=mod.lob.last_result[0])
    l = mod.lob.last_ansi_file[0]
    if l:
        app.info('.ansi file was created', fn=l)
    if FLG.sh_ansi_file:
        c = tools.read_file(l)
        app.info('.ansi file content', content=c)


def runit():
    app.warn('Running lob code snippet'.upper(), dir=D(), snip=FLG.snippet)
    do(run_snippet)
