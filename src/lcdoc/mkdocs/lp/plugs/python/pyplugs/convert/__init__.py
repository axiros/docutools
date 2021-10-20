import os
import shutil
from functools import partial

from lcdoc.mkdocs.lp.plugs import lightbox, python
from lcdoc.mkdocs.tools import make_img
from lcdoc.tools import dirname, exists

config, page, Session = (python.config, python.page, python.Session)


def register(fmts):
    fmts['convert'] = convert


# :docs:convert_defaults
# Set keep=True in order to keep the produced pngs within the docs dir:
dflts = dict(width=400, pages=0, thumbwidth=200, keep=False)
# :docs:convert_defaults


def pngs(fn_png):
    k = os.path.basename(fn_png).rsplit('-', 1)[0].rsplit('.png', 1)[0]
    dir = dirname(fn_png)
    return [dir + '/' + i for i in os.listdir(dir) if k in i and i.endswith('.png')]


def unlink_old_pngs(fn_png):
    for fn in pngs(fn_png):
        python.app.info('unlinking old', fn=fn)
        os.unlink(fn)


def move_to_site_dir(d, fn_png, relp):
    copy_or_move = shutil.copyfile if d['keep'] else shutil.move
    sd = config()['site_dir'] + '/' + page().file.src_path
    sd = sd.replace('/index.md', '').replace('.md', '')
    sd += '/' if not sd.endswith('/') else ''
    sd += dirname(relp(fn_png))
    os.makedirs(sd, exist_ok=True)
    for i in pngs(fn_png):
        copy_or_move(i, sd)


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

    relp = lambda fn, dp=dp: fn.replace(dp, '')
    if str(pages).isdigit():
        # single png with link to pdf:
        move_to_site_dir(d, fn_png, relp)
        return '[![](%s)](%s)' % (fn_png.replace(dp, ''), fn_pdf.replace(dp, ''))

    python.app.info('Creating slideshow')
    pics = pngs(fn_png)
    pdf = os.path.basename(fn_pdf)
    pdfr = relp(fn_pdf)
    r = ['<div style="display:flex; flex-wrap:wrap;" class="pdf-slides">']
    twidth = d['thumbwidth']
    for k in pics:
        p = relp(k)
        if not page().file.src_path.endswith('/index.md'):
            p = '../' + p
        # pic = f'![]({p})'
        pic = f'<div style="width:{twidth}px;margin: 5px;"><img width=100% src="{p}"></img></div>'
        r.append(pic)
    r += ['</div>']
    r += [f'[{pdf}]({pdfr})']

    res = lightbox.run('', {'mode': 'lightbox', 'outer_match': '.pdf-slides '})
    res['res'] = '\n\n'.join(r)
    res['page_assets'] = {'lightbox': lightbox.page_assets}
    move_to_site_dir(d, fn_png, relp)
    return res


def convert(s, pdf=None, **kw):
    if pdf:
        return convert_pdf(pdf, kw)
    return 'Not supported: %s' % str(locals())
