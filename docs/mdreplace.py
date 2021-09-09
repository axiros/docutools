import os
import sys
import time

from lcdoc.mkdocs.tools import inline_src_link  # , badge

# not autobuilding anymore, wrote dedicated pages:
# from lcdoc.tools import write_file
# def plugin_docs(**kw):
#     r = []
#     for p, obj in kw['config']['plugins'].items():
#         if not p.startswith('lcd-'):
#             continue
#         doc = sys.modules[obj.__class__.__module__].__doc__
#         if not doc:
#             doc = '## %s Plugin\n\n(no doc)' % p
#         d = 'docs/features/%s' % p.replace('lcd-', '')
#         fn = d + '/index.md'
#         r += [doc]
#     return '\n\n'.join(r)


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
    'plugs_docs': plugs_docs,
    'ctime': time.strftime('%a, %d %b %Y %Hh GMT', time.localtime()),
    'lnksrc': inline_src_link,
    # only prevents the editor from going crazy, with nested code examples in nested code:
    'fences:all:': '```',
}
