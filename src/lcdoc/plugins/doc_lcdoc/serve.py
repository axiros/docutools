#!/usr/bin/env python
"""
`doc serve` is a convenience tool which starts the live server together with doc pre_process

(with working but changeable defaults)

Note: You have to run this from the repo root of a checked out devapp project, which has a docs folder.


"""
from devapp.tools import FLG, exists
from devapp.app import app, do, system, run_app
import os, sys, json
import time

# ------------------------------------------------------------------------------ config

from . import pre_process  # import lit_prog_evaluation


class Flags:
    autoshort = ''

    class lit_prog_evaluation(pre_process.Flags.lit_prog_evaluation):
        'Example: re-evaluate only page config.md.lp: doc serve -lpe conf'
        d = 'md'

    class pre_proc:
        n = 'How to run doc pre_process'

    class port:
        n = 'mkdocs live server port. if the port is occupied (checked via netstat) we kill(!) the occupying other process'
        d = 8000

    class only_kill:
        n = 'Action: Only kill server at port'
        d = False


# ----------------------------------------------------------------------------- actions


def kill_server():
    p = FLG.port
    cmd = 'netstat -tanp | grep " LISTEN " | grep ":%s"' % p
    res = os.popen(cmd).read().strip().split()
    if not res:
        return app.warn('No server process was running at port', port=p)
    app.warn('Killing', proc=res)
    proc = res[-1].split('/', 1)[0]
    do(os.kill, int(proc), 9)
    app.warn('Server process at port killed', port=p)


def start_server():
    do(kill_server)
    cmd = 'mkdocs serve --livereload -a 127.0.0.1:%s &' % FLG.port
    do(system, cmd)


def start_doc_preproc():
    cmd = 'doc pre_process --lit_prog_evaluation=%s --lit_prog_evaluation_monitor=true'
    cmd = cmd % FLG.lit_prog_evaluation
    do(system, cmd)


def run():
    if FLG.only_kill:
        return do(kill_server)

    D = os.getcwd()
    if not exists(D + '/docs/'):
        app.die('You have to run doc serve within the repo root of a devapps checkout')
    do(start_server)
    p = FLG.port
    do(start_doc_preproc)


main = lambda: run_app(run, flags=Flags)
