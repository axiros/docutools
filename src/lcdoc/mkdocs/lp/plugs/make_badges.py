"""
###  `make_badges`

Creates badges. Optionally writes the README.md

#### Parameters

- write_readme: Create the readme with static badges.

"""


import json
import os
import readline
from functools import partial

import anybadge as ab

from lcdoc.mkdocs.tools import src_link
from lcdoc.tools import app, dirname, exists, now, os, project, read_file, write_file

multi_line_to_list = True

# class badges:
#     """We must the eval results statically into the source - otherwise README won't work"""

#     def gh_action(a, kw):
#         # a e.g. 'ci'
#         fn = kw['page'].file.abs_src_path
#         md = read_file(fn)
#         # md = kw['markdown']
#         config = kw['config']
#         ru = config['repo_url']
#         while ru.endswith('/'):
#             ru = ru[:-1]
#         y = '%s/actions/workflows/%s.yml' % (ru, a)
#         r = '[![%s](%s/badge.svg)][%s]' % (a, y, a)
#         if r in md:
#             return ''
#         b = '<!-- badges'
#         l = md.split(b, 1)
#         if not len(l) == 2:
#             app.die('have badges within a "<-- badges" html comment block')
#         k = l[1].split('-->', 1)
#         md = l[0] + r + '\n' + b + k[0] + '-->\n\n[%s]: %s\n\n' % (a, y) + k[1]
#         app.warning('Writing file with static badges links', fn=fn, badge=a, url=y)
#         write_file(fn, md)
#         return r


config = lambda kw: kw['LP'].config

no_end_slash = lambda s: s if not s[-1] == '/' else s[:-1]


class badges:
    def axblack(spec, kw):
        return dict(
            lnk='https://pypi.org/project/axblack/',
            label='code_style',
            value='axblack',
            color='#222222',
        )

    def gh_action(spec, kw):
        a = spec['action']
        ru = no_end_slash(config(kw)['repo_url'])
        u = '%s/actions/workflows/%s.yml' % (ru, a)
        i = '%s/badge.svg' % u
        return dict(lnk=u, img=i, label='gh-' + a)

    def pypi(spec, kw):
        lnk = project.packagehome()
        value = project.version()
        label = 'pypi' if value.startswith('https://pypi.org') else 'pkg'
        color = '#8bd124'
        return dict(locals())


def make_badge_svg_file(badge_fn, label, value, color='gray', **kw):
    p = partial(ab.Badge, label=label, value=value, text_color='white')

    if not isinstance(color, dict):
        badge = p(default_color=color)
    else:
        badge = p(thresholds=color)
    write_file(badge_fn, badge.badge_svg_text, mkdir=True, only_on_change=True)


def write_readme(page, config):
    fn = project.root(config) + '/README.md'
    write_file(fn, page.markdown, only_on_change=True)
    app.warning('Have written README', fn=fn)


def run(cmd, kw):
    # prevents mkdocs serve loops, this counts up, changing the svgs all the time:
    ab.Badge.mask_id = 0
    project.root(config(kw))
    project.load_config()
    specs = []
    for spec in cmd:
        func = getattr(badges, spec['cmd'].replace('-', '_'))
        d = func(spec, kw)
        for k in d:
            spec[k] = spec.get(k) or d[k]
        if not spec.get('img'):
            bdg = 'badge_%(cmd)s.svg' % spec
            fn = dirname(kw['LP'].page.file.abs_src_path) + '/img/' + bdg
            spec['badge_fn'] = fn
            # need an absolute path for the readme.md:
            u = no_end_slash(config(kw)['site_url'])  # +  './img/' + bdg
            k = dirname(kw['LP'].page.file.src_path) or '/'
            u = no_end_slash(u + k) + '/img/' + bdg
            spec['img'] = u
            make_badge_svg_file(**spec)
        specs.append(spec)
    r = ''
    l = []
    for s in specs:
        r += '[![%(label)s][%(label)s_img]][%(label)s] ' % s
        l += ['[%(label)s]: %(lnk)s' % s]
        l += ['[%(label)s_img]: %(img)s' % s]
    l = '\n'.join(l)
    if kw.get('write_readme'):
        p = kw['LP'].page
        p.lp_on_post_page = partial(write_readme, page=p, config=config(kw))
    return {'res': specs, 'formatted': '\n'.join(['', r, '', l, ''])}
