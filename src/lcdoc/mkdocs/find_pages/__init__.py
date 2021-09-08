"""
## Find Pages

Adds pages to nav
"""
from ast import literal_eval
from functools import partial

from lcdoc.mkdocs.tools import MDPlugin, app, config_options, find_md_files
from lcdoc.tools import dirname, exists, flatten, os, project, read_file
import string


def uppercase_words(s):
    """titles in nav should only contain the strings, not e.g. links"""
    l = s.split(' ')
    r = []
    while l[0] == l[0].upper() and l[0] in string.ascii_letters:
        r.append(l)
    return ' '.join(r)


def find_pages(find, config, stats):

    ev = [i.strip() for i in os.environ.get('find_pages', '').split(',')]
    ev = [i for i in ev if i]
    find.extend(ev)
    find = list(set(find))
    stats['find_terms'] = len(find)
    if not find:
        return
    found = []
    for m in find:
        found = find_md_files(match=m, config=config)
        if not found:
            app.warning('No pages found', match=m)
        found.extend(found)
    stats['matching'] = len(found)
    return found


def find_pages_and_add_to_nav(find, config, stats):
    found = find_pages(find, config, stats)
    if not found:
        return

    m = {p: None for p in found}
    nav = config['nav']
    navl = flatten(nav, '.')
    m.update({v: k for k, v in navl.items()})
    stats['missing'] = len(m) - len(navl)

    # find the right position to insert:
    b, a, l = None, None, sorted([[k, v] for k, v in m.items()])
    new, dd = [['', '']], config['docs_dir']

    def get_title(fn_page):
        h = read_file(dd + '/' + fn_page, dflt='') + '\n# Found\n'
        return uppercase_words(h.split('\n# ', 1)[1].split('\n', 1)[0])

    def clear_digits(t):
        return '.'.join([k for k in t.split('.') if not k.isdigit()])

    newt = []
    while l:
        new.append(l.pop(0))
        if new[-1][1]:
            continue
        h = get_title(new[-1][0])
        b, cur = new[-2], new[-1]
        app.info('Adding to nav', path=cur[0], title=h)
        title = into_path(cur[0], b[0], b[1])
        a = [k for k in l if k[1]]
        if a:
            a = a[0]
            titlea = into_path(cur[0], a[0], a[1])
            if len(titlea) > len(title):
                title = titlea
        new[-1][1] = title + '.' + h
        newt.append(clear_digits(new[-1][1]))
    if not newt:
        return
    new = sorted([[v, k] for k, v in new[1:]])
    new = [[clear_digits(t), i] for t, i in new]
    out = [[k, ('-- ADDED --> ' if k in newt else '') + v] for k, v in new]
    out = [dict(out), 'Added:', newt]
    app.info('Rebuilt nav tree', json=out)
    nnav = []
    rebuild_nav(new, into=nnav)
    config['nav'].clear()
    config['nav'].extend(nnav)


def rebuild_nav(l, into, start=''):
    if start:
        start += '.'
    for t, p in l:
        if not t.startswith(start):
            continue
        if start:
            t = t.split(start, 1)[1]
        s = t.split('.')
        if len(s) > 1:
            lc = []
            rebuild_nav(l, into=lc, start=start + s[0])
            p = lc
            t = s[0]
        if not into or list(into[-1].keys())[0] != t:
            into.append({t: p})


def into_path(dm, dh, th):
    """
    (Pdb) pp dm, dh, th (m=miss, h=have)
    ('features/bar/baz.md', 'features/termcasts/index.md', '3.Features.3.TermCasts')
    Then we return '3.Features.3.'
    """
    dm = dirname(dm)
    dh = dirname(dh)
    th = th.rsplit('.', 1)[0]
    if dm == dh:
        return th
    r = th.rsplit('.', 1)
    if r[-1].isnumeric():
        th = r[0]
    return into_path(dm, dh, th)


class MDFindPagesPlugin(MDPlugin):
    config_scheme = (('find-pages', config_options.Type(list, default=[])),)

    def on_config(self, config):
        find_pages_and_add_to_nav(self.config['find-pages'], config, self.stats)
