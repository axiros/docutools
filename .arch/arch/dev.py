#!/usr/bin/env python
"""
Starting Dev Server with Dir Change Watcher and Org Publisher

**Alternative** to mkdocs serve --livereload

Requires entr, tmux and npm install live-server
You have more finegrained control on used resources plus the org exporter

It will all be started in a tmux window.
"""
from plugins import _tools as tools
from devapp.app import app
import subprocess as sp
import os, sys, json, time

now = time.time

# ------------------------------------------------------------------------------ config

browsers = {'ff': 'firefox', 'gc': 'google-chrome', 'b': 'brave-browser'}


class Flags(tools.DfltFlags):
    autoshort = ''
    env_export_edit_uri = tools.env_export_edit_uri

    if 1:

        class tmux_cat_session_log:
            n = 'Display the session log'
            d = False

        class tmux_session_name:
            """We are using tmux for multicommand sessions."""

            n = 'Name of tmux session'
            d = 'docset_dev_%(dir_2_levels)s'

        class tmux_enter:
            n = 'Only attach to running session instead of creating a new one, killing the old'
            d = False

        class tmux_attach:
            """2 enables restarts of all services via a single C-b-d"""

            n = 'Attach to session after build services are up. 0: do not attach. 1: attach once. 2: re-attach after exit'
            d = 1

        class tmux_notifier:
            n = 'How to get informed about whats happening in tmux (we also write a log file)'
            d = ''

        class publish_all:
            """
            May take a while, dependent on your lob code blocks.
            """

            n = 'Publishes all org files, one by one.'
            n += 'Note: This will disable the live web server, the md rebuilding, and will set publish_disable_lob_cache to 1. Set it to -1 if you still want to render from cached results.'
            d = False

        class publish_all_excludes:
            n = 'Paths to exclude from delete-republish cycles (comma sep.ed list)'
            d = '/add/,'

        class publish_all_on_err_exit_tmux:
            n = 'By default we do not kill tmux when there is an error'
            d = False

        class publish_all_report_output_strings:
            n = 'Lowercased list of strings we should report when publishing'
            d = 'traceback, wrong, error'

        class publish_disable_lob_cache:
            n = 'Never check cached lob.py results, i.e. run all lob code'
            d = 0

    if 1:

        class server_disable:
            n = 'Do not start server'
            d = False

        class server_browser:
            n = 'Browser to use. Understood also %s' % browsers
            d = 'firefox'

        class server_no_browser:
            n = 'Add --no-browser to the server_cmd'
            d = False

        class server_wait:
            n = 'Wait ms after build'
            d = 500

        class server_cmd:
            n = 'Which server command to use. Run in dir_docset.'
            d = 'while true; do builtin cd site && live-server --browser=%(server_browser)s --wait=%(server_wait)s . ; sleep 1; done'

    if 1:

        class file_watcher_disable:
            n = 'Disable the file watcher'
            d = False

        class file_watcher_follow_symlinks:
            n = 'Follow also repos symlinks when searching for monitored files'
            d = True

        class file_watcher_watch_file_list:
            n = 'Supply a manually built watch file list'

        class file_watcher_org_publish_on_change:
            n = 'Do monitor org and publish on change'
            d = True

        class file_watcher_md_rebbuild_on_change:
            n = 'Do monitor md and rebuild on change'
            d = True

        class file_watcher_mkdoc_build_flags:
            n = 'Flags for mkdocs build'
            d = '--dirty'

        class file_watcher_fg:
            n = 'Runs only(!) the file_watcher in foreground'
            d = False


main = lambda: tools.main(run, Flags)
FLG = tools.FLG
D = tools.D
do = tools.do
system = tools.system


def build_dirs_dict():
    # for the session name:
    m = {'dir': D()}
    parent = D()
    dn, i = '', 0
    while parent:
        i += 1
        parent, d = parent.rsplit('/', 1)
        dn = d + '/' + dn
        m['dir_%s_levels' % i] = dn[:-1]
    return m


# ----------------------------------------------------------------------------- actions
tmux = tools.tmux
exists = tools.exists


class S:
    tmux = None
    stats = {'timings': {}, 'warnings': {}}


