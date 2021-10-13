"""
## Find Pages

Adds pages to nav
"""
import string
import time
from ast import literal_eval
from collections import OrderedDict as OD
from functools import partial

from lcdoc.mkdocs.tools import MDPlugin, app, config_options, find_md_files
from lcdoc.tools import dirname, exists, flatten, os, project, read_file


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
    fnd = []
    for m in find:
        found = find_md_files(match=m, config=config)
        if not found:
            app.info('No pages found', match=m)
        else:
            fnd.extend(found)
    stats['matching'] = len(fnd)
    return fnd


def is_after(fn, hfn):

    breakpoint()  # FIXME BREAKPOINT


def get_insert_pos(fn, have):
    while fn:
        fn, post = fn.rsplit('/', 1)
        for i in range(len(have)):
            if not have[i].startswith(fn):
                continue
            while have[i] < (fn + '/' + post) and have[i].startswith(fn):
                i += 1
            return have[i - 1], have[i]


now = time.time


def clear_digits(t):
    return '.'.join([k for k in t.split('.') if not k.isdigit()])


def find_pages_and_add_to_nav(find, config, stats):
    found = find_pages(find, config, stats)
    if not found:
        return

    # m = OD({p: None for p in found})
    nav = config['nav']
    navl = flatten(nav, '.')
    navll = [[fn, k] for k, fn in navl.items()]
    have = [fn[0] for fn in navll]
    ins = {}
    while found:
        fn = found.pop(0)
        if fn in have:
            continue
        bef, aft = get_insert_pos(fn, have)
        ins.setdefault(have.index(bef), []).insert(0, fn)
    l = {}
    for k in reversed(sorted([i for i in ins])):
        fns = ins[k]
        [have.insert(k + 1, fn) for fn in fns]
        l[have[k]] = fns
    app.info('Inserting %s pages into nav' % sum([len(i) for i in ins.values()]), json=l)
    # have now the complete list with found ones inserted at right places
    #  'features/lp/python/_tech.md',
    #  'features/lp/python/data_table/index.md',
    navl_rev = {v: k for k, v in navl.items()}
    r = OD()

    dd = config['docs_dir']

    def get_title(fn_page):
        h = '\n' + read_file(dd + '/' + fn_page, dflt='') + '\n# Found\n'
        h = uppercase_words(h.split('\n# ', 1)[1].split('\n', 1)[0])
        if not h:
            # e.g. # bash alone has no uppercase word. then take the filename:
            l = fn_page.rsplit('/', 2)
            if l[-1] == 'index.md':
                h = l[-2]
            else:
                h = fn_page.rsplit('/', 1)[-1].split('.', 1)[0]
        return h

    to = None
    for h in have:
        tit = navl_rev.get(h)
        if not tit:
            t = to.rsplit('.', 2)
            tit = '.'.join((t[0], str(int(t[-2]) + 1), get_title(h)))
        r[tit] = h
        to = tit

    n = OD()
    for k, v in r.items():
        n[clear_digits(k)] = v

    r = unflatten(n)
    r = to_list(r)
    config['nav'].clear()
    config['nav'].extend(r)


def to_list(d):
    l = []
    for k, v in d.items():
        v = v if not isinstance(v, dict) else to_list(v)
        l.append({k: v})
    return l


def unflatten(dictionary):
    resultDict = OD()
    for key, value in dictionary.items():
        parts = key.split('.')
        d = resultDict
        for part in parts[:-1]:
            if part not in d:
                d[part] = OD()
            d = d[part]
        d[parts[-1]] = value
    return resultDict


def into_path(item, after, last_title):
    """
    (Pdb) pp item, after, last_title
    ('features/termcasts/zab/baz.md', 'features/termcasts/index.md', '3.Features.3.TermCasts.0.Overview')

    Then we return '3.Features.3.TermCasts.0'
    """
    while not item.startswith(after):
        after = after.rsplit('/', 1)[0]
    parts = after.split('/')
    return '.'.join(last_title.split('.', 2 * len(parts) + 1)[:-1])


class MDFindPagesPlugin(MDPlugin):
    config_scheme = (('find-pages', config_options.Type(list, default=[])),)

    def on_config(self, config):
        # t0 = now()
        find_pages_and_add_to_nav(self.config['find-pages'], config, self.stats)
        # print(now() - t0)  # = 0.02 for docutools. Could be improved
