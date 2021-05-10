import sys, os
from lcdoc.auto_docs import mod_doc
from importlib import import_module
from devapp.tools import FLG


# def gen_mod_doc(test_mod_file):
#     """
#     """
#     if not 'pytest' in sys.argv[0]:
#         return

#     if not FLG.make_autodocs:
#         return
#     if not '/' in test_mod_file:
#         test_mod_file = os.getcwd() + '/' + test_mod_file
#     d, fn = test_mod_file.rsplit('/', 1)
#     sys.path.insert(0, d) if not d in sys.path else 0
#     mod = import_module(fn.rsplit('.py', 1)[0])

#     fn_md = mod_doc(mod, dest='auto')
#     return fn_md


# from devapp.app import app
# import os, json, sys
# from devapp.tools import (
#     FLG,
#     filter_passwords,
#     exists,
#     project,
#     write_file,
#     read_file,
#     dirname,
# )
# from devapp.tools import define_flags
# import inspect


# from theming.formatting import markdown

# T = markdown.Mkdocs


# class Skip(Exception):
#     pass


# class S:
#     """state - set for each test func's call to def build_pipeline"""

#     n_mod = None
#     n_func = None
#     n_cls = None
#     mod = None
#     cls = None
#     func = None
#     fn_doc = None
#     d_root = None


# from devapp.tools import deindent


# from inflection import humanize


# details = lambda s, b: T.details % (s, b)


# def incr_header_levels(s, min_levels):
#     s = '\n' + s
#     return s.replace('\n#', '\n' + min_levels * '#')


# def add_doc(body):
#     with open(S.fn_doc, 'a') as fd:
#         fd.write(body)


# source = lambda src: details('Source code', T.py % src)


# def do_mod():
#     def find_mod(fn):
#         for k, v in sys.modules.items():
#             if (getattr(v, '__file__', None) or '').endswith(fn):
#                 return v

#     S.mod = mod = find_mod(S.n_mod)
#     # fn = lambda n: DTB() + '/' + n
#     if not getattr(mod, 'is_auto_doc_file'):
#         raise Skip(S.n_mod)
#     fn = S.mod.__file__
#     S.d_root = S.d_root or project.root()
#     f = fn.split(S.d_root, 1)[1][1:].rsplit('.py', 1)[0] + '.md'
#     S.fn_doc = os.path.join(S.d_root + '/build/autodocs', f)
#     app.info('Generating autodoc file', fn=S.fn_doc)
#     b = mod.__doc__
#     if not b.strip():
#         b = '# %s' % mod.__name__
#     b += source(read_file(fn))
#     write_file(S.fn_doc, b, mkdir=1)


# def do_cls():
#     b = '\n\n## %s\n\n' % S.n_cls
#     S.cls = getattr(S.mod, S.n_cls)
#     b += deindent(S.cls.__doc__ or '')
#     add_doc(b)


# func_title = lambda fn: humanize(fn.split('_', 1)[1])


# def do_func():
#     l, H = (2, 'h2') if not S.n_cls else (3, 'h3')
#     h = '#' * l
#     title = func_title(S.n_func)
#     # b = '<a href="#%s">&nbsp;.</a>' % S.n_func
#     b = '\n\n' + h + ' ' + title + '\n'
#     # b = '\n\n%s %s\n###### %s\n' % ('#' * l, title, S.n_func)
#     p = S.cls if S.n_cls else S.mod
#     S.func = getattr(p, S.n_func)
#     b += incr_header_levels(deindent(S.func.__doc__ or ''), l + 1)
#     # b += add_chart()
#     # b += add_flow()
#     b += source(inspect.getsource(S.func))
#     add_doc(b)


# def register_new_test_func(pyt):
#     l = pyt.split('::')
#     funcs = []
#     mod = l[0]
#     funcs.append(do_mod) if mod != S.n_mod else 0
#     S.n_mod = mod
#     cls = None
#     if len(l) > 2:
#         cls = l[1]
#         funcs.append(do_cls) if cls != S.n_cls else 0
#     S.n_cls = cls
#     S.n_func = l[-1].replace('(call)', '').strip()
#     funcs.append(do_func)
#     return funcs


# def gen_func_doc():

#     """We generate the markdown docs while running pytest process
#     - we generate graph specs and write flow files for out of process analysis

#     """
#     pyt = os.environ.get('PYTEST_CURRENT_TEST')
#     if not pyt:
#         app.die('This is not a pytest run - cannot generate build doc')
#     breakpoint()  # FIXME BREAKPOINT
#     return [f() for f in register_new_test_func(pyt)]


# from decorator import decorate
