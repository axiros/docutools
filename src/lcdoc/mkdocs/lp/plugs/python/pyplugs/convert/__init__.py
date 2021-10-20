import os
from functools import partial

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import make_img
from lcdoc.tools import dirname, exists

config, page, Session = (python.config, python.page, python.Session)


def register(fmts):
    fmts['convert'] = convert


dflts = dict(width=400, pages=0, thumbwidth=200)


def pngs(fn_png):
    k = os.path.basename(fn_png).rsplit('-', 1)[0].rsplit('.png', 1)[0]
    dir = dirname(fn_png)
    return [dir + '/' + i for i in os.listdir(dir) if k in i and i.endswith('.png')]


def unlink_old_pngs(fn_png):
    for fn in pngs(fn_png):
        python.app.info('unlinking old', fn=fn)
        os.unlink(fn)


def convert_pdf(fn_pdf, kw):
    fn_png = kw.get('png', fn_pdf + '.png')
    dp = os.path.dirname(page().file.abs_src_path) + '/'
    if not exists(fn_pdf):
        fn_pdf = dp + fn_pdf
        if not exists(fn_pdf):
            return 'Pdf not present: %s' % fn_pdf
    if not fn_png.startswith('/'):
        fn_png = dp + fn_png
    d = dict(dflts)
    d.update(kw)
    width = d['width']
    pages = d['pages']
    unlink_old_pngs(fn_png)
    cmd = f'convert -thumbnail x{width} -background white -alpha remove "{fn_pdf}[{pages}]" "{fn_png}"'
    python.app.info('Converting pdf to png', cmd=cmd)
    if os.system(cmd):
        return 'err running %s' % cmd

    if str(pages).isdigit():
        # single png with link to pdf:
        return '[![](%s)](%s)' % (fn_png.replace(dp, ''), fn_pdf.replace(dp, ''))

    python.app.info('Creating slideshow')
    pics = pngs(fn_png)
    pdf = os.path.basename(fn_pdf)
    relp = lambda fn: fn.replace(dp, '')
    pdfr = relp(fn_pdf)
    r = ['<div style="display:flex; flex-wrap:wrap;">']
    for k in pics:
        p = relp(k)
        p = '../' + p
        # pic = f'![]({p})'
        pic = f'<div style="width: 300px;margin: 5px;"><img width=100% src="{p}"></div>'
        r.append(pic)
    r += ['</div>']
    r += [f'[{pdf}]({pdfr})']
    from lcdoc.mkdocs.lp.plugs import lightbox

    res = lightbox.run('', {'mode': 'lightbox'})
    res['res'] = '\n\n'.join(r)
    return res


def convert(s, pdf=None, **kw):
    if pdf:
        return convert_pdf(pdf, kw)
    return 'Not supported: %s' % str(locals())
