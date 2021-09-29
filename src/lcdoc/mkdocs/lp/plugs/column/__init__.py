"""
###  `lightbox`

"""


from lcdoc.mkdocs.tools import style

nocache = True
formatted = True
nocache = True

sep = '<b>-col-</b>'

# :docs:lp_column_dflts
lp_column_dflts = {
    'max_width': '1000px',  # max width per column - determines the min total width
    'padding': '0',
    'margin': '2%',
    'custom_style': False,  # when set we do NOT include our Column Style, user must.
}

ColumnStyle = '''
@media screen and (min-width: %(min_total_width)s) {
    .md-grid { max-width: initial;}
    .lp-row { display: flex; }
    .lp-column {
      padding: %(padding)s;
      margin-left: %(margin)s;
      margin-right: %(margin)s;
      flex: %(flex)s%%;
      max-width: %(max_width)s;
    }
}
'''
# :docs:lp_column_dflts


def to_col(html, page, LP, **kw):
    html = html.split(sep)
    cols = len(html)
    if cols == 1:
        return html
    d = dict(lp_column_dflts)
    d.update(page.lp_column_settings)
    mw = d.get('max_width')
    unit = 'px'
    for u in ('px', '%', 'em', 'rem'):
        if mw.endswith(u):
            unit = u
            mw = int(mw.split(u, 1)[0])
            break
    d['min_total_width'] = d.get('min_total_width', '%s%s' % (mw * cols, unit))
    d['flex'] = 100.0 / cols
    h = '<div class="lp-row"><div class="lp-column">'
    h = h + '</div><div class="lp-column">'.join(html) + '</div></div>'
    if not d['custom_style']:
        h += style(ColumnStyle % d)
    return h


page_assets = {'func': to_col}


def run(cmd, kw):
    p = kw['LP'].page
    p.lp_column_settings = s = getattr(p, 'lp_column_settings', {})
    s.update(kw)
    return sep