class file_watcher:
    tmemcs = None  # emacs window
    d_work = lambda: '/tmp/docs_work%s' % D()
    fn_session_log = lambda: file_watcher.d_work() + '/session.log'
    fn_stats = lambda: file_watcher.d_work() + '/stats.json'
    fn_success = lambda: file_watcher.d_work() + '/published_all_flag'

    def stats_out(stats=None):
        """When called from the tmux spawner it does not have them, but tmux _fg wrote"""
        s = stats or S.stats
        if not s:
            fn = file_watcher.fn_stats()
            if not exists(fn):
                return app.warn('no stats written yet')
            app.debug('stats from file', fn=fn)
            s = tools.read_file(json.loads(fn))
        app.info('stats', json=s)

    def start_in_tmux():
        cmd = sys.argv
        cmd.append('--file_watcher_fg')
        do(S.tmux.new_window, 'file_mon', cmd=' '.join(cmd))

    @classmethod
    def clear_work_dir(fw):
        d_work = fw.d_work()
        app.info('creating work dir', dir=d_work)
        os.makedirs(d_work, exist_ok=True)

        def rm(f):
            ff = os.path.join(d_work, f)
            os.unlink(ff)
            app.info('unlinked', fn=f)

        [rm(f) for f in os.listdir(d_work)]

    @classmethod
    def start_publish_all_fg(fw):
        f = FLG.publish_all_report_output_strings
        FLG.publish_all_report_output_strings = [
            i.strip() for i in f.split(',') if i.strip()
        ]

        def all_mds_in_mkdocs():
            # cannot import the yml due to plugins, so:
            with open('mkdocs.yml') as fd:
                mkd = fd.read().split('\nnav:', 1)[1].splitlines()
            mds = []
            d = D() + '/src/markdown/'
            while mkd:
                line = mkd.pop(0)
                lline = line.strip()
                if lline.startswith('#'):
                    continue
                if lline and not lline.startswith('#'):
                    if not line.startswith(' '):
                        break  # done

                if lline.endswith('.md'):
                    mds.append(d + lline.rsplit(':', 1)[1].strip())
            return mds

        def all_existing_orgs_in_mkdocs():
            mds = all_mds_in_mkdocs()
            orgs = [m.rsplit('.md', 1)[0] + '.org' for m in mds]
            return [o for o in orgs if exists(o)]

        t0 = now()
        excls = {i.strip() for i in FLG.publish_all_excludes.split(',') if i.strip()}
        orgs_all = all_existing_orgs_in_mkdocs()
        orgs = [o for o in orgs_all if not any([f for f in excls if f in o])]
        app.info('will publish', json=orgs, count=len(orgs), total=len(orgs_all))
        for fn in orgs:
            fw.publish_org(fn)
        s = dict(S.stats)
        pt = sorted(s['timings'].items(), key=lambda k: k[1])
        s['timings'] = {
            'total': now() - t0,
            'pages_total': sum([i[1] for i in pt]),
            'pages': pt,
        }
        with open(fw.fn_stats(), 'w') as fd:
            fd.write(json.dumps(s))
        fw.stats_out(s)
        tools.write_file(fw.fn_success(), str(now()))

    @classmethod
    def start_fg(fw):
        """We are in tmux now"""
        fw.clear_work_dir()
        if FLG.publish_all:
            return fw.start_publish_all_fg()

        app.info('watching for changes')
        do_org = FLG.file_watcher_org_publish_on_change
        do_md = FLG.file_watcher_md_rebbuild_on_change
        w = ''
        if do_org:
            w += ' -e org'
        if do_md:
            w += ' -e md'
        if not w:
            app.warn('Both watch modes disabled - not watching files')
            return
        f = '--follow' if FLG.file_watcher_follow_symlinks else ''
        get_files_cmd = "fd %s . 'src/markdown/' %s | " % (f, w)
        cmd = ['writeout () { echo "$0" ; } && ']  # % fw.fn_entr_comm_fifo()]
        cmd += ['export -f writeout; ']
        # cmd += ['while true; do ']
        cmd += [get_files_cmd]
        # -d: will exit at new file added:
        cmd += ['entr -dps writeout; sleep 0.1; ']
        # cmd += ['done ']
        cmd = ' '.join(cmd)
        t0 = now()
        while True:
            app.info('starting file monitor', cmd=cmd)
            p = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
            try:
                while True:
                    try:
                        line = p.stdout.readline().decode('utf-8').strip()
                        if not line:
                            app.info('entr restarts')
                            break
                    except KeyboardInterrupt:
                        app.warn('Keyboard Interrupt')

                        testfn = '/home/gk/docs/src/markdown/add/doom.d/docutools/docs/mkdocs/index.org'
                        fw.publish_org(testfn)
                        return
                    app.info('Changed file', fn=line)
                    if now() - t0 < 1:
                        # the build took a while, when there had been other changes
                        # we get them in a flush which we ignore:
                        app.info('Ignoring file', fn=line)
                        continue

                    if line.endswith('.org'):
                        # we le the md build but the rest we ignore for a second (see a few lines above)
                        line = fw.publish_org(line)
                    if line.endswith('.md'):
                        fw.rebuild_mkdocs(line)
                    else:
                        app.die('Unsupported monitor file')
                    t0 = now()
            finally:
                p.kill()

    @classmethod
    def publish_org(fw, fn):
        is_first = False if S.stats.get('cur') else True
        S.stats['cur'] = fn  # when something failed - where is why
        tmx = fw.tmemcs
        if not tmx:
            fw.tmemcs = tmx = tmux(session_name(), window_name='emacs_publisher')

        def send_lisp(stmt, wait_for=None, timeout=1, sleep=None, warnings_into=None):
            tmx.send_keys(' \\;', enter=None)
            tmx.wait_for('Eval:')
            tmx.send_keys(stmt)
            if not wait_for:
                return
            r = None
            if warnings_into is not None:
                r = {
                    'strings': FLG.publish_all_report_output_strings,
                    'into': warnings_into,
                }
            tmx.wait_for(wait_for, timeout=timeout, sleep=sleep, monitor=r)

        def init_setup_emacs(tmx):
            m = '(global-font-lock-mode 0)'  # syn hl off
            do(send_lisp, m)
            m = "(add-to-list '+format-on-save-enabled-modes 'markdown-mode t)"
            do(send_lisp, m, wait_for='(not ', timeout=10)
            tmx.send_keys(' :', enter=None)
            tmx.send_keys('view-echo-area-messages')

        def init_setup_org_roam(tmx, fn_db='/src/markdown/org-roam.db'):
            have_roam_db = lambda: exists(D() + fn_db)
            if have_roam_db():
                app.debug('already present', fn_db=fn_db)
                return
            app.info('building first time', fn_db=fn_db)
            do(send_lisp, '(org-roam-db-build-cache)', timeout=60)
            tools.wait_for('org-roam.db', lambda: have_roam_db(), timeout=60, sleep=0.5)

        if is_first:
            t0 = now()
            do(init_setup_emacs, tmx)
            do(init_setup_org_roam, tmx)
            app.info('emacs initted', dt=now() - t0)
        warnings_into = {}
        app.debug('publishing', fn=fn)
        bn = os.path.basename
        fn_md = fn.rsplit('.org', 1)[0] + '.md'
        md_st = lambda: os.stat(fn_md)[7] if exists(fn_md) else 0
        lsp = lambda l, w, t, s, r=warnings_into: do(
            send_lisp, l, wait_for=w, timeout=t, sleep=s, warnings_into=r
        )
        lsp('(org-link-open-from-string \\"[[%s]]\\")' % fn, bn(fn), 10, 0.1)
        t0 = now()
        lsp('(org-gfm-export-to-markdown)', bn(fn_md), 60, [0.1] * 10 + [0.5])
        dt = S.stats['timings'][fn] = now() - t0
        if warnings_into:
            S.stats['warnings'][fn] = {k: list(v) for k, v in warnings_into.items()}
        app.info('published', fn=fn, took='%.2f' % dt)
        return fn_md

    def rebuild_mkdocs(line):
        cmd = 'mkdocs build --dirty'
        app.info('Triggering mkdocs rebuild', cmd=cmd, changed_file=line)
        do(system, cmd)


