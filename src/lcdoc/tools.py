"""
Common tools for all modules

"""
import collections
import hashlib
import json
import os
import socket
import sys
import time

import toml

from lcdoc.log import app, now

exists = os.path.exists

# fastest algo:
def file_hash(fn, algo='blake2b'):
    return getattr(hashlib, algo)(open(fn, 'rb').read()).hexdigest()


def dirname(fn, create=False):
    d = os.path.dirname(fn)
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def require(cmd, name=None, die=True, _have=set()):
    '''cmd e.g. "rg --version"'''
    name = name or cmd.split(' ', 1)[0]
    if cmd in _have:
        return True
    if os.system(cmd + ' >/dev/null') == 0:
        _have.add(cmd)
        return True

    msg = 'Missing required command: %s' % name
    if die:
        app.die(msg, tried=cmd)
    else:
        app.warning(msg, tried=cmd)
        return False


def hostname(c=[0]):
    i = c[0]
    if i:
        return i
    c[0] = socket.gethostname()
    return c[0]


def into(d, k, v):
    """the return is important for e.g. rx"""
    d[k] = v
    return d


def to_list(o):
    o = [] if o is None else o
    t = type(o)
    return o if t == list else list(o) if t == tuple else [o]


# ----------------------------------------------------------------------------- file ops
def walk_dir(directory, crit=None):
    crit = (lambda *a: True) if crit is None else crit
    files = []
    j = os.path.join
    for (dirpath, dirnames, filenames) in os.walk(directory):
        files += [j(dirpath, file) for file in filenames if crit(dirpath, file)]
    return files


def read_file(fn, dflt=None, bytes=-1, strip_comments=False):
    """
    API function.
    read a file - return a default if it does not exist"""
    if not exists(fn):
        if dflt is not None:
            return dflt
        raise Exception(fn, 'does not exist')
    with open(fn) as fd:
        # no idea why but __etc__hostname always contains a linesep at end
        # not present in source => rstrip(), hope this does not break templs
        res = fd.read(bytes)
        res = res if not res.endswith('\n') else res[:-1]
        if strip_comments:
            lines = res.splitlines()
            res = '\n'.join([l for l in lines if not l.startswith('#')])
        return res


def insert_file(fn, content, sep):
    s = read_file(fn).split(sep)
    if not len(s) == 3:
        raise Exception(f'No 2 times occurrance of sep in file. sep: {sep}, fn: {fn}')
    write_file(fn, s[0] + sep + content + sep + s[2])


def write_file(fn, s, log=0, mkdir=0, chmod=None, mode='w', only_on_change=False):
    'API: Write a file. chmod e.g. 0o755 (as octal integer)'

    fn = os.path.abspath(fn)

    if isinstance(s, (list, tuple)):
        s = '\n'.join(s)
    if only_on_change:
        so = read_file(fn, dflt='xxx')
        if s == so:
            return

    if log > 0:
        app.info('Writing file', fn=fn)
    if log > 1:
        sep = '\n----------------------\n'
        ps = (
            s
            if not 'key' in fn and not 'assw' in fn and not 'ecret' in fn
            else '<hidden>'
        )
        app.debug('Content', content=sep + ps + sep[:-1])
    e = None
    while True:
        try:
            with open(fn, mode) as fd:
                fd.write(str(s))
            if chmod:
                if not isinstance(chmod, (list, tuple)):
                    chmod = [int(chmod)]
                for s in chmod:
                    os.chmod(fn, s)
            return fn
        except IOError as ex:
            if mkdir:
                mkdir = 0
                d = os.path.dirname(fn)
                os.makedirs(d)
                continue
            e = ex
        except Exception as ex:
            e = ex
        app.die('Could not write file', filename=fn, exc=e)


have_tty = lambda: sys.stdin.isatty() and sys.stdout.isatty()


def flatten(d, sep='_', tpljoin=None):
    """when tpljoin is given we detect them as keys and join
    (enables json serialization)"""

    obj = collections.OrderedDict()

    def recurse(t, parent_key=''):

        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                if isinstance(k, tuple):
                    k = tpljoin.join(k)
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t

    recurse(d)

    return obj


