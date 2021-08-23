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
from lcdoc.mkdocs.tools import MDPlugin, app, link_assets
from lcdoc.tools import dirname, os, project, read_file, write_file
from lcdoc.mkdocs import markdown


def gen_change_log(fncl, plugin, config):
    """
    Problem: The git-changelog cmd uses Jinja and wants .md sources.
    mkdocs macros also, different contexts though -> crash.
    So we cannot have .md sources in the docs folder -> have to change on the fly when
    using git-changelog. Here we do that. Also we dyn set the versioning message.
    """
    dr, d, dtmp = project.root(), dirname, project.root() + '/tmp/changelog_tmpl'

    def set_version_scheme(fn, ver):
        # todo: do it in jinaja in the template itself:
        CV = 'This project adheres to [CalVer Versioning](http://calver.org) '
        CV += '![](https://img.shields.io/badge/calver-YYYY.M.D-22bfda.svg).'
        SV = 'This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).'
        VSM = CV if ver == 'calver' else SV
        s = read_file(fn).replace('_VERSION_SCHEME_MSG_', VSM)
        write_file(fn, s)

    dcl = plugin.d_assets + '/keepachangelog'
    os.makedirs(dtmp, exist_ok=True)
    ver = os.environ.get('versioning') or plugin.config['versioning']
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

    for k in os.listdir(dcl):
        fn = dtmp + '/' + k.replace('.tmpl', '')
        shutil.copyfile(dcl + '/' + k, fn)
        if k == 'changelog.md.tmpl':
            set_version_scheme(fn, ver)
    cmd = 'cd "%s"; git-changelog -s %s -t "path:%s" . > "%s"'
    cmd = cmd % (dr, plugin.config['commit_style'], dtmp, fncl)
    err = os.system(cmd)
    if err:
        app.die('changelog creation failed', fn=dcl, cmd=cmd)
    markdown.mark_auto_created(fncl)
    app.info('changelog created')


class ChangeLogPlugin(MDPlugin):
    d = config_options.Choice(['angular', 'basic', 'atom'], default='angular')
    v = config_options.Choice(['auto', 'semver', 'calver'], default='auto')
    config_scheme = (('commit_style', d), ('versioning', v))

    def on_pre_build(self, config):
        link_assets(self, __file__, config)
        fn = project.root(config) + '/CHANGELOG.md'
        if os.path.exists(fn):
            if not os.environ.get('lcd_changelog'):
                hint = '$lcd_changelog=true: force rebuild'
                return app.info('No new changelog generated', hint=hint)
        gen_change_log(fn, self, config)
