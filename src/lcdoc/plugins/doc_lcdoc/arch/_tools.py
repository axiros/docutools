#!/usr/bin/env python
from devapp.tools import (
    FLG,
    FlagsDict,
    read_file,
    write_file,
    dir_of,
    dict_merge,
    partial,
)
from devapp.app import app, run_app, system, do  # noqa
import os, sys, json, time
from dataclasses import dataclass

wait, now = time.sleep, time.time


# ------------------------------------------------------------------------------ config
exists = os.path.exists
d_start = os.getcwd()
d = d_start
while len(d) > 2:
    if exists(d + '/mkdocs.yml'):
        break
    d = d.rsplit('/', 1)[0]
d_dflt = d if len(d) > 2 else d_start + '/docs'

# used in dev and build:
class env_export_edit_uri:
    n = 'Export $mk_edit_base, used via env var in mkdocs.yml file'
    d = 'org-protocol://roam-file?file=%(dir)s/src/markdown'


class BaseFlags:
    class dir_docset:
        n = '''Directory of docuset (location of its mkdocs.yml).
            Full path or from $d_repo.
            Can contain a .mkdocs.config'''
        d = d_dflt


class DfltFlags(BaseFlags):
    class tmux_base_index:
        """
        base_index 1 means: Start windows and panes at 1, not 0.
        """

        n = 'Set to 0 if your tmux conf has NOT the usual altered base index set to 1.'
        d = 1


def main(run, Flags, log_level=10):
    return run_app(run, flags=Flags, kw_log={'level': log_level})


# ------------------------------------------------------------------------------- tools
here = dir_of(__file__)
d_installer_base = dir_of(here, up=1) + '/docutools/mkdocs'


D = lambda: full_path(FLG.dir_docset)
fn_cfg = lambda: D() + '/.mkdocs.config'
fn_mkdocs_yml = lambda: D() + '/mkdocs.yml'
fn_tmpl = lambda t: d_installer_base + '/templates/%s' % t


def chdir_to_docs_root():
    if not exists(fn_mkdocs_yml()):
        app.die('Cannot derive your docset directory')
    os.chdir(D())


def export_mk_edit_base():
    value = FLG.env_export_edit_uri % {'dir': D()}
    # value = 'org-protocol://roam-file?file=%s/src/markdown' % value
    app.info(
        'exporting $mk_edit_base for mkdocs edit links',
        used_in='mkdocs.yml',
        value=value,
    )
    os.environ['mk_edit_base'] = value


def full_path(fn):
    if os.path.exists(fn):
        fn = os.path.abspath(fn)
    if fn.startswith('/'):
        return fn
    if fn.startswith('.'):
        return os.path.abspath(fn)
    d = os.environ['d_repos']
    return d + '/' + fn


def tar_pipe(frm, to):
    if not exists(to):
        os.mkdir(to)
    do(system, '(cd "%s" && tar -cf - .) | (cd "%s" && tar -xpf -)' % (frm, to))


tdo = partial(do, titelize=True)


def symlink(frm, to, rmdir=False):
    if os.path.islink(to):
        d = os.readlink(to)
        if d != frm:
            app.warn('leaving existing but different link', at=to, points=d, should=frm)
        else:
            app.debug('link exists already', to=to, frm=frm)
        return
    if os.path.exists(to):
        if rmdir:
            app.warn('removing', target=to)
            assert len(to.split('/') > 4)
            do(system, '/bin/rm -rf "%s"' % to)
    do(system, 'ln -s "%s" "%s"' % (frm, to))


def wait_for(msg, f=None, *a, timeout=1, sleep=None, **kw):
    """wait for truthy return of function or, alternative (errcode, value) result"""
    if not isinstance(sleep, list):
        sleep = [timeout / 10.0] if sleep is None else [sleep]
    t0 = now()
    while True:
        res = f(*a, **kw)
        # print(res)
        if res:
            # in errcode, value format?
            if isinstance(res, tuple):
                if not res[0]:
                    return res[1]
            else:
                return res
        if now() - t0 > timeout:
            break
        ls = sleep.pop(0) if sleep else ls
        wait(ls)
    app.die('Timeout waiting', for_=msg, waited=now() - t0, json={'got result': res})


@dataclass
class tmux:
    """
    A tmux session or window within session
    Use get_tmux to get a new parametrized class.
    """

    session_name: str
    window_name: str = ''  # optional

    @classmethod
    def new(cls, session_name=None, first_win='docset', kill_any_old=True):
        sn = session_name or FLG.tmux_session_name
        s = partial(do, system, no_fail=True)
        if kill_any_old:
            s('tmux kill-session -t "%s"' % sn)
        s('tmux new -s "%s" -d -n docset' % sn)
        t = tmux(session_name=sn)
        app.info('crea new', **t.__dict__)
        return t

    def call(self, cmd, args='', no_fail=False):
        sn = self.session_name
        if self.window_name:
            sn += ':%s' % self.window_name
        tcmd = 'tmux ' + cmd + ' -t "%s" ' % sn + args
        do(system, tcmd)

    def new_window(self, name, cmd=None):
        self.call('new-window', '-n "%s"' % name)
        if cmd:
            self.send_keys(cmd)

    def send_keys(self, keys, enter=True):
        keys = '"%s"' % keys
        if enter:
            keys += ' Enter'
        return self.call('send-keys', keys)

    def enter_session(self):
        return self.call('att')

    def capture(self, window=None):
        i = self.session_name
        w = window or self.window_name
        if w:
            i += ':%s' % w
        res = os.popen('tmux capture-pane -p -t "%s"' % i).read()
        return res

    def wait_for(self, content, timeout=1, sleep=None, window=None, monitor=None):
        def f(window=window, monitor=monitor):
            # no_capture can be passed when not-understood timeouts happen, in order
            # to eval the last result
            cap = self.capture(window)
            if monitor:
                for s in monitor['strings']:
                    capl = cap.lower()
                    if s in capl:
                        pre, post = capl.split(s, 1)
                        line = pre.rsplit('\n', 1)[-1] + s + post.split('\n', 1)[0]
                        h = monitor['into'].setdefault(s, set())
                        if not line in h:
                            app.warn('found: "%s"' % s, line=line)
                            h.add(line)
            if content in cap:
                app.debug('found expected content', content=content)
                return 0, cap
            return 1, cap.strip()

        wait_for(content, f, timeout=timeout, sleep=sleep)
