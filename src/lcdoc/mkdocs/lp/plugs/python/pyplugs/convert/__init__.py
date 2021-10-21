import os
import shutil
from functools import partial

from mkdocs.structure.files import File

from lcdoc.mkdocs.lp.plugs import lightbox, python
from lcdoc.mkdocs.tools import make_img
from lcdoc.tools import dirname, exists

config, page, Session = (python.config, python.page, python.Session)

LP = lambda: python.lpkw()['LP']

# :docs:convert_defaults
# Set png=img/foo.png in order to keep the produced pngs within the docs dir:
# pages: whatever is accepted by convert. E.g. 0-4. 0=first page
dflts = dict(width=400, pages=0, thumbwidth=200)
# :docs:convert_defaults


def pngs(fn_png):
    k = os.path.basename(fn_png).rsplit('-', 1)[0].rsplit('.png', 1)[0]
    dir = dirname(fn_png)
    return [dir + '/' + i for i in os.listdir(dir) if k in i and i.endswith('.png')]


def unlink_old_pngs(fn_png, dd):
    files = LP().files
    for fn in pngs(fn_png):
        python.app.info('unlinking old', fn=fn)
        os.unlink(fn)
        fns = fn.replace(dd + '/', '')
        [files.remove(f) for f in files if f.src_path.endswith(fns)]


def png_pth(fn_png, relp, page, dd):
    rp = relp(fn_png)
    return rp.replace(
        dd + '/build/', ('../' * (len(page().file.src_path.split('/')) - 1) + 'build/'),
    )


def add_files(dd, fn_png):
    files = LP().files
    f = File(fn_png.replace(dd + '/', ''), dd, config()['site_dir'], False)
    files.append(f)


def convert_pdf(fn_pdf, kw):
    dp = os.path.dirname(page().file.abs_src_path) + '/'
    dd = config()['docs_dir']
    fn_png = kw.get('png')
    if not fn_png:
        nr = str(LP().spec['nr']) + '/'
        fn_png = dp.replace(config()['docs_dir'], '')
        fn_png = dd + '/build' + fn_png + nr + os.path.basename(fn_pdf) + '.png'
        os.makedirs(dirname(fn_png), exist_ok=True)
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
    unlink_old_pngs(fn_png, dd)
    cmd = f'convert -thumbnail x{width} -background white -alpha remove "{fn_pdf}[{pages}]" "{fn_png}"'
    python.app.info('Converting pdf to png', cmd=cmd)
    if os.system(cmd):
        return 'err running %s' % cmd

    relp = lambda fn, dp=dp: fn.replace(dp, '')
    if str(pages).isdigit():
        # single png with link to pdf:
        rp = png_pth(fn_png, relp, page, dd)
        add_files(dd, fn_png)
        return '[![](%s)](%s)' % (rp, relp(fn_pdf))

    python.app.info('Creating slideshow')
    pics = pngs(fn_png)
    pdf = os.path.basename(fn_pdf)
    pdfr = relp(fn_pdf)
    r = ['<div style="display:flex; flex-wrap:wrap;" class="pdf-slides">']
    twidth = d['thumbwidth']
    ni = '' if page().file.src_path.endswith('/index.md') else '../'
    for k in pics:
        p = png_pth(k, relp, page, dd)
        add_files(dd, k)
        # pic = f'![]({p})'
        pic = f'<div style="width:{twidth}px;margin: 5px;"><img width=100% src="{ni}{p}"></img></div>'
        r.append(pic)
    r += ['</div>']
    r += [f'[{pdf}]({pdfr})']

    res = lightbox.run('', {'mode': 'lightbox', 'outer_match': '.pdf-slides '})
    res['res'] = '\n\n'.join(r)
    res['page_assets'] = {'lightbox': lightbox.page_assets}
    return res


def convert(s, pdf=None, **kw):
    if pdf:
        return convert_pdf(pdf, kw)
    return 'Not supported: %s' % str(locals())


register = {'convert': convert}
