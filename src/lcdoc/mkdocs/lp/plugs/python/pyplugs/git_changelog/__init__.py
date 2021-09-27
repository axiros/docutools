"""
## Changelog

Creates CHANGELOG.md (using git-changelog)

File: `<project root>/CHANGELOG.md`. Reference in docs like:

```bash
~/repos/docutools❯ cat docs/about/changelog.md
\{\!CHANGELOG.md!}
```

(without the backslashes)


### Templates

Links default jinja templates over to docs/lcd/changelog.
In order to use your own, overwrite that directory.


### Config

```python
    style      = Choice(['angular', 'basic', 'atom'], default='angular')
    versioning = Choice(['auto', 'semver', 'calver'], default='auto')
```

when set to auto we derive by inspecting your last git tag - if like X.foo.bar with X a
number > 2000 we set to calver.

You can set $versioning also via environ, which will have precedence then.

"""
import shutil

from mkdocs.config import config_options

import lcdoc
from lcdoc.mkdocs import markdown
from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import MDPlugin, app, link_assets
from lcdoc.tools import dirname, os, project, read_file, write_file

config, page, Session, lpkw = (python.config, python.page, python.Session, python.lpkw)

formatted = True


def gen_change_log(d_assets, versioning_scheme, commit_style):
    """
    Problem: The git-changelog cmd uses Jinja and wants .md
    mkdocs macros also, different contexts though -> crash.
    So we cannot have .md sources in the docs folder -> have to change on the fly when
    using git-changelog. Here we do that. Also we dyn set the versioning message.
    """
    dr = project.root(config())
    d, dtmp = (dirname, dr + '/build/git_changelog_tmpl')

    def set_version_scheme(fn, ver):
        # todo: do it in jinaja in the template itself:
        CV = 'This project adheres to [CalVer Versioning](http://calver.org) '
        CV += '![](https://img.shields.io/badge/calver-YYYY.M.D-22bfda.svg).'
        SV = 'This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).'
        VSM = CV if ver == 'calver' else SV
        s = read_file(fn).replace('_VERSION_SCHEME_MSG_', VSM)
        write_file(fn, s)

    dcl = d_assets + '/keepachangelog'
    os.makedirs(dtmp, exist_ok=True)
    ver = versioning_scheme
    if ver == 'auto':
        hint = 'export $versioning or set "versioning" in mkdocs plugin config '
        hint += 'to calver or semver'
        gt = os.popen('cd "%s" && git tag | tail -n 1' % dr).read().strip()
        if not gt:
            app.die('Cannot derive versioning scheme, no git tags yet', hint=hint)
        ver = 'semver'
        try:
            if int(gt.split('.', 1)[0]) > 2000:
                ver = 'calver'
        except:
            pass
        app.info('Versioning derived from git tags', versioning=ver)

    # '/home/gk/repos/docutools/docs/lcd/git_changelog/keepachangelog'
    for k in os.listdir(dcl):
        fn = dtmp + '/' + k.replace('.tmpl', '')
        shutil.copyfile(dcl + '/' + k, fn)
        if k == 'changelog.md.tmpl':
            set_version_scheme(fn, ver)
    cmd = 'cd "%s"; git-changelog -s %s -t "path:%s" .'
    cmd = cmd % (dr, commit_style, dtmp)
    cl = os.popen(cmd).read()
    if not cl:
        app.die('changelog creation failed', cmd=cmd)
    app.info('changelog created')
    return cl


def register(fmts):
    fmts['git_changelog'] = make_changelog


def g(key, dflt, *l):
    for d in l:
        v = d.get(key)
        if v:
            return v
    return dflt


def make_changelog(s, **show_kw):
    l = (show_kw, lpkw(), os.environ)
    style = g('commit_style', 'angular', *l)
    ver = g('versioning', 'semver', *l)
    d_assets = link_assets(python, __file__, config())
    os.system('ls docs/lcd/git_changelog')

    r = gen_change_log(d_assets, ver, style)
    return r
