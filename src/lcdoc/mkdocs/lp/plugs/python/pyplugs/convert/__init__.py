import os
from functools import partial

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import make_img
from lcdoc.tools import exists

config, page, Session = (python.config, python.page, python.Session)


def register(fmts):
    fmts['convert'] = convert


dflts = {'width': 400}


def convert_pdf(fn_pdf, kw):
    fn_png = kw.get('png', fn_pdf + '.png')
    dp = os.path.dirname(page().file.abs_src_path) + '/'
    if not exists(fn_pdf):
        fn_pdf = dp + fn_pdf
        if not exists(fn_pdf):
            return 'Pdf not present: %s' % fn_pdf
    if not fn_png.startswith('/'):
        fn_png = dp + fn_png
    width = kw.get('width', dflts['width'])
    cmd = f'convert -thumbnail x{width} -background white -alpha remove "{fn_pdf}[0]" "{fn_png}"'
    if os.system(cmd):
        return 'err running %s' % cmd
    return '[![](%s)](%s)' % (fn_png.replace(dp, ''), fn_pdf.replace(dp, ''))


def convert(s, pdf=None, **kw):
    if pdf:
        return convert_pdf(pdf, kw)
    return 'Not supported: %s' % str(locals())
