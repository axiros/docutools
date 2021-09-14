import os
import sys
import time

from lcdoc.mkdocs.tools import srcref  # , badge

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


table = {
    'ctime': time.strftime('%a, %d %b %Y %Hh GMT', time.localtime()),
    'srcref': srcref,
    # only prevents the editor from going crazy, with nested code examples in nested code:
    'fences:all:': '```',
}
