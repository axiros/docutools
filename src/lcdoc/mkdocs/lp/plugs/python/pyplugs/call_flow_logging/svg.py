import os
import time

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.tools import exists

config, page, Session, stats = (python.config, python.page, python.Session, python.stats)
project = python.project
app = python.app

now = time.time


def embed_svgs(output, page, config, **kw):
    """post page hook
    During show we inserted markers for the images, like:

    return {'nocache': True, 'res': '\n<lp_svg "%s::%s" />\n' % (kw['id'], pth_d)}

    Now, after html, we replace those with a embedded svgs from the build filesystem.
    """
    dt = config['docs_dir'] + '/autodocs'
    if not exists(dt):
        os.symlink(project.d_autodocs(), dt)

    o = output.split('<lp_svg "')
    if len(o) == 1:
        return
    r = o[0]
    for part in o[1:]:
        id, rest = part.split('" />', 1)
        id, pth = id.split('::')
        # was added by the show function
        kroki_run = getattr(page, 'to_svg_' + id)
        svg = kroki_run()['svg']
        svg = svg.split('<svg', 1)[1]
        t = '<svg id="%s" pth_rel="%s/" class="call_flow_chart" '
        svg = (t % (id, pth)) + svg
        svg = svg.split('<!--MD5', 1)[0]
        if not svg.endswith('</svg>'):
            svg += '</g></svg>'
        r += '\n' + svg + '\n' + rest
    return r