class project:
    """loads the project config

    Main app config put into project.cfg['app']
    An optional tool.lc.app section will be merged into that

    TODO: other formats than pyproject.toml

    """

    config, dir_home, fn_cfg = {}, None, None

    def root(config=None, root=None, c=[0]):
        # config maybe given. Understood currently: mkdocs config
        if root is not None:
            c[0] = root  # for tests, to force it
        if c[0]:
            return c[0]
        ret = 0
        try:
            if config and hasattr(config, '__getitem__'):
                dd = config.get('docs_dir')
                if dd:
                    ret = dirname(dd)
                    return ret
            # todo: look at git here
            raise Exception('Cannot derive project root')
        finally:
            c[0] = ret

    fn_config = lambda: project.root() + '/pyproject.toml'
    d_autodocs = lambda: project.root() + '/build/autodocs'

    def abs_path(fn, config=None, mkdirs=False):
        r = project.root(config)
        if not fn:
            return r
        if fn[0] != '/':
            fn = r + '/' + fn
        if mkdirs:
            os.makedirs(dirname(fn), exist_ok=True)
        return fn

    # TODO: understand also poetry and piptools:
    def load_config():

        fn = project.fn_config()
        if not exists(fn):
            app.die('no config found', fn=fn)

        cfg = toml.load(fn)
        app.info('loaded config', filename=fn)
        c = project.config
        c.update(cfg)
        if not 'project' in c:
            c['project'] = {'urls': {}}
        if 'tool' in c and 'poetry' in c['tool']:
            c['project'].update(c['tool']['poetry'])
            c['project']['urls']['homepage'] = c['project']['homepage']
            c['project']['urls']['repository'] = c['project']['repository']

        t = cfg['tool']
        # breakpoint()  # FIXME BREAKPOINT
        # c['app'] = t['poetry']
        # c['app'].update(t.get('lc', {}).get('app', {}))
        project.fn_cfg = fn
        # app.die('Did not find a pyproject.toml file with badges declared')
        return project.config

    def conf():
        return project.config or project.load_config()

    def name():
        p = project.conf()
        return p['project']['name']

    def urls():
        p = project.conf()['project']
        if 'urls' in p:
            return p['urls']
        urls = 'packagehome', 'discusshome', 'homepage', 'repository'
        return {k: p.get(k, '') for k in urls}

    def homepage():
        return project.urls().get('homepage', 'n.a.')

    def repository():
        return project.urls().get('repository', 'n.a.')

    def packagehome():
        return (
            project.urls().get('packagehome')
            or 'https://pypi.org/project/%s/_VERSION_/' % project.name()
        ).replace('_VERSION_', project.version())

    def version():
        p = project.conf()['project']
        v = p['version']
        if isinstance(v, dict) and v.get('use_scm'):
            raise NotImplemented('currently only poetry')
            # from pdm.pep517.scm import get_version_from_scm
            # v = get_version_from_scm(project.root())
        return str(v)

    def dependencies():
        d = project.conf()['project']['dependencies']
        if isinstance(d, dict):
            # poetry:
            return d
        # pdm (pep)
        return parse_deps(d)

    def dev_dependencies():
        p = project.conf()['project']
        dd = p.get('dev-dependencies')
        if dd:
            if isinstance(dd, dict):
                # poetry - already dict:
                return dd
            return parse_deps(dd)

        r = [
            l
            for k in project.conf()['tool']['pdm']['dev-dependencies'].values()
            for l in k
        ]
        return parse_deps(r)

    def lock_data():
        fn = []
        for k in 'pdm', 'poetry':
            fn.insert(0, project.root() + '/%s.lock' % k)
            if exists(fn[0]):
                return toml.load(fn[0])
        app.die('No lock file in root', fn)


def parse_deps(deplist, seps='~<>!= '):
    m = {}
    for dep in deplist:
        h = False
        for s in seps:
            if s in dep:
                l = dep.split(s, 1)
                m[l[0]] = (s + l[1]).strip()
                h = True
                break
        if not h:
            m[dep] = ''
    return m
