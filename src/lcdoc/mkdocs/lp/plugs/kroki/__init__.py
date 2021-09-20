"""
Adds kroki support to the page.

"""

import json

import httpx

from lcdoc import lp
from lcdoc.mkdocs.tools import os, make_img
from lcdoc.tools import dirname, os, read_file, exists

dflt_server = 'https://kroki.io/'
dflt_server = os.environ.get('lp_kroki_server', dflt_server)
dflt_puml = os.environ.get('lp_kroki_puml', 'dark_blue')
s = 'mkdocs/lp/'
d_assets = dirname(__file__).split(s, 1)[0] + s + '/assets/plantuml'
pumls = {}


def read_puml_file(fn, kw):
    ofn = fn
    p = pumls.get(fn)
    if p:
        return p
    fnp = dirname(kw['LP'].page.file.abs_src_path)
    if not '/' in fn:
        # default dir:
        fn = '%s/%s.puml' % (d_assets, fn)
    elif fn[0] == '/':
        fn = fn
    else:
        fn = fnp + '/' + fn
    return pumls.setdefault(ofn, read_file(fn, ''))


def run(cmd, kw):
    if not cmd.strip():
        src = kw.get('abs_src')
        if not src:
            return lp.err('Require a diag source')

        if not exists(src):
            return lp.err('Not found', src=src)
        cmd = read_file(src)

    typ = (kw['mode'] + ':plantuml').split(':', 2)[1]
    if typ == 'plantuml':
        cmd = cmd.replace('@startuml', '')
        cmd = cmd.replace('@enduml', '')
        puml = read_puml_file(kw.get('puml', dflt_puml), kw)
        cmd = puml + '\n' + cmd
        cmd = '@startuml\n%s\n@enduml' % cmd

    if isinstance(cmd, (dict, list, tuple)):
        data = json.dumps(cmd)
    else:
        data = cmd
    #    {'diagram_source': cmd, 'diagram_type': typ, 'output_format': 'svg'}
    # )
    server = kw.get('server', dflt_server)
    server = server[:-1] if server[-1] == '/' else server
    server += '/%s/svg' % typ
    res = httpx.post(server, data=data)
    if res.status_code > 299:
        return lp.err(
            'Server returned error',
            status=res.status_code,
            txt=getattr(res, 'text', 'n.a.')[:200],
        )

    res = res.text.replace('\r\n', '\n')
    imglnk = make_img(res, kw=kw)
    return {'res': imglnk, 'formatted': True}
