"""
## Credits

Creates a Credits Page (using poetry lock file)

File: `<project root>/CREDITS.md`. Reference in docs like:

```bash
~/repos/docutools❯ cat docs/about/credits.md
\{\!CREDITS.md!}
```
(without the backslashes)

"""
from lcdoc.mkdocs.tools import MDPlugin, app
from lcdoc.tools import os, project, write_file
from lcdoc.mkdocs import markdown

TP = '''
|Package | Description | Version | License
|- | - | - | -
%s
'''
TC = '''
# Credits

Listed below all the python dependencies of _ME_

## Run Dependencies

_RD_

## Dev  Dependencies

_DD_

## Indirect Dependencies

_ID_


These projects were used to *build* _PN_

[`python`](https://www.python.org/) |
[`poetry`](https://poetry.eustace.io/) |
[`copier-poetry`](https://github.com/pawamoy/copier-poetry)

**Many thanks to all authors, for all these brilliant software packages!**


'''


import httpx


def fetch_pypi(pkg, attrs):

    app.info('from pypi', pkg=pkg)
    p = httpx.get('https://pypi.python.org/pypi/%s/json' % pkg)
    p = p.json()['info']
    p['home-page'] = p['home_page'] or p['project_url'] or p['package_url']
    p = {_: p[_] for _ in attrs}
    return p


from pip._internal.commands.show import search_packages_info  # noqa


def get_credits_data() -> dict:
    """
        Return data used to generate the credits file.

        Returns:
            Data required to render the credits template.
        """
    project_dir = project.root()
    # metadata = toml.load(project_dir + "/pyproject.toml")["tool"]["poetry"]

    lock_data = project.lock_data()
    project_name = project.name()

    direct_dependencies = {dep.lower() for dep in project.dependencies()}
    dev_dependencies = {dep.lower() for dep in project.dev_dependencies()}
    'python' in direct_dependencies and direct_dependencies.remove('python')
    indirect_dependencies = {pkg['name'].lower() for pkg in lock_data['package']}
    indirect_dependencies -= direct_dependencies
    indirect_dependencies -= dev_dependencies
    dependencies = direct_dependencies | dev_dependencies | indirect_dependencies
    app.info(
        'Generating credits',
        dependencies=dependencies,
        indirect_dependencies=indirect_dependencies,
    )

    packages = {}
    attrs = ('name', 'home-page', 'license', 'version', 'summary')
    for pkg in search_packages_info(dependencies):
        pkg = {_: pkg[_] for _ in attrs}
        packages[pkg['name'].lower()] = pkg
    ds = dependencies
    for dependency in dependencies:
        if dependency not in packages:
            pkg = fetch_pypi(dependency, attrs)
            packages[pkg['name'].lower()] = pkg
        else:
            app.debug('found', dependency=dependency)

    for d in indirect_dependencies:
        if not d in packages:
            app.warn('Not found in packages', dependency=d)
            continue
        packages[d]['for'] = [
            packages[k['name']]
            for k in lock_data['package']
            if d in k.get('dependencies', ())
        ]

    lnk = lambda p: '[`%(name)s`](%(home-page)s)' % p
    lico = lambda p: (p.get('license') or 'n.a.').replace('UNKNOWN', 'n.a.')

    def lic(p):
        l = lico(p)
        if l.startswith('http'):
            l = '[%s](%s)' % ((l + '///').split('/')[3], l)
        for k in 'license', 'License', 'version', 'Version':
            l = l.replace(k, '')
        return l

    def smry(p):
        s = p['summary']
        f = ' '.join([lnk(k) for k in p.get('for', ())])
        return s + ' ' + f

    def tbl(what, all=packages):
        ps = [packages[n] for n in what if n in packages]
        ps = [['', lnk(p), smry(p), p['version'], lic(p)] for p in ps]
        r = ['|'.join(l) for l in ps]
        return TP % '\n'.join(r)

    t = TC
    t = t.replace('_ME_', '`%s`' % project_name)
    t = t.replace('_RD_', tbl(sorted(direct_dependencies)))
    t = t.replace('_DD_', tbl(sorted(dev_dependencies)))
    t = t.replace('_ID_', tbl(sorted(indirect_dependencies)))
    t = t.replace('_PN_', project_name)
    return t


def create_credits_page(fncr, plugin, config):
    project.root(config)
    app.info('Regenerating', page=fncr)  # noqa: WPS421 (print)
    b = get_credits_data()
    app.info('writing', page=fncr)
    b = markdown.mark_auto_created(b)
    write_file(fncr, b)


class CreditsPlugin(MDPlugin):
    # config_scheme = (('commit_style', d), ('versioning', v))

    def on_pre_build(self, config):
        fn = project.root(config) + '/CREDITS.md'
        if os.path.exists(fn):
            if not os.environ.get('lcd_credits'):
                hint = '$lcd_credits=true: force rebuild'
                return app.info('No new credits page generated', hint=hint)
        create_credits_page(fn, self, config)
