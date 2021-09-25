"""
https://dschnurr.medium.com/using-headless-chrome-as-an-automated-screenshot-tool-4b07dffba79a
"""
import shutil
import string
import subprocess as sp

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import page_dir
from lcdoc.tools import app, dirname, exists, os, project, sys, write_file, read_file

config, page, Session, err = (python.config, python.page, python.Session, python.err)

inst = 'npm install -g chrome-remote-interface minimist'


# fmt:off
url_shot_defaults = dict(
# :docs:url_shot_defaults
    delay   = 0,     # wait this long before shots (setTimeout param)
    force   = False, # overwrite if shot exists
    format  = 'png', # or jpeg
    height  = 900,   # height or chrome window when fetching the URL
    into    = 'img', # directory to put the screenshot into, relative to page
    port    = 9922,  # port of chrome remote interface
    width   = 1440,  # width of chrome window
# :docs:url_shot_defaults
)
# fmt:on

brwsr = ' '.join(
    [
        '%(browser)s',
        '--headless',
        '--hide-scrollbars',
        '--remote-debugging-port=%(port)s',
        '--disable-gpu',
    ]
)


def url_to_fn(url, p, C=string.ascii_letters + '._0123456789'):
    fmt = p['format']
    url = url.replace('/', '_')
    url = ''.join([c for c in url if c in C])
    return url + '.' + fmt


T_index_js = read_file(dirname(__file__) + '/index.js')


def urlshot(**show_kw):
    ctx = dict(url_shot_defaults)
    ctx.update(show_kw)
    url = ctx['url']
    url_fn = url_to_fn(url, ctx)
    dfn = ctx['into']
    fn_shot = page_dir(Session.kw) + dfn + '/' + url_fn
    md_fn = dfn + '/' + url_fn
    if exists(fn_shot) and not ctx['force']:
        app.info('Screenshot already exists', fn=fn_shot)
        return md_fn
    if config()['site_url'].startswith(url) and 'serve' in sys.argv:
        app.error('Cannot shoot url while building the site in serve mode', url=url)
        return md_fn
    ctx['browser'], ctx['node'] = urlshot_requirements()
    here = os.getcwd()

    # node module not found, working in /tmp?! d_tmp = tempfile.mkdtemp()
    d_tmp = project.root(config()) + '/build/urlshot'
    os.makedirs(d_tmp, exist_ok=True)
    app.info('Screenshot', **ctx)
    try:
        os.chdir(d_tmp)
        write_file('index.js', T_index_js % ctx)
        bp = sp.Popen(brwsr % ctx, shell=True)
        cmd = '%(node)s index.js --url="%(url)s"' % ctx
        e = os.system(cmd)
        if e:
            return err('Failed urlshot', cmd=cmd, hint=inst)
        os.makedirs(dirname(fn_shot), exist_ok=True)
        shutil.move('output.%(format)s' % ctx, fn_shot)
        return md_fn
    finally:
        os.chdir(here)
        bp.kill()


def urlshot_requirements():
    browser = os.environ.get('browser', os.environ.get('BROWSER', 'nobrowser'))
    if os.system(browser + ' --version >/dev/null'):
        raise Exception('$BROWSER not working. hint=%s' % 'export $BROWSER')
    node = os.environ.get('nodejs', 'node')
    if os.system(node + ' -v >/dev/null'):
        return err('Have no node command. hint=%s. Also: %s' % ('export $nodejs', inst))
    return browser, node


def register(fmts):
    fmts['screenshot'] = makeshot


def makeshot(cmd, url=None, **kw):
    if url:
        r = urlshot(url=url, **kw)
        title = url.replace(']', '').replace('[', '')
        return '![Screenshot: %s](./%s)' % (title, r)
    python.app.die('not supported', cmd=cmd)
