#!/usr/bin/env python
"""
Wrapper for mkdocs build, with set environment variables, possibly referenced in mkdocs.yml

"""
from plugins import _tools as tools
from devapp.app import app
import os, sys, json


# ------------------------------------------------------------------------------ config


class Flags(tools.DfltFlags):
    autoshort = ''

    env_export_edit_uri = tools.env_export_edit_uri

    class mkdoc_flags:
        n = 'Flags for mkdocs build (--dirty makes a fast build)'
        d = ''


main = lambda: tools.main(run, Flags)
FLG = tools.FLG
D = tools.D
do = tools.do
system = tools.system

# ----------------------------------------------------------------------------- actions


def run_mkdocs_build():
    do(system, 'mkdocs build %s' % FLG.mkdoc_flags)


def run():
    app.warn('Starting mkdocs build'.upper(), dir=D())
    os.chdir(D())
    do(tools.export_mk_edit_base)
    do(run_mkdocs_build)