def start_publishing_emacs():
    app.info('Starting emacs for publishing actions')
    cmd = 'cd "%s/src/markdown" && emacs -nw index.org' % D()
    do(S.tmux.new_window, 'emacs_publisher', cmd=cmd)


def start_live_server():
    app.info('Starting live server')
    FLG.server_browser = browsers.get(FLG.server_browser, FLG.server_browser)
    if FLG.server_no_browser:
        FLG.server_browser += ' --no-browser '
    cmd = FLG.server_cmd % tools.FlagsDict(FLG)
    do(S.tmux.new_window, 'live_server', cmd)
    # when site was deleted it will keep trying. No problem
    # tools.tmux.wait_for('Serving', timeout=2, window='live_server')


session_name = lambda: FLG.tmux_session_name % build_dirs_dict()


def run():
    tools.chdir_to_docs_root()
    FLG.tmux_session_name = session_name()
    do = tools.tdo
    if FLG.file_watcher_fg:
        return file_watcher.start_fg()
    if FLG.tmux_enter:
        return do(tools.tmux.enter_session)
    if FLG.tmux_cat_session_log:
        app.info('tmux session log', fnlog=file_watcher.fn_session_log())
        print(tools.read_file(file_watcher.fn_session_log(), dflt='n.a.'))
        return
    app.warn('Starting Dev Tmux Session'.upper(), dir=D())

    if FLG.publish_disable_lob_cache > 0:
        os.environ['disable_lob_cache'] = 'true'
    else:
        os.environ['disable_lob_cache'] = ''

    do(tools.export_mk_edit_base)
    S.tmux = do(tmux.new)

    if not FLG.file_watcher_disable:
        if FLG.publish_all or FLG.file_watcher_org_publish_on_change:
            do(start_publishing_emacs)
        do(file_watcher.start_in_tmux)

    if not FLG.server_disable:
        do(start_live_server)

    app.info('All services started', tmux_session_name=FLG.tmux_session_name)
    # tmux.send_keys('alias r=\\"cd $(pwd)\\"')
    # tmux.send_keys('cd src/markdown')

    if not FLG.tmux_attach:
        app.info('Not attaching to tmux')

    elif FLG.tmux_attach == 2:
        app.info('Attaching in a loop')
        # give the user time to say ctrl-c:
        while True:
            S.tmux.call('attach')
            system(' '.join(sys.argv))
    else:
        app.info('Attaching once')
        S.tmux.call('attach')
        if FLG.publish_all:
            fw = file_watcher
            fw.stats_out()
            if not exists(file_watcher.fn_success()):
                app.die('Missing success flag')
    app.info('tmux output in', fnlog=file_watcher.fn_session_log())
