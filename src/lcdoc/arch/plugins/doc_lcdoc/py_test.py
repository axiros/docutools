#!/usr/bin/env python
"""
Allows to run the full cycle for autodocs generation

"""
from plugins import _tools as tools
from devapp.app import app
from devapp import tools as datools
import os, sys, json


# ------------------------------------------------------------------------------ config


class Flags(tools.DfltFlags):
    autoshort = ''

    class clear:
        n = 'Clear the autodocs folder'
        d = False

    class flags:
        n = 'If pytest should run, supply the flags here'

    class pre_proc:
        n = 'How to run doc pre_process'

    class mkdocs:
        """Complete Example: doc pt -f "-xs tests/operators/test_build.py" -pp -gad -m"""

        n = 'Run mkdocs build'
        d = False


main = lambda: tools.main(run, Flags)
FLG = tools.FLG
D = tools.D
do = tools.do
system = tools.system

# ----------------------------------------------------------------------------- actions


def run():
    root = datools.project.root()
    if FLG.clear:
        do(system, '/bin/rm -rf "%s/build/autodocs/*"' % root)
    f = FLG.flags
    if f:
        app.warn('Setting $make_autodocs=true -> triggers call flow logging')
        os.environ['make_autodocs'] = 'true'
        e = do(system, 'pytest -p no:randomly %s' % f)
    f = FLG.pre_proc
    if f:
        do(system, 'doc pre_process %s' % f)
    f = FLG.mkdocs
    if f:
        do(system, 'cd "%s" && mkdocs build' % root)
