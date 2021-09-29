import os, sys, socket, time
import inspect
from lcdoc.call_flows import markdown as MD
from lcdoc.tools import write_file, read_file, exists

T = MD.Mkdocs
h = lambda level, s: '#' * level + ' ' + s
source = inspect.getsource

auto_gen_cmt = '''
<!-- AUTOMATICALLY GENERATED FILE - DO NOT DIRECTLY EDIT!

Direct edits will be gone after next CI build.
By: %s@%s (%s)
Command Line (see duties.py):

    %s
-->
'''


def mark_auto_created(fn):
    from devapp.app import app

    if exists(fn):
        s = read_file(fn)
    else:
        s = fn
    h = auto_gen_cmt % (
        os.environ.get('USER'),
        socket.gethostname(),
        time.ctime(),
        ' '.join(sys.argv).replace(' -', ' \\\n     -'),
    )
    s = h.lstrip() + '\n' + s
    if exists(fn):
        write_file(fn, s)
    app.info('Marked content as autocreated')
    return s


def recurse_into(obj, md, hir=1):
    """obj a module or class"""
    code = source(obj)
    docu_obj(obj, md, hir, code)
    if hir == 1:
        md.append('## Use Cases')
        hir += 1
    # we don't recurse anymore into the module makes no sense too fragmeneted, reading the whole source is better
    # return
    # cs = classes_by_line_nr(obj, code)
    # if cs:
    #     md.append(MD.header('Classes', hir + 1))
    #     for _, c in sorted(cs.items()):
    #         recurse_into(c, md, hir + 2)

    # fs = functions_by_line_nr(obj, code)
    # if fs:
    #     md.append(MD.header('Functions', hir + 1))
    #     for _, f in sorted(fs.items()):
    #         docu_obj(f, md, hir + 2, source(f))


def name(obj):
    n = getattr(obj, '__qualname__', '') or getattr(obj, '__name__')
    return n.rsplit('.', 1)[-1]


def docu_obj(obj, md, hir, code):
    ds = obj.__doc__ or ''
    h, doc = MD.extract_docstr_head(ds)
    h = '%s' % h  # , name(obj))
    md.append(MD.header(h, hir))
    md.append(doc)
    src = T.code('python', code)
    md.append(T.closed_admon('%s source code' % name(obj), src))


def module_name(obj):
    return obj.__name__ if inspect.ismodule(obj) else obj.__module__


def in_same_module(obj1, obj2):
    """Don't document stuff outside a containing module"""
    return module_name(obj1) == module_name(obj2)


def childs(obj, typ):
    cs = [k for k in dir(obj) if not k.startswith('_')]
    cs = [getattr(obj, k) for k in cs]
    return [c for c in cs if typ(c) and in_same_module(obj, c)]


def classes_by_line_nr(obj, code):
    cs = childs(obj, inspect.isclass)
    r = {}
    for c in cs:
        line = code.split('class %s' % c.__name__, 1)
        if len(line) == 1:
            continue
        line = len(line[0].splitlines())
        r[line] = c
    return r


def functions_by_line_nr(obj, code):
    def filt(f):
        return inspect.ismethod(f) or inspect.isfunction(f)

    fs = childs(obj, filt)
    r = {}
    for f in fs:
        line = code.split('def %s' % name(f), 1)
        if len(line) == 1:
            continue
        line = len(line[0].splitlines())
        r[line] = f
    return r


def mod_doc(mod, dest='auto'):

    from lcdoc.call_flow_logging import autodoc_dir

    d = autodoc_dir(mod, dest)
    os.makedirs(d, exist_ok=True)
    fn = d + '/%s.md' % mod.__name__
    md = []
    recurse_into(mod, md)
    c = '\n'.join(md)
    write_file(fn, c)
    return fn
