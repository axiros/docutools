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

from lcdoc import lp
from lcdoc.tools import dirname, exists, os, project

multi_line_to_list = False
# req_kw = ['name']

cov_files = lambda d: [k for k in os.listdir(d) if k.startswith('.coverage')]
err = lp.err

# thanks timothy:
T = ''' 
<style>
.md-content {
    max-width: none !important;
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
    return {'formatted': T % kw, 'res': 'cov_report'}


def run(cmd, kw):
    """
    interpret the command as python:
    no session, lang = python:
    """
    LP = kw['LP']
    name = kw.get('name', 'coverage')
    d_cover = kw.get('dir', os.environ.get('d_cover_html'))
    if not d_cover:
        return lp.err('require dir param or $d_cover_html')
    d_cover = project.abs_path(d_cover, LP.config)
    if not exists(d_cover + '/index.html'):
        return lp.err('No coverage html files found', dir=d_cover)

    d_rel_html = '/media/cov/%s' % name
    # does not work the first time - files not registered:
    # d_lnk = dirname(LP.page.file.abs_src_path) + d_rel_html
    # os.makedirs(dirname(d_lnk), exist_ok=True)
    # if exists(d_lnk):
    #     os.unlink(d_lnk)
    # cmd = 'ln -s "%s" "%s"' % (d_cover, d_lnk)
    # r = lp.sprun(cmd, report=lp.nfo, no_fail=True)
    # if r:
    #     return r
    err = copy_files_to_html_site_dir(LP, d_rel_html, d_cover)
    if err:
        return err
    return incl_html_report(name=name, d_rel_html='..' + d_rel_html)


def copy_files_to_html_site_dir(LP, d_rel_html, d_cover):
    """have to copy all report files over to site dir, since at *first* build those
    had not been scanned into the files list, when we only symlink them from the cover dir
    """
    # e.g. '/home/gk/repos/docutools/site' or the tmp dir at mkdocs serve:
    d_site = LP.config['site_dir']
    d_dest = d_site + '/' + dirname(LP.page.file.src_path) + d_rel_html
    os.makedirs(d_dest, exist_ok=True)
    try:
        copy_tree(d_cover, d_dest)
    except Exception as ex:
        return err('Could not copy cover html', frm=d_cover, to=d_dest)


# begin_archive
# name = kw['name']
# d_root = kw['PROJECT_ROOT']
# LP = kw['LP']

# if not exists(d_root):
#     return err('No dir', dir=d_root)
# l = cov_files(d_root)
# if not l:
#     return err('No data files', dir=d_root, hint='must start with ".coverage"')
# C = coverage.control.Coverage()
# if not ['.coverage'] in l:
#     C.combine()
# l = cov_files(d_root)
# if not '.coverage' in l:
#     return err('Cov combine failed', dir=d_root)
# C = coverage.control.Coverage(data_file=d_root + '/.coverage')
# d_rel_html = '/media/cov/%s' % name
# c = LP.config
# d_html = d_root + '/build/coverage/' + name

# d_html = c['site_dir'] + '/' + LP.page.url + d_rel_html
# d_rel_html = './' + d_rel_html
# os.makedirs(d_html, exist_ok=True)
# [os.unlink(d_html + '/' + f) for f in os.listdir(d_html)]
# cmd = 'coverage html --title="%s" -d "%s"' % (n, d_html)
# app.info('creating report', cmd=cmd)
# # C.html_report(directory=d_html, precision=2)
# if os.system(cmd) or not exists(d_html + '/index.html'):
#     return err('html creation failed', cmd=cmd)
# return incl_html_report(name=n, d_rel_html=d_rel_html)
