#!/usr/bin/env python
"""
Creating The Repo Badges SVGs

Run by CI after tests and coverage, outputs SVGs into public docu dir or pushes them to
a public repo.
"""

import os
from functools import partial

import anybadge as ab
from devapp.app import app, do, run_app, system
from devapp.tools import FLG, project, dirname, exists, repl_dollar_var_with_env_val


class Flags:
    autoshort = ''

    class badges:
        """
        Requirements:
        - pypi: cfg:packagehome,e.g. in [tool.lc.app]
        - discuss: cfg:discuss
        - pipeline: cfg:repository
        - coverage: must have been run and cmd_coverage_report must deliver report
        """

        # TODO: list output not perfect at -hf:
        n = 'badges to create'
        d = [
            'documentation',
            'pypi_package',
            'discuss',
            'pipeline',
            'coverage',
            'statements',
            'code_style_ax_black',
        ]

    class badge_directory:
        """repo urls like: hg+https://...::<workdir>"""

        n = 'repo url, absolute path or relative to project root, colon sepped by link path prefix'
        d = 'public/img::img'

    class cmd_coverage_report:
        d = 'cat build/coverage_report'

    class modify_readme:
        n = 'write the badges into README.md and commit it'
        d = False

    class modify_index:
        """sometimes you want them here"""

        n = 'write the badges into docs/index.md and commit it'
        d = False

    class ignore_errors:
        n = 'exit 1 if any declard badge cannot be created'
        d = True

    class print_out:
        n = 'print markdown on exit'
        d = True


# --------------------------------------------------------------------- tools/  actions


class Repo:
    """Functions for when we are storing the badges externally in a repo"""

    def prepare_hg(repo, workdir):
        if repo.startswith('hg+'):
            repo = repo[3:]
        S.repo_url = repo
        if not exists(workdir):
            os.makedirs(dirname(workdir), exist_ok=True)
            do(system, 'hg clone "%s" "%s"' % (repo, workdir))
        else:
            do(system, 'cd "%s" && hg pull -u' % workdir)
        d = workdir + '/%s' % project.name()
        os.makedirs(d, exist_ok=True)
        return d

    def commit_and_push_if_repo():
        if not S.repo_url:
            return app.info('no repo backing of badges')
        rev = os.popen('git rev-parse --short HEAD').read().strip()
        d = project.name(), rev
        cmd = (
            "cd '%s'" % S.dest_dir,
            'hg addremove',
            "hg commit -m '%s:%s'; hg push; echo done" % d,
        )
        app.info('pushing', json=cmd)
        do(system, ' && '.join(cmd))
        ver = os.popen(cmd[0] + ' && hg identify').read().strip()
        ver = ver.split()[0]
        # https://badges.github.com/scm/hg/noauth/badges/raw-file/a07460beee0f/docutools/discuss.svg
        u = '%s/raw-file/%s/%s'
        u = u % (S.repo_url, ver, project.name())
        S.repo_badges_base_url = u
        app.info('base url for badges', url=u)


def make_directory(dir):
    pre, post = dir.split('::')
    if pre.startswith('hg+'):
        S.dest_dir = do(Repo.prepare_hg, repo=pre, workdir=post)
    else:
        dir, S.d_link_prefix = pre, post
        if not dir.startswith('/'):
            dir = os.path.join(project.root(), dir)
        S.dest_dir = dir
        os.makedirs(S.dest_dir, exist_ok=True)
    app.info('dest dir', dir=S.dest_dir)


class S:
    repo_url = None
    dest_dir = None
    markdown = []
    markdown_refs = []
    d_link_prefix = ''
    coverage_report = ''
    repo_badges_base_url = None


def read_cov_report():
    r = S.coverage_report
    if not r:
        cmd = 'cd "%s" && %s' % (project.root(), FLG.cmd_coverage_report)
        app.debug('getting coverage', cmd=cmd)
        r = S.coverage_report = os.popen(cmd).read()
    return r


def make_badge(fn, label, value, link, color, **kw):
    if not link:
        return app.warn('skipping - no link', badge=label)
    p = partial(ab.Badge, label=label, value=value, text_color='white')

    if not isinstance(color, dict):
        badge = p(default_color=color)
    else:
        badge = p(thresholds=color)
    do(badge.write_badge, file_path=fn, overwrite=True)
    il = app_cfg('homepage') + '/' + os.path.join(S.d_link_prefix, os.path.basename(fn))
    S.markdown_refs += ['[lnk_%s]: %s' % (label, link)]
    S.markdown_refs += ['[img_%s]: %s' % (label, il)]
    S.markdown += ['[![%s][img_%s]][lnk_%s]' % (label, label, label)]


