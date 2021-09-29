import os
import time
from functools import partial
from hashlib import md5

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import add_post_page_func, make_img
from lcdoc.tools import dirname, exists, read_file, walk_dir, write_file

config, page, Session, stats = (python.config, python.page, python.Session, python.stats)
project = python.project
app = python.app
nocache = True  # we always need to embed the svg into the html, need to be called.
now = time.time


def register(fmts):
    """registering us as renderer for show(<pyplot module>) within lp python"""
    fmts['call_flow'] = call_flow_log


def call_flow_log(s, call, trace, **inner_kw):
    import lcdoc.call_flows.call_flow_logging as cfl
    from lcdoc.mkdocs.lp.plugs.kroki import run as kroki_run

    kw = python.lpkw()
    trace = [trace] if not isinstance(trace, list) else trace

    use_case = '_'.join([t.__name__ for t in trace])
    call_name = call.__name__
    os.environ['PYTEST_CURRENT_TEST'] = 'fakepytest.py::%s' % use_case
    dest = project.root() + '/build/autodocs/%s/%s.md' % (kw['id'], use_case)
    python.write_file(dest, '', mkdir=True)
    f = cfl.document(call, dest=dest)

    # this creates all infos, incl. plantuml within autodocs dir in /build:
    f(call, trace=trace)()

    # we need to embed the svg, only then mouseovers work.
    # But we embedd the svg only later, after html is there, avoids many problems with
    # html conversion:
    from .svg import embed_svgs

    page_ = page()
    add_post_page_func(python.Session.kw, embed_svgs, once=True)

    # Now every svg may have its own params, e.g. server, plantuml style.
    # so we parametrize a kroki plantuml partial for each of them and add to the page:
    # Main mess is to find out the actual filename, relative to us but also absolut:
    # (relative needed since the svg will also be created within site dir)

    d = config()['docs_dir'] + '/autodocs'
    if not exists(d):
        frm = project.root() + '/build/autodocs/'
        app.info('Symlink', frm=frm, to=d)
        os.symlink(frm, d)

    d = dict(Session.kw)
    d['mode'] = 'kroki:plantuml'
    pth_up = '../' * (len(page_.file.src_path.split('/')) - 1)
    fn = 'autodocs/%s/%s/run_lp_flow.%s/call_flow'
    t = kw['id'], use_case, call_name
    d['fn'] = fn = fn % t
    pth_d = pth_up + fn.rsplit('/', 1)[0]

    uml = read_file(config()['docs_dir'] + '/' + fn + '.plantuml')
    d['fn'] = pth_up + fn + '.svg'
    d['add_svg'] = True
    d['page'] = page_
    setattr(page_, 'to_svg_' + kw['id'], partial(kroki_run, uml, d))

    return {'nocache': True, 'res': '\n<lp_svg "%s::%s" />\n' % (kw['id'], pth_d)}
