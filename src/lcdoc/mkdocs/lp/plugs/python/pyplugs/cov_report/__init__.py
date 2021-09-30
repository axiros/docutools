"""
### `cov_report`

Inserts a coverage report.

Based on
[pawamoy](https://github.com/pawamoy/mkdocs-coverage/tree/master/src/mkdocs_coverage)'
work.

The report must exist in the file system at evaluation time at
- dir parameter or
- $d_cover_html env var
- LP Header Syntax: `bash lp mode=cov_report [dir=<report dir>]`

#### Features:

- While LP blocks are running, the LP plugin creates a [coverage context](https://coverage.readthedocs.io/en/coverage-5.5/contexts.html#dynamic-contexts),
  with the current markdown file.
- When the lp plugin has a non empty config value for `coverage_backrefs`, a link will be created back to the markdown source with the lp block.

Mechanics how to create coverage reports in general: See the coverage setup in this repo's `/make` file.

"""


import os
from distutils.dir_util import copy_tree
from functools import partial

from lcdoc import lp
from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import make_img
from lcdoc.tools import dirname, exists, os, project

config, page, Session = (python.config, python.page, python.Session)


def register(fmts):
    fmts['coverage'] = incl_coverage


cov_files = lambda d: [k for k in os.listdir(d) if k.startswith('.coverage')]
err = lp.err

# thanks timothy:
T = ''' 
<style>
.md-main__inner {
    max-width: none;
}
article h1, article > a {
    display: none;
}
</style>

[<small>Full Page</small>](%(d_rel_html)s)
<iframe id="coviframe_%(name)s" src="%(d_rel_html)s/index.html" frameborder="0" scrolling="no"
onload="resizeIframe();" width="100%%"></iframe>

<script>
var coviframe = document.getElementById("coviframe_%(name)s");

function resizeIframe() {
    coviframe.style.height = coviframe.contentWindow.document.documentElement.offsetHeight + 'px';
}

coviframe.contentWindow.document.body.onclick = function() {
    coviframe.contentWindow.location.reload();
}
</script>

'''


def incl_html_report(**kw):
    return T % kw


idx = lambda d: d + '/index.html'
import time

now = time.time


def copy_files_to_html_site_dir(LP, d_rel_html, d_cover):
    """have to copy all report files over to site dir, since at *first* build those
    had not been scanned into the files list, when we only symlink them from the cover dir
    """
    # e.g. '/home/gk/repos/docutools/site' or the tmp dir at mkdocs serve:
    d_site = LP.config['site_dir']
    d_dest = d_site + '/' + dirname(LP.page.file.src_path) + d_rel_html
    # it never exists, server cleans it off at reruns:
    # if time would be critical we also needed to link them over to docs/autodocs which
    # is not scanned for changes
    # if exists(idx(d_dest)) and os.stat(idx(d_dest)).st_mtime >= os.stat(idx(d_cover)): return
    python.app.info('copying coverage html', frm=d_cover, to=d_dest)
    os.makedirs(d_dest, exist_ok=True)
    try:
        copy_tree(d_cover, d_dest)
    except Exception as ex:
        return err('Could not copy cover html', frm=d_cover, to=d_dest)


d_cover_dflt = os.environ.get('d_cover_html', 'build/coverage/overall')

from lcdoc.mkdocs import lp

LP = lp.LP


def incl_coverage(s, name='overall', dir=d_cover_dflt, **kw):
    if not dir[0] == '/':
        dir = project.root(config()) + '/' + dir
    if not exists(idx(dir)):
        return 'No coverage data yet in %s' % dir
    d_rel_html = '/media/cov/%s' % name

    err = copy_files_to_html_site_dir(LP, d_rel_html, dir)
    if err:
        return err
    return {
        'nocache': True,
        'res': incl_html_report(name=name, d_rel_html='..' + d_rel_html),
    }