class Badges:
    def documentation(fn):
        label, value, link = 'docs', app_cfg('name'), app_cfg('homepage')
        color = 'purple'
        do(make_badge, **locals())

    def pypi_package(fn):
        loc = app_cfg('packagehome')
        p = 'pypi package' if loc.startswith('https://pypi.org') else 'package'
        label, value, color = p, app_cfg('version'), '#8bd124'
        link = loc.replace('_VERSION_', app_cfg('version'))
        do(make_badge, **locals())

    def discuss(fn):
        label, value, color = ('discuss', 'skype', '#0078d4')
        link = 'https://join.skype.com/krSNYZqvEmJm'
        do(make_badge, **locals())

    def pipeline(fn):
        # we only get to here when tests finished.
        # The failing ones you'll see as repo badge, outside the markdown
        label, value, color = 'pipeline', 'passed', 'green'
        link = app_cfg('repository') + '/-/commits/master'
        do(make_badge, **locals())

    def coverage(fn, statements=False):
        s = statements
        r = do(read_cov_report)
        if not r:
            return (app.warn if FLG.ignore_errors else app.die)('no coverage report')
        r = r.rsplit('TOTAL', 1)[-1].split()[0 if s else -1]
        value = float(r[:-1]) if not s else r
        label = s['t'] if s else 'coverage'
        color = s['c'] if s else {20: 'red', 50: 'orange', 80: 'yellow', 100: 'green'}
        link = app_cfg('homepage') + '/coverage/index.html'
        do(make_badge, **locals())

    def statements(fn):
        Badges.coverage(fn, statements={'t': 'statements', 'c': 'blue'})

    def code_style_ax_black(fn):
        do(
            make_badge,
            fn,
            'code style',
            'axblack',
            'https://github.com/axiros/axblack',
            '#222222',
        )


def app_cfg(k):
    return getattr(project, k)()


modify_readme = lambda: modify_container_md(project.root() + '/README.md')
modify_index = lambda: modify_container_md(project.root() + '/docs/index.md')


md_sep = '<p attr="autogenerated by make_badges"></p>'


def modify_container_md(fn):
    with open(fn) as fd:
        md = md_orig = fd.read()
    s = md_txt_pre_code = md.split('```', 1)[0]

    if not '\n# ' in s and not s.startswith('# '):
        md = '# This package\n' + md
    l = md.split(md_sep, 2)
    if len(l) == 1:
        parts = ('\n' + md).split('\n# ', 1)
        parts[0] += '\n# '
        fh = parts[1].split('\n', 1)
        s = '''%s %s

%s

%s

        '''
        s = s % (parts[0].lstrip(), fh[0], gen_markdown(), fh[1],)
    else:
        pre, _, post = l
        s = pre + gen_markdown() + post
    if s == md_orig:
        return app.info('make_badges: no change')
    with open(fn, 'w') as fd:
        fd.write(s)
    cmd = 'git commit "%s" -m "docs: autogenerated badges" %s'
    for u, nf in (('', False), ('--author "%(USER)s"; echo true' % os.environ, True)):
        # noail since on CI we can't push anyway but dont' want to fail after a fine build.
        # docu build will have the change:
        do(system, cmd % (fn, u), no_fail=True)
    app.warn('have modified container markdown page', fn=fn)


def gen_markdown():
    if S.repo_badges_base_url:

        def replace(i, sep=']: '):
            if not i.startswith('[img_') or S.repo_badges_base_url in i:
                return i
            pre, post = i.split(sep, 1)
            post = S.repo_badges_base_url + '/' + post.rsplit('/', 1)[-1]
            return pre + sep + post

        S.markdown_refs = [replace(i) for i in S.markdown_refs]

    r = []
    _ = r.append
    _(md_sep)
    _('')
    _('&nbsp; '.join(S.markdown))
    _('')
    _('\n'.join(S.markdown_refs))
    _('')
    _(md_sep)
    return '\n'.join(r)


# ------------------------------------------------------------------------- end actions
def run():
    project.load_config()
    d = repl_dollar_var_with_env_val(FLG.badge_directory)
    make_directory(dir=d)
    # make_directory(dir=d)
    # do(make_directory, dir=FLG.badge_directory)
    for k in FLG.badges:
        try:
            do(getattr(Badges, k), fn=S.dest_dir + '/%s.svg' % k)
        except Exception as ex:
            if FLG.fail_on_error:
                raise
            app.error('Could not build', badge=k, exc=ex)
    do(Repo.commit_and_push_if_repo)
    if FLG.print_out:
        app.info(
            'printing markdown', json={'links': S.markdown, 'refs': S.markdown_refs}
        )
        print('')
        print(gen_markdown())

    do(modify_readme) if FLG.modify_readme else 0
    do(modify_index) if FLG.modify_index else 0


main = partial(run_app, run, flags=Flags)
