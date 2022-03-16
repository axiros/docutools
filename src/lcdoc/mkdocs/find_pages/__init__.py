"""
## Find Pages

Adds pages to nav
"""

import string
import time
from ast import literal_eval
from functools import partial

from lcdoc.mkdocs.tools import MDPlugin, app, config_options, find_md_files
from lcdoc.tools import dirname, exists, OD, unflatten, flatten, os, project, read_file
from lcdoc.mkdocs.find_pages.autodocs import autodocs, find_pages


def repl_src_refs(s):
    if not s.startswith(':srcref:'):
        return s
    s = s.split(',t=', 1)
    if len(s) == 1:
        return ''
    return s[-1].split(',', 1)[0]


def uppercase_words(s):
    """titles in nav should only contain the strings, not e.g. links

    s: "Local LP Blocks :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/lprunner/__init__.py,t=Runner"

    """
    L = [repl_src_refs(i) for i in s.split(' ')]
    r = []
    for l in L:
        if l and l[0] == l[0].upper() and l[0] in string.ascii_letters:
            r.append(l)
    return ' '.join(r)


def is_after(fn, hfn):

    breakpoint()  # FIXME BREAKPOINT


def get_insert_pos(fn, have):
    """when "after" is not given we have to find out ourselves"""
    while fn:
        fn, post = fn.rsplit('/', 1)
        for i in range(len(have)):
            if not have[i].startswith(fn):
                continue
            while (
                (i < len(have) - 1)
                and have[i] < (fn + '/' + post)
                and have[i].startswith(fn)
            ):
                i += 1
            return have[i - 1], have[i]


# get_insert_pos( './features', ['index.md', 'install.md', 'features/index.md', 'features/blacklist/index.md'],)
now = time.time


def clear_digits(t):
    return '.'.join([k for k in t.split('.') if not k.isdigit()])


def get_title(fn_page, dd):
    # TODO: find the mkdocs way of deriving the title from the header within content
    s = read_file(dd + '/' + fn_page, dflt='')
    h = '\n' + s + '\n# Found\n'  # so that we find *something* when there is no head
    tit = ''
    # find the highest header, could be also "### My Title"
    for k in range(5, 0, -1):
        head = '\n' + k * '#' + ' '  #  "\n#### " for k = 3
        _ = h.split(head)
        if len(_) == 1:
            continue
        h = _[0]  # the content above, is there a higher header?
        tit = _[1].split('\n', 1)[0]
    if not tit:
        tit = fn_page
    h = uppercase_words(tit)
    if not h:
        # e.g. # `bash` alone has no uppercase word. then take the filename:
        l = fn_page.rsplit('/', 2)
        if l[-1] == 'index.md':
            h = l[-2]
        else:
            h = fn_page.rsplit('/', 1)[-1].split('.', 1)[0]
    return h


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
    for spec in found:
        while spec['found']:
            fn = spec['found'].pop(0)
            if fn in have:
                continue
            aft = spec.get('after')
            if not aft:
                aft, _ = get_insert_pos(fn, have)
            ins.setdefault(have.index(aft), []).insert(0, fn)
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

    to = None
    for h in have:
        tit = navl_rev.get(h)
        if not tit:
            t = to.rsplit('.', 2)
            try:
                T = get_title(h, dd)
                if t[-1].isdigit():
                    tit = '.'.join((t[0], t[1], str(int(t[2]) + 1), T))
                else:
                    tit = '.'.join((t[0], str(int(t[-2]) + 1), T))
            except Exception as ex:
                hint = 'Your filenames in that folder must match mkdocs config'
                msg = 'Cannot find position or title for page'
                app.error(msg, page=h, to=to, hint=hint)
                raise
        r[tit] = h
        to = tit

    n = OD()
    for k, v in r.items():
        n[clear_digits(k)] = v

    r = unflatten(n, '.')
    r = to_list(r)
    config['nav'].clear()
    config['nav'].extend(r)


def to_list(d):
    l = []
    for k, v in d.items():
        if k == None:  # inserted by unflatten, when there was no title
            l.append(v)
            continue
        v = v if not isinstance(v, dict) else to_list(v)
        l.append({k: v})
    return l


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
    config_scheme = (
        ('find-pages', config_options.Type(list, default=[])),
        ('autodocs', config_options.Type(dict, default={}),),
    )

    def on_config(self, config):
        # t0 = now()
        ad = self.config['autodocs']
        if ad:
            [autodocs.do_spec(ad, k, v, config, self.stats) for k, v in ad.items()]
        find_pages_and_add_to_nav(self.config['find-pages'], config, self.stats)
        # print(now() - t0)  # = 0.02 for docutools. Could be improved
