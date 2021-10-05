"""
###  `make_badges`

Creates badges. Optionally writes the README.md


#### Format

Line separated badge function names with statement level lp parameters.

Functions:

    - axblack
    - docs (with value=[pagecount], default "mkdocs-material")
    - gh_action (with action parameter, default ci)
    - pypi

Params:

    - value
    - label
    - color
    - lnk
    - img

#### Parameters

- write_readme: Create the readme with static badges.

"""


import json
import os
import readline
from functools import partial

import anybadge as ab

from lcdoc.mkdocs.tools import add_post_page_func, srclink
from lcdoc.tools import (
    app,
    dirname,
    exists,
    now,
    os,
    project,
    read_file,
    write_file,
    insert_file,
)

multi_line_to_list = True

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
        a = spec.get('action', 'ci')
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

    def docs(spec, kw):
        lnk = configured_site_url(kw)
        # lnk = config(kw)['site_url'] # 127.0.0.1 for mkdocs serve
        value = spec.get('value', 'mkdocs-material')
        label = 'docs'
        if value == 'pagecount':
            d = config(kw)['docs_dir']
            spec['value'] = (
                os.popen("cd '%s' && find . | grep 'md$' | wc -l" % d).read().strip()
            )
            label = 'docs pages'
        color = '#331188'
        return dict(locals())

    def generic(spec, kw):
        spec['label'] = spec.get('label', spec['cmd'])
        return dict(spec)


def configured_site_url(kw, c=[0]):
    if not c[0]:
        d = project.root(config(kw))
        d = read_file('%s/mkdocs.yml' % d, dflt='').split('\nnav:', 1)[0]
        c[0] = yaml.safe_load(d)['site_url']
    return c[0]


import yaml


def make_badge_svg_file(badge_fn, label, value, color='gray', **kw):
    p = partial(ab.Badge, label=label, value=value, text_color='white')

    if not isinstance(color, dict):
        badge = p(default_color=color)
    else:
        badge = p(thresholds=color)
    write_file(badge_fn, badge.badge_svg_text, mkdir=True, only_on_change=True)


def write_readme(page, config, content=None, **kw):
    # :docs:insert_readme_badges
    fn = project.root(config) + '/README.md'
    insert_file(fn, content, sep='<!-- badges -->')
    app.info('Have inserted badges into README', file=fn)
    # :docs:insert_readme_badges


def run(cmd, kw):
    # prevents mkdocs serve loops, this counts up, changing the svgs all the time:
    ab.Badge.mask_id = 0
    project.root(config(kw))
    project.load_config()
    specs = []
    for spec in cmd:
        func = getattr(badges, spec['cmd'].replace('-', '_'), badges.generic)
        d = func(spec, kw)
        [d.pop(k, 0) for k in ['kw', 'spec']]  # the locals hack
        for k in d:
            spec[k] = spec.get(k) or d[k]
        if not spec.get('img'):
            bdg = 'badge_%(cmd)s.svg' % spec
            fn = dirname(kw['LP'].page.file.abs_src_path) + '/img/' + bdg
            spec['badge_fn'] = fn
            # need an absolute path for the readme.md:
            u = no_end_slash(configured_site_url(kw))
            k = '/' + dirname(kw['LP'].page.file.src_path)
            u = no_end_slash(u + k) + '/img/' + bdg
            spec['img'] = u  # .replace('//', '/')
            try:
                make_badge_svg_file(**spec)
            except Exception as ex:
                app.error('Badge creation failed', exc=ex)
                continue
        specs.append(spec)
    r = ''
    l = []
    for s in specs:
        r += '[![%(label)s][%(label)s_img]][%(label)s] ' % s
        l += ['[%(label)s]: %(lnk)s' % s]
        l += ['[%(label)s_img]: %(img)s' % s]
    l = '\n'.join(l)
    content = '\n'.join(['', r, '', l, ''])
    if kw.get('write_readme'):
        add_post_page_func(kw, partial(write_readme, content=content))

    return {'res': specs, 'formatted': content}
