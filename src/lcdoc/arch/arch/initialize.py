#!/usr/bin/env python
"""
Initialize a new mkdocs docu set

If you point to a dir with a .mkdocs.config it will patch the default yml with those.
"""
# edit from dir above this file then ide will resolve this:
from plugins import _tools as tools
from devapp.app import app
import os, sys, json
import yaml


# ------------------------------------------------------------------------------ config


class Flags(tools.DfltFlags):
    autoshort = ''

    class repos:
        n = 'Repos to include to "add" sources directory. Absolute or relative from $d_repos'
        d = ''
        t = list

    class link_templates:
        n = 'Link to the default templates instead of creating a new one. Only for doc source (this repo) development.'
        d = False

    class git_ignore_md_files:
        n = 'If you write exclusively .org this is practical for file browsing'
        d = False

    class force_build:
        n = 'Not asking for confirmations when interactive'
        d = False


main = lambda: tools.main(run, Flags)
FLG = tools.FLG
D = tools.D
do = tools.do
system = tools.system
exists = tools.exists

# ----------------------------------------------------------------------------- actions
def mk_dir_with_config():
    if exists(FLG.dir_docset + '/src'):
        app.warn('Already present', dir='src')
    cfg = tools.read_file(tools.fn_cfg(), dflt='')
    mkcfg = m = tools.read_file(D() + '/mkdocs.yml', dflt='')
    if not m:
        app.info('Found only initial mkdocs.yml')
        t = tools.fn_tmpl('mkdocs.yml')
        if FLG.link_templates:
            os.makedirs(D(), exist_ok=True)
            return tools.symlink(t, D() + '/mkdocs.yml')

        mkcfg = m = tools.read_file(tools.fn_tmpl('mkdocs.yml'))
    if cfg:
        Fubar = ': EXCLS__'
        m = m.replace(': !!', Fubar)
        m = yaml.safe_load(m)
        cfg = yaml.safe_load(cfg)
        cfg = tools.dict_merge(cfg, m)
        cfg = yaml.safe_dump(cfg)
        mkcfg = cfg.replace(Fubar, ': !!')
    tools.write_file(FLG.dir_docset + '/mkdocs.yml', mkcfg, mkdir=True)


def copy_init_src():
    frm = tools.d_installer_base + '/src'
    to = D() + '/src'
    fn = to + '/markdown/index.md'
    if exists(fn):
        return app.warn('Docu exists - skipping copying template sources', fn=fn)
    tools.tar_pipe(frm, to)


def link_repos():
    dr = D() + '/src/markdown/add'
    for r in FLG.repos:
        d = tools.full_path(r)
        if not exists(d):
            app.die('Not found', repo=d)
        s = d.rsplit('/', 1)[-1]
        # .dot files are not copied to site:
        if s.startswith('.'):
            s = s[1:]
        to_ = dr + '/' + s
        app.info('linking', repo=d, to_=to_)
        do(tools.symlink, frm=d, to=to_)


def copy_theme():
    dr = D() + '/theme'
    tools.tar_pipe(tools.d_installer_base + '/theme', dr)


def setup_git():
    dr = D()

    def add_gitignore(fn):
        if exists(fn):
            return app.warn('Already exists', fn=fn)
        ign = ['site', '*.pyc', '*.pyo', '__pycache__/', '*org-roam.db']
        if FLG.git_ignore_md_files:
            ign.append('*.md')
        with open(fn, 'w') as fd:
            fd.write('\n'.join(ign))

    if exists(dr + '/.git'):
        return app.warn('Git already present - wont create/commit', dir=dr + '/.git')
    do(system, 'git init "%s"' % dr)
    do(add_gitignore, dr + '/.gitignore')
    for fn in ['.gitignore', 'src', 'mkdocs.yml']:
        do(system, 'git add "%s"' % fn)
    do(system, 'git commit -am "Initial commit (by docuset builder)"')


# def setup_org_export():
#     return
#     t = tools.fn_tmpl('org_publish.el')
#     to = D() + '/.org_publish.el'
#     if exists(to):
#         return app.warn('skipping existing', file=to)
#     if FLG.link_templates:
#         return tools.symlink(t, to)
#     do(system, 'cp "%s" "%s"' % (t, to))


# org-protocol://roam-file?file=%2Ftmp%2Fset%2Fsrc%2Fmarkdown%2Findex.org
def setup_org_roam(check_roam_db=False):
    d_src = D() + '/src/markdown'
    fn = d_src + '/.dir-locals.el'
    if exists(fn):
        app.info('skipping existing', dir_locals=fn)
    else:
        t = tools.read_file(tools.fn_tmpl('dir-locals.el'))
        t = t.replace('_D_', D())
        tools.write_file(fn, t)


def build_docs():
    dr = D()
    do(system, '%s build' % sys.argv[0])


def final_messages():
    """
    Docset is built - ready to document!

    Next you normally do "%s dev" to start the dev services

    - Edit the mkdocs.yml for structure.
    - Check the docu (included in your build) for how to configure the browser
      links in order to open the editor on docu clicks
    """
    m = (final_messages.__doc__ % sys.argv[0]).replace('\n    ', '\n')
    m = '\n%s\n%s\n' % ('-' * 60, m)
    app.info(m)


# ----------------------------------------------------------------------------- Pipline
def run():
    m = 'Initializing new'
    if tools.exists(D() + '/mkdocs.yml'):
        m = 'Updating'

    app.warn((m + ' Doc Set').upper(), dir=D())
    if not FLG.force_build:
        if sys.stdin.isatty():
            if input('ok [y|NQ]? ').lower() != 'y':
                app.die('Unconfirmed')
        else:
            app.die('Non interactive requires force_build flag set')
    # add docs repo:
    d = tools.dir_of(tools.d_installer_base, up=1)
    assert '.git' in os.listdir(d), '.git not found in ' + d
    FLG.repos.append(d)
    do = tools.tdo
    do(mk_dir_with_config)
    FLG.dir_docset = D()
    os.chdir(D())
    do(copy_init_src)
    do(link_repos)
    do(copy_theme)
    # do(setup_org_export)
    do(setup_git)
    do(setup_org_roam)
    do(build_docs)
    do(final_messages)
