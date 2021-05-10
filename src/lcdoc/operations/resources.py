from devapp.tools import exists, write_file, read_file, abspath, os, project, os
from devapp.app import app, system, do

environ = os.environ


class emacs:
    def rdp(rsc):
        root = project.root()
        DOOMDIR = root + '/cfg/doom'
        prof_name = project.root().rsplit('/', 1)[1].strip()
        # d = abspath(rsc.path + '/../')
        dde = root + '/build/doom_dot_emacs'
        return root, DOOMDIR, prof_name, dde

    def emacs(rsc, **kw):
        root, DOOMDIR, prof_name, dde = emacs.rdp(rsc)
        return {
            'cmd_pre': 'export DOOMDIR="%s"; ' % DOOMDIR,
            'cmd': 'emacs --with-profile "%s"' % prof_name,
        }

    def doom(rsc, **kw):
        root, DOOMDIR, prof_name, dde = emacs.rdp(rsc)
        return {
            'cmd_pre': 'export DOOMDIR="%s"; ' % DOOMDIR,
            'cmd': ':' + dde + '/bin/doom',
        }

    def doom_install(rsc, install=False, verify=False, api=None, **kw):
        helpme = 'https://github.com/hlissner/doom-emacs/blob/develop/docs/getting_started.org#install-doom-alongside-other-configs-with-chemacs'

        root, DOOMDIR, prof_name, dde = emacs.rdp(rsc)
        if verify:
            fn = DOOMDIR + '/init.el'
            if (
                exists(fn)
                and exists(root + '/bin/doom')
                and exists(root + '/bin/emacs')
                and exists(dde)
            ):
                app.info('doom installed', exists=fn)
                return True
            return False
        if not install:
            return
        app.info('Installing doom...')
        H = environ.get('HOME')
        fnprofs = H + '/.emacs-profiles.el'

        if not exists(fnprofs):
            if exists(H + '/.emacs'):
                app.die(
                    'you have .emacs but not .emacs-profiles.el in your home - confusing me',
                    hint='install chemacs properly',
                    see=helpme,
                )
            app.info('downloading chemacs for multiprofile mgmt')
            c = 'wget -O ~/.emacs https://raw.githubusercontent.com/plexus/chemacs/master/.emacs'
            do(system, c)
            ed = H + '/.emacs.d'
            if exists(ed):
                edn = H + '/.emacs.d.default'
                if not os.listdir(ed):
                    # emacs autocreated - in the way for chemacs
                    do(system, 'rm -f "%s"' % ed)
                app.info(
                    'moving existing emacs to chemacs default profile',
                    frm_dir=ed,
                    to_dir=edn,
                )
                do(system, 'mv "%s" "%s"' % (ed, edn))
                P = '( ("default"   . ((user-emacs-directory . "~/.emacs.default"))))'
                write_file(fnprofs, P)

        p = read_file(fnprofs)
        if '"%s"' % prof_name in p:
            msg = 'Profile name already configured in chemacs - leaving'
            app.warn(msg, name=prof_name, found_in=fnprofs)
        else:
            p = p.rsplit(')', 1)[0]
            _ = '''\n  ("%s"   . ((user-emacs-directory . "%s"))) )'''
            p += _ % (prof_name, dde)
            write_file(fnprofs, p)
        app.info('profiles content', content=p)

        cmd = 'git clone --depth 1 https://github.com/hlissner/doom-emacs "%s"' % dde

        if not exists(dde):
            do(system, cmd)
        os.chdir(dde)
        os.makedirs(DOOMDIR, exist_ok=True)
        # this is the config - ready to modify and doom will be recreatable alone from that:
        # via doom sync
        cmd = 'export DOOMDIR="%s"; bin/doom -y install' % DOOMDIR
        do(system, cmd)


class rsc:
    class emacs:
        n = 'Doom Emacs - set up 100% self contained within conda env - except one profile switcher in HOME.'
        n += 'E.g. for org file based documentation generation.'
        d = True
        cmd = emacs.emacs
        pkg = 'emacs'
        provides = emacs.doom
        post_inst = emacs.doom_install

    class graph_easy:
        n = 'Flow plotting library for terminal and svg'
        d = False
        cmd = 'graph-easy'
        pkg = 'perl(Graph::Easy)'
        conda_inst = ' && '.join(
            [
                'conda install -y -c bioconda perl-app-cpanminus ',
                'env PERL5LIB="" PERL_LOCAL_LIB_ROOT="" PERL_MM_OPT="" PERL_MB_OPT="" cpanm Graph::Easy::As_svg',
            ]
        )
