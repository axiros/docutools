"""
###  `drawio`

Automatically includes an svg, based on .drawio file changes.
"""

import json
import subprocess as sp

from lcdoc import lp
from lcdoc.tools import file_hash, app, dirname, exists, os, read_file, write_file, os

multi_line_to_list = True
req_kw = ['fn', 'src']


def run(cmd, kw):
    """
    """
    D = lp.page_dir(kw)
    src = kw['abs_src']
    if not exists(src):
        return 'Not found: %s' % src
    fn = kw['fn']
    if not fn or fn[0] == '/':
        return lp.err('Require relative fn', have=fn)
    ffn = D + fn
    os.makedirs(dirname(ffn), exist_ok=True)
    fn_src_info = ffn + '.src'
    if exists(fn_src_info):
        oldmtime, oldhsh = json.loads(read_file(fn_src_info))
    else:
        oldmtime, oldhsh = 0, 0

    mtime = os.stat(src).st_mtime
    have, hsh = False, None
    if mtime == oldmtime:
        have = True
    else:
        hsh = file_hash(src)
        if hsh == oldhsh:
            have = True
    if not have:
        create_new_svg(src, ffn, kw)
        write_file(fn_src_info, json.dumps([mtime, hsh or file_hash(src)]))
    return {'res': '![](%s)' % fn, 'formatted': True}


def create_new_svg(fn_src, fn_svg, kw):
    app.info('Exporting drawio', src=fn_src, svg=fn_svg)
    d = os.environ.get('drawio', 'drawio')
    sp.call([d, '--output', fn_svg, '--export', fn_src])
