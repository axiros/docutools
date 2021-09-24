import shutil
import string
import subprocess as sp

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import page_dir
from lcdoc.tools import write_file, project, app, exists, os, sys, dirname


config, page, Session, err = (python.config, python.page, python.Session, python.err)

inst = 'npm install -g chrome-remote-interface minimist'

# fmt:off
# :docs:url_shot_defaults
url_shot_defaults = {
    'port': 9922,     # port of chrome remote interface
    'format': 'png',  # or jpeg
    'force': False,   # overwrite if shot exists
    'width': 1440,    # width of chrome window
    'height': 900,    # height
    'delay': 0,       # wait this long before shots (setTimeout param)
    'into': 'img'     # directory to put the screenshot into, relative to page
}
# :docs:url_shot_defaults
# fmt:on

brwsr = '%(browser)s --headless --hide-scrollbars --remote-debugging-port=%(port)s --disable-gpu'


def url_to_fn(url, p):
    fmt = p['format']
    url = url.replace('/', '_')
    C = string.ascii_letters + '._0123456789'
    url = ''.join([c for c in url if c in C])
    return url + '.' + fmt


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
    # node module not found, working in /tmp?!
    # d_tmp = tempfile.mkdtemp()
    d_tmp = project.root(config()) + '/build/urlshot'
    os.makedirs(d_tmp, exist_ok=True)
    app.info('Screenshot', **ctx)
    try:
        os.chdir(d_tmp)
        write_file('index.js', T % ctx)
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
        return '![](./%s)' % r
    python.app.die('not supported', cmd=cmd)


# begin_archive
# https://dschnurr.medium.com/using-headless-chrome-as-an-automated-screenshot-tool-4b07dffba79a
T = '''

const CDP = require("chrome-remote-interface");
const argv = require("minimist")(process.argv.slice(2));
const file = require("fs");

// CLI Args
const url = argv.url
const format = "%(format)s"
const viewportWidth = %(width)s
const viewportHeight = %(height)s
const delay = %(delay)s
const userAgent = argv.userAgent;
const fullPage = ""; // does not work. use height

// Start the Chrome Debugging Protocol
CDP({port: %(port)s}, async function (client) {
  // Extract used DevTools domains.
  const { DOM, Emulation, Network, Page, Runtime } = client;

  // Enable events on domains we are interested in.
  await Page.enable();
  await DOM.enable();
  await Network.enable();

  // If user agent override was specified, pass to Network domain
  if (userAgent) {
    await Network.setUserAgentOverride({ userAgent });
  }

  // Set up viewport resolution, etc.
  const deviceMetrics = {
    width: viewportWidth,
    height: viewportHeight,
    deviceScaleFactor: 0,
    mobile: false,
    fitWindow: false,
  };
  await Emulation.setDeviceMetricsOverride(deviceMetrics);
  await Emulation.setVisibleSize({
    width: viewportWidth,
    height: viewportHeight,
  });

  // Navigate to target page
  await Page.navigate({ url });

  // Wait for page load event to take screenshot
  Page.loadEventFired(async () => {
    // If the `full` CLI option was passed, we need to measure the height of
    // the rendered page and use Emulation.setVisibleSize
    if (fullPage) {
      const {
        root: { nodeId: documentNodeId },
      } = await DOM.getDocument();
      const { nodeId: bodyNodeId } = await DOM.querySelector({
        selector: "body",
        nodeId: documentNodeId,
      });
      const {
        model: { height },
      } = await DOM.getBoxModel({ nodeId: bodyNodeId });

      await Emulation.setVisibleSize({ width: viewportWidth, height: height });
      // This forceViewport call ensures that content outside the viewport is
      // rendered, otherwise it shows up as grey. Possibly a bug?
      await Emulation.forceViewport({ x: 0, y: 0, scale: 1 });
    }

    setTimeout(async function () {
      const screenshot = await Page.captureScreenshot({ format });
      const buffer = new Buffer(screenshot.data, "base64");
      file.writeFile("output.png", buffer, "base64", function (err) {
        if (err) {
          console.error(err);
        } else {
          console.log("Screenshot saved");
        }
        client.close();
      });
    }, delay);
  });
}, {port: %(port)s}).on("error", (err) => {
  console.error("Cannot connect to browser:", err);
});
'''
