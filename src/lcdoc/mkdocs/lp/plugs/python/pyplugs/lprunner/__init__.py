import os
from functools import partial

from lcdoc.const import lprunner_sep as sep
from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import make_img
from lcdoc.tools import write_file

config, page, Session = (python.config, python.page, python.Session)


def register(fmts):
    """registering us as renderer for show(<pyplot module>) within lp python"""
    fmts['lprunner'] = lprunner


msg = '''
??? "Run this locally"
    
    You can run the code on this page locally via:

    ```bash
    pip install --user docutools # if not yet installed
    mdrun "%s"
    ```
'''


def lprunner(s, **kw):
    """The client requires the source"""
    url = config()['site_dir'] + '/' + page().url
    if not url.endswith('/'):
        python.app.die('for runners we require URLs ending with "/"')
    url += 'runner.md'
    src = page().markdown
    write_file(url, src, mkdir=True)
    url = config()['site_url'] + page().url
    return {'res': msg % url, 'formatted': True, 'nocache': True}
