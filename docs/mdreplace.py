import sys
import time
from lcdoc.mkdocs.tools import inline_src_link


def plugin_docs(**kw):
    r = []
    for p, obj in kw['config']['plugins'].items():
        if not p.startswith('lcd-'):
            continue
        doc = sys.modules[obj.__class__.__module__].__doc__
        if not doc:
            doc = '## %s Plugin\n\n(no doc)' % p
        r += [doc]
    return '\n\n'.join(r)


table = {
    'plugin_docs': plugin_docs,
    'ctime': time.ctime(),
    'lnk_src': inline_src_link,
    'fences:all:': '```',
}
