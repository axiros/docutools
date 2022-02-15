"""
We replace via md-find

    !!! :foo: ["some title"]

with

    <style>
    ...
    </style>

    !!! some-title "some title"

see: https://squidfunk.github.io/mkdocs-material/reference/admonitions/#customization
"""

import os
from functools import partial
from lcdoc.mkdocs.tools import read_file, app
import material


def style(typ, ico, col, bgcol=None):
    if not bgcol:
        if not 'rgb(' in col:
            raise Exception('You need an rgb col if you do not specify bgcol')
        bgcol = col.strip().replace('rgb(', 'rgba(')[:-1] + ', 0.1)'
    s = '''
<style>
:root { --md-admonition-icon--%(typ)s: url('data:image/svg+xml;charset=utf-8,%(ico)s') }
.md-typeset .admonition.%(typ)s,
.md-typeset details.%(typ)s {
  border-color: %(col)s;
}
.md-typeset .%(typ)s > .admonition-title,
.md-typeset .%(typ)s > summary {
  background-color: %(bgcol)s;
  border-color: %(col)s;
}
.md-typeset .%(typ)s > .admonition-title::before,
.md-typeset .%(typ)s > summary::before {
  background-color: %(col)s;
  -webkit-mask-image: var(--md-admonition-icon--%(typ)s);
          mask-image: var(--md-admonition-icon--%(typ)s);
}
</style>
'''
    return s % locals()


import httpx


def admons(*which):
    _ = cust_admons
    return {k: partial(admon, **v) for k, v in _.items() if k in which}


d_material = os.path.dirname(material.__file__)


def get_raw(svg):
    """
    ico = '<svg ....' # raw svg from anywhere. 
    ico = 'https://twemoji.maxcdn.com/v/latest/svg/1f4f7.svg' # url
    ico = 'material/camera-account.svg' # file in your site-directories/material/.icons
    """
    if svg.startswith('<svg'):
        return svg
    if svg.startswith('http'):
        return httpx.get(svg).text
    fn = os.path.join(d_material + '/.icons/', svg)
    s = read_file(fn, dflt='')
    if s:
        return s
    app.die('Icon not loadable', ico=svg)


def admon(title, ico, col, bgcol=None, **kw):
    p = kw['page']
    ind = kw['line'].split('!!!', 1)[0]
    l = kw['line'].split(':')
    t = title.lower().replace(' ', '-')
    if len(l) == 3 and l[2]:
        title = l[2]
    # avoid duplicate style defs in one page:
    s, tn = '', 'admon_style_' + t
    if not hasattr(p, tn):
        ico = get_raw(ico)
        s = style(t, ico, col, bgcol)
        setattr(p, tn, True)
    r = {'line': '''%s!!! %s "%s"''' % (ind, t, title), 'markdown_header': s}
    return r


ico_dev = 'fontawesome/brands/dev.svg'

# import this within mdreplace and extend to your liking
cust_admons = {
    'dev': dict(title='Developer Tip', ico=ico_dev, col='rgb(139, 209, 36)'),
}


# then say e.g.

# table.update(admons.admons('dev'))
