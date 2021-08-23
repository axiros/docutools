from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import log as mkdlog

from lcdoc.const import PageStats, Stats
from lcdoc.tools import app, dirname, exists, now, os


def theme_dir(config):
    """strangly we don't see custom_dir in config.theme - it only inserts it, when given, into config.theme.dirs
    """
    cd = config['theme'].dirs[0]
    if cd.endswith('/' + config['theme'].name):
        app.debug('Theme dir is docs dir')
        return config['docs_dir']
    app.info('Theme dir is custom', dir=cd)
    return cd


def link_assets(plugin, fn_plugin, config):
    """Linking assets folder content into D/lcd/<pluginname>, where D is either docs dir or custom_dir
    Setting plugin.d_assets to that folder.
    """
    # extra css and js has be in docs dir, even with custom dir:
    d = dirname(fn_plugin) + '/assets'
    if not exists(d):
        app.die('Cannot link: No assets found', dir=d)
    n = fn_plugin.rsplit('/', 2)[-2]
    to = config['docs_dir'] + '/lcd'
    t = to + '/' + n
    plugin.d_assets = t
    if exists(t):
        return app.debug('Exists already', linkdest=t)
    app.warning('Linking', frm=d, to=t)
    os.makedirs(dirname(t), exist_ok=True)
    cmd = 'ln -s "%s" "%s"' % (d, t)
    if os.system(cmd):
        app.die('Could not link assets')


def split_off_fenced_blocks(markdown, fc_crit=None, fc_process=None, fcb='```'):
    fc_crit = (lambda s: True) if fc_crit is None else fc_crit
    lines = markdown.splitlines()
    mds, fcs = [[]], []
    while lines:
        l = lines.pop(0)
        ls = l.lstrip()
        if not ls.startswith(fcb) or not fc_crit(ls):
            mds[-1].append(l)
            continue

        fc = []
        mds.append([])
        beg = (' ' * (len(l) - len(l.lstrip()))) + fcb
        fc.append(l)
        while lines:
            l = lines.pop(0)
            fc.append(l)
            if l.startswith(beg):
                break
        if not lines:
            msg = 'Closing fenced block. Your markdown will not be correctly rendered'
            app.warn(msg, block=fc)
            fc.append(beg)
        if fc_process:
            fc = fc_process(fc)
        fcs.append(fc)
    return mds, fcs


hooks = [
    'on_serve',
    'on_config',
    'on_pre_build',
    #'on_files',
    #'on_nav',
    #'on_env',
    'on_post_build',
    #'on_build_error',
    #'on_pre_template',
    #'on_template_context',
    #'on_post_template',
    #'on_pre_page',
    #'on_page_read_source',
    'on_page_markdown',
    #'on_page_content',
    #'on_page_context',
    #'on_post_page',
]

clsn = lambda o: o.__class__.__name__


def get_page(hookname, a, kw, c={}):
    pos = c.get(hookname)
    if pos is None:
        if 'page' in kw:
            pos = 'kw'
        else:
            h = None
            for i, arg in zip(range(len(a)), a):
                if getattr(arg, 'is_page', None):
                    h = i
                    break
            if h is None:
                c[hookname] = -1
                return
    if pos == 'kw':
        return kw['page']
    if pos < 0:
        return
    return a[pos]


def wrap_hook(plugin, hook, hookname):
    n = clsn(plugin)
    Stats[n][hookname] = {}
    PageStats[n][hookname] = {}

    def wrapped_hook(*a, plugin=plugin, hook=hook, name=n, hookname=hookname, **kw):
        plugin.stats = stats = Stats[n][hookname]
        page = get_page(hookname, a, kw)
        if page:
            stats = PageStats[n][hookname]
            stats[(page.url, page.title)] = stats = page.stats = {}
        on = app.name
        app.name = n
        app.debug('%s.%s' % (n, hookname))
        t0 = now()
        r = hook(*a, **kw)
        dt = now() - t0
        stats['dt'] = stats.get('dt', 0) + dt

        app.name = on
        return r

    setattr(plugin, hookname, wrapped_hook)


class MDPlugin(BasePlugin):
    def __init__(self):
        app.setup_logging(mkdlog, name='lc')
        Stats[clsn(self)] = {}
        PageStats[clsn(self)] = {}
        for h in hooks:
            f = getattr(self, h, None)
            if not f:
                continue
            wrap_hook(self, f, h)


"""


HOOK: on_serve
server: livereload.Server instance
config: global configuration object
builder: a callable which gets passed to each call to server.watch

HOOK: on_config
config: global configuration object
Returns: global configuration object

HOOK: on_pre_build
config: global configuration object

HOOK: on_files
files: global files collection
config: global configuration object

HOOK: on_nav
nav: global navigation object
config: global configuration object
files: global files collection
Returns: global navigation object

HOOK: on_env
env: global Jinja environment
config: global configuration object
files: global files collection
Returns: global Jinja Environment

HOOK: on_post_build
config: global configuration object

HOOK: on_build_error
error: exception raised
Template Events


HOOK: on_pre_template
template: a Jinja2 Template object
template_name: string filename of template
config: global configuration object
Returns: a Jinja2 Template object

HOOK: on_template_context
context: dict of template context variables
template_name: string filename of template
config: global configuration object
Returns: dict of template context variables

HOOK: on_post_template
output_content: output of rendered template as string
template_name: string filename of template
config: global configuration object
Returns: output of rendered template as string

================= Page Events ===========================
HOOK: on_pre_page
page: mkdocs.nav.Page instance
config: global configuration object
files: global files collection
Returns: mkdocs.nav.Page instance

HOOK: on_page_read_source
page: mkdocs.nav.Page instance
config: global configuration object
Returns: The raw source for a page as unicode string. If None is returned, the default loading from a file will be performed.

HOOK: on_page_markdown
markdown: Markdown source text of page as string
page: mkdocs.nav.Page instance
config: global configuration object
files: global files collection
Returns: Markdown source text of page as string

HOOK: on_page_content
html: HTML rendered from Markdown source as string
page: mkdocs.nav.Page instance
config: global configuration object
files: global files collection
Returns: HTML rendered from Markdown source as string

HOOK: on_page_context
context: dict of template context variables
page: mkdocs.nav.Page instance
config: global configuration object
nav: global navigation object
Returns: dict of template context variables

HOOK: on_post_page
output: output of rendered template as string
page: mkdocs.nav.Page instance
config: global configuration object
Returns: output of rendered template as string
"""
