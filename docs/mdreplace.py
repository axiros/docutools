import sys, os
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


def plugs_docs(**kw):
    from lcdoc.tools import project
    from importlib import import_module

    res = []
    r = project.root(kw['config'])
    for p in sorted(os.listdir(r + '/src/lcdoc/mkdocs/lp/plugs')):
        if not p.endswith('.py'):
            continue
        mod = import_module('lcdoc.mkdocs.lp.plugs.%s' % p.split('.py', 1)[0])
        res += [str(mod.__doc__) or '### %s' % p]
    return '\n\n'.join(res)


table = {
    'plugin_docs': plugin_docs,
    'plugs_docs': plugs_docs,
    'ctime': time.ctime(),
    'lnk_src': inline_src_link,
    'fences:all:': '```',
}
