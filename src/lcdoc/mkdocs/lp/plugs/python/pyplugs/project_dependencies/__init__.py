import httpx
from pip._internal.commands.show import search_packages_info

from lcdoc.mkdocs import markdown
from lcdoc.mkdocs.lp.plugs import python
from lcdoc.tools import app, os, project, write_file

config, page, Session = (python.config, python.page, python.Session)

TP = '''
|Package | Description | Version | License
|- | - | - | -
%s
'''
TC = '''

## Run Dependencies

_RD_

## Development Dependencies

_DD_

## Indirect Dependencies

_ID_

**Many thanks to all authors, for all these brilliant software packages!**


'''


def fetch_pypi(pkg, attrs):

    app.info('from pypi', pkg=pkg)
    p = httpx.get('https://pypi.python.org/pypi/%s/json' % pkg)
    p = p.json()['info']
    p['home-page'] = p['home_page'] or p['project_url'] or p['package_url']
    p = {_: p[_] for _ in attrs}
    return p


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
    direct_deps = {dep.lower() for dep in project.dependencies()}
    dev_deps = {dep.lower() for dep in project.dev_dependencies()}
    'python' in direct_deps and direct_deps.remove('python')
    indirect_deps = {pkg['name'].lower() for pkg in lock_data['package']}
    indirect_deps -= direct_deps
    indirect_deps -= dev_deps
    deps = sorted(direct_deps | dev_deps | indirect_deps)
    app.info(
        'Generating credits', deps=deps, indirect_deps=indirect_deps,
    )

    packages = {}
    attrs = ('name', 'home-page', 'license', 'version', 'summary')
    # pip changed from dict to instance with 21.2.0:
    g = lambda o, n: o[n] if isinstance(o, dict) else getattr(o, n.replace('-', ''))

    for pkg in search_packages_info(deps):
        pkg = {_: g(pkg, _) for _ in attrs}
        app.level < 20 and app.debug('pkg', json=pkg)
        packages[pkg['name'].lower()] = pkg

    for dep in deps:
        if dep not in packages:
            pkg = fetch_pypi(dep, attrs)
            packages[pkg['name'].lower()] = pkg
        else:
            app.debug('found', dep=dep)

    for d in sorted(indirect_deps):
        if not d in packages:
            app.warning('Not found in packages', dep=d)
            continue
        packages[d]['for'] = [
            packages[k['name']] for k in lock_data['package'] if d in k.get('deps', ())
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
    t = t.replace('_RD_', tbl(sorted(direct_deps)))
    t = t.replace('_DD_', tbl(sorted(dev_deps)))
    t = t.replace('_ID_', tbl(sorted(indirect_deps)))
    t = t.replace('_PN_', project_name)
    return t


def register(fmts):
    fmts['project_dependencies'] = render_deps


def render_deps(s, **kw):
    project.root(config())
    app.info('Regenerating dependencies')
    r = get_credits_data()
    return r
