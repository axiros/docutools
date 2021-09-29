import os, json, sys, time
from lcdoc.tools import exists, project, write_file, read_file, to_list
import inspect, shutil
from functools import partial, wraps
from lcdoc.call_flows.call_flow_charting import make_call_flow_chart

from lcdoc.call_flows.markdown import Mkdocs, deindent, to_min_header_level

from pprint import pformat

from inflection import humanize

from importlib import import_module
from .auto_docs import mod_doc


# ------------------------------------------------------------------------------ tools
now = time.time


class ILS:
    """
    Call Flow Logger State

    Normally populated/cleared at start and end of a pytest.
    """

    traced = set()  # all traced code objects
    max_trace = 100
    call_chain = _ = []
    counter = 0
    calls_by_frame = {}
    parents = {}
    parents_by_code = {}
    doc_msgs = []
    # sources = {}

    # wrapped = {}

    def clear():
        ILS.max_trace = 100
        ILS.call_chain.clear()
        ILS.calls_by_frame.clear()
        ILS.counter = 0
        ILS.traced.clear()
        ILS.parents.clear()
        ILS.parents_by_code.clear()
        ILS.doc_msgs.clear()


def call_flow_note(msg, **kw):
    msg = json.dumps([msg, kw], indent=2) if kw else msg
    s = {
        'input': None,
        'fn_mod': 'note',
        'output': None,
        'thread_req': thread(),
        'name': msg,
        't0': now(),
    }
    ILS.call_chain.append(s)


def unwrap_partial(f):
    while hasattr(f, 'func'):
        f = f.func
    return f


from threading import current_thread

thread = lambda: current_thread().name.replace('ummy-', '').replace('hread-', '')


class SetTrace:
    """
    sys.settrace induced callbacks are passed into this
    (when the called function is watched, i.e. added to ILS.traced)
    """

    def request(frame):
        if ILS.counter > ILS.max_trace:
            call_flow_note('Reached max traced calls count', max_trace=ILS.max_trace)
            sys.settrace(None)
            return
        ILS.counter += 1

        # need to do (and screw time) this while tracing
        co = frame.f_code
        # frm = SetTrace.get_traced_sender(frame)

        # if ILS.counter == 5:
        #     f = frame.f_back
        #     while f:
        #         print('sender', f, inp)
        #         f = f.f_back

        t0 = now()
        p = ILS.parents_by_code.get(co)
        if p:
            if len(p) == 1:
                n = p[0]
            else:
                n = '%s (%s)' % (p[-1], '.'.join(p[:-1]))
        else:
            n = co.co_name
        inp = dumps(frame.f_locals)
        # inp = ''
        s = {
            'thread_req': thread(),
            'counter': ILS.counter,
            'input': inp,
            'frame': frame,
            'parents': ILS.parents_by_code.get(co),
            'name': n,
            'line': frame.f_lineno,
            't0': now(),
            'dt': -1,
            'output': 'n.a.',
            'fn_mod': co.co_filename,
        }
        ILS.call_chain.append(s)
        ILS.calls_by_frame[frame] = s

    def response(frame, arg):
        try:
            s = ILS.calls_by_frame[frame]
        except Exception as ex:
            return
        s['dt'] = now() - s['t0']
        s['output'] = dumps(arg)
        s['thread_resp'] = thread()
        ILS.call_chain.append(s)

    def tracer(frame, event, arg, counter=0):
        """The settrace function. You can't pdb here!"""
        if not frame.f_code in ILS.traced:
            return
        if event == 'call':
            SetTrace.request(frame)
            # getting a callback on traced function exit:
            return SetTrace.tracer
        elif event == 'return':
            SetTrace.response(frame, arg)


is_parent = lambda o: inspect.isclass(o) or inspect.ismodule(o)
is_func = inspect.isfunction or inspect.ismethod


def trace_object(
    obj,
    pth=None,
    containing_mod=None,
    filters=(
        lambda k: not k.startswith('_'),
        lambda k, v: inspect.isclass(v) or is_func(v),
    ),
    blacklist=(),
):
    """recursive

    partials:
    For now we ignore them, treat them like attributes.
    The functions they wrap, when contained by a traced object will be documented,
    with all args.
    In order to document partials we would have to wrap them into new functions, set into the parent.

    filters: for keys and keys + values
    """
    if is_parent(obj):
        if not pth:
            pth = (obj.__name__,)
            ILS.parents[pth] = obj
            containing_mod = pth[0] if inspect.ismodule(obj) else obj.__module__
        for k in filter(filters[0], dir(obj)):
            v = getattr(obj, k)
            if filters[1](k, v):
                pth1 = pth + (k,)
                ILS.parents[pth1] = v
                trace_object(v, pth1, containing_mod, filters, blacklist)
    elif is_func(obj):
        spth = str(pth) + str(obj)
        if any([b for b in blacklist if b in spth]):
            # TODO: Just return in settrace and write the info into the spec of the call:
            print('blacklisted for tracing', str(obj))
            return

        if containing_mod and not obj.__module__.startswith(containing_mod):
            return
        co = obj.__code__
        ILS.parents_by_code[co] = pth
        ILS.traced.add(co)
        # print(obj)


def trace_func(traced_func, settrace=True):
    """trace a function w/o context"""
    func = unwrap_partial(traced_func)
    ILS.traced.add(func.__code__)
    # collector = collector or ILS.call_chain.append
    if settrace:
        sys.settrace(SetTrace.tracer)  # partial(tracer, collector=collector))


# we already dumps formatted, so that the js does not need to parse/stringify:
def dumps(s):
    try:
        return json.dumps(s, default=str, indent=4, sort_keys=True)
    except Exception as ex:
        # sorting sometimes not works (e.g. 2 classes as keys)
        return pformat(s)


fmts = {'mkdocs': Mkdocs}


def autodoc_dir(mod, _d_dest):
    if _d_dest != 'auto':
        return _d_dest

    if not inspect.ismodule(mod):
        breakpoint()  # FIXME BREAKPOINT
        raise
    modn, fn = mod.__name__, mod.__file__

    r = project.root()
    if fn.startswith(r):
        # fn '/home/gk/repos/lc-python/tests/operators/test_build.py' -> tests/operators:
        d_mod = fn.rsplit(r, 1)[1][1:].rsplit('/', 1)[0]
    else:
        d_mod = modn.replace('.', '/')
    _d_dest = project.root() + '/build/autodocs/' + d_mod
    return _d_dest


flag_defaults = {}


def set_flags(flags, unset=False):
    if not unset:
        try:
            FLG.log_level  # is always imported
        except UnparsedFlagAccessError:
            from devapp.app import init_app_parse_flags

            init_app_parse_flags('pytest')
            for k in dir(FLG):
                flag_defaults[k] = getattr(FLG, k)
        M = flags
    else:
        M = flag_defaults

    return [setattr(FLG, k, v) for k, v in M.items()]


import os
from functools import partial


def pytest_plot_dest(dest):
    cur_test = lambda: os.environ['PYTEST_CURRENT_TEST']
    # if os.path.isfile(dest):
    fn_t = cur_test().split('.py::', 1)[1].replace('::', '.').replace(' (call)', '')
    dest = dest.rsplit('.', 1)[0] + '/' + fn_t

    # fn_t = cur_test().rsplit('/', 1)[-1].replace(' (call)', '')
    # '%s/%s._plot_tag_.graph_easy.src' % (dest, fn_t)
    return dest + '/_plot_tag_.graph_easy.src'


def plot_build_flow(dest):
    f = {
        'plot_mode': 'src',
        'plot_before_build': True,
        'plot_write_flow_json': 'prebuild',
        'plot_after_build': True,
        'plot_destination': partial(pytest_plot_dest, dest=dest),
    }
    return f


def add_doc_msg(msg, code=None, **kw):
    if code:
        T = fmts[kw.pop('fmt', 'mkdocs')]
        c = T.code(kw.pop('lang', 'js'), code)
        msg = (T.closed_admon if kw.pop('closed', 0) else T.admon)(msg, c, 'info')
        kw = None
    ILS.doc_msgs.append([msg, kw])


def document(
    trace,
    max_trace=100,
    fmt='mkdocs',
    blacklist=(),
    call_seq_closed=True,
    flags=None,
    dest=None,
):
    """
    Decorating call flow triggering functions (usually pytest functions) with this

    dest:
    - if not a file equal to d_dest below
    - if file: d_dest is dir named file w/o ext. e.g. /foo/bar.md -> /foo/bar/


    """

    def check_tracable(t):
        if (
            not isinstance(t, type)
            and not callable(t)
            and not getattr(type(t), '__name__') == 'module'
        ):
            raise Exception('Can only trace modules, classes and callables, got: %s' % t)

    [check_tracable(t) for t in to_list(trace)]
    if not dest:
        # dest is empty if env var make_autodocs is not set.
        # Then we do nothing.
        # noop if env var not set, we don't want to trace at every pytest run, that
        # would distract the developer when writing tests:
        def decorator(func):
            @wraps(func)
            def noop_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return noop_wrapper

        return decorator

    ILS.max_trace = max_trace  # limit traced calls

    # this is the documentation tracing decorator:
    def use_case_deco(use_case, trace=trace):
        def use_case_(*args, _dest=dest, _fmt=fmt, **kwargs):
            n_mod = use_case.__module__
            if os.path.isfile(_dest):
                fn_md_into = _dest
                _d_dest = _dest.rsplit('.', 1)[0]
                os.makedirs(_d_dest, exist_ok=True)
            else:
                raise NotImplementedError(
                    'derive autodocs dir when no mod was documented'
                )
                # _d_dest = autodoc_dir(n_mod, dest)
                # fn_md_into = (d_usecase(_d_dest, use_case) + '.md',)

            n = n_func(use_case)
            fn_chart = n
            blackl = to_list(blacklist)
            if max_trace and trace:
                [trace_object(t, blacklist=blackl) for t in to_list(trace)]
                trace_func(use_case)
            flg = {}
            if flags:
                for k, v in flags.items():
                    flg[k] = v() if callable(v) else v
                set_flags(flg)
            try:
                throw = None
                # set_flags(flags)
                value = use_case(*args, **kwargs)  # <-------- the actual original call
            except SystemExit as ex:
                throw = ex

            set_flags(flags, unset=True)
            doc_msgs = list(ILS.doc_msgs)  # will be cleared in next call:

            write.flow_chart(_d_dest, use_case, clear=True, with_chart=fn_chart)
            T = fmts[fmt]
            src = deindent(inspect.getsource(use_case)).splitlines()
            while True:
                # remove decorators:
                if src[0].startswith('@'):
                    src.pop(0)
                else:
                    break
            src = '\n'.join(src)

            # if the test is within a class we write the class as header and add the
            # funcs within:
            min_header_level, doc = 4, ''
            # n .e.g. test_01_sock_comm
            if '.' in n:
                min_header_level = 5
                section, n = n.rsplit('.', 1)
                have = written_sect_headers.setdefault(n_mod, {})
                if not section in have:
                    doc += '\n\n#### ' + section
                    have[section] = True

            doc += '\n\n'
            n_pretty = n.split('_', 1)[1] if n.startswith('test') else n
            n_pretty = humanize(n_pretty)

            # set a jump mark for the ops reference page (doc pp):
            _ = pytest_plot_dest(_dest).split('/autodocs/', 1)[1].rsplit('/', 1)[0]
            doc += '\n<span id="%s"></span>\n' % _

            ud = deindent(strip_no_ad(use_case.__doc__ or ''))
            _ = to_min_header_level
            doc += _(min_header_level, deindent('\n\n#### %s\n%s' % (n_pretty, ud)))

            n = use_case.__qualname__
            f = flg.get('plot_destination')
            if f:
                doc += add_flow_json_and_graph_easy_links(f, T)

            _ = T.closed_admon
            doc += _(n + ' source code', T.code('python', strip_no_ad(src)))

            # call flow plots only when we did trace anythning:
            if max_trace and trace:
                # m = {'fn': fn_chart}
                # svg_ids[0] += 1
                # m['id'] = svg_ids[0]
                # v = '[![](./%(fn)s.svg)](?src=%(fn)s&sequence_details=true)' % m
                # v = '![](./%(fn)s.svg)' % m  # ](?src=%(fn)s&sequence_details=true)' % m
                # v = (
                #     '''
                # <span class="std_svg" id="std_svg_%(id)s">
                # <img src="../%(fn)s.svg"></img>
                # </span>'''
                #     % m
                # )
                #![](./%(fn)s.svg)' % m  # ](?src=%(fn)s&sequence_details=true)' % m
                tr = [name(t) for t in to_list(trace)]
                tr = [t for t in tr if t]
                tr = ', '.join(tr)

                _ = call_seq_closed
                adm = T.closed_admon if _ else T.clsabl_admon
                # they are rendered and inserted at doc pre_process, i.e. later:
                fn = '%s/%s/call_flow.svg' % (fn_md_into.rsplit('.', 1)[0], fn_chart)
                fn = fn.rsplit('/autodocs/', 1)[1]
                svg_placeholder = '[svg_placeholder:%s]' % fn

                #                 svg = (
                #                     read_file('%s/%s.svg' % (os.path.dirname(fn_md_into), fn_chart))
                #                     .split('>', 1)[1]
                #                     .strip()
                #                     .split('<!--MD5', 1)[0]
                #                 )
                #                 if not svg.endswith('</svg>'):
                #                     svg += '</g></svg>'
                #                 id = '<svg id="%s" class="call_flow_chart" ' % fn_chart
                #                 svg = svg.replace('<svg ', id)
                doc += adm('Call Sequence `%s` (%s)' % (n, tr), svg_placeholder, 'info')

            # had doc_msgs been produced during running the test fuction? Then append:
            for d in doc_msgs:
                if not d[1]:
                    doc += '\n\n%s\n\n' % d[0]
                else:
                    doc += '\n%s%s' % (d[0], T.code('js', json.dumps(d[1], indent=4)))

            # append our stuffs:
            s = read_file(fn_md_into, dflt='')
            if s:
                doc = s + '\n\n' + doc
            write_file(fn_md_into, doc)

            # had the function been raising? Then throw it now:
            if throw:
                raise throw

            return value

        return use_case_

    return use_case_deco


# svg_ids = [0]


def strip_no_ad(s, sep='# /--'):
    if not sep in s:
        return s
    r, add, lines = [], True, s.splitlines()
    while lines:
        l = lines.pop(0)
        if l.strip() == sep:
            add = not add
            continue
        if not add:
            continue
        r.append(l)
    return ('\n'.join(r)).strip()


written_sect_headers = {}


def import_mod(test_mod_file):
    """
    """
    if not 'pytest' in sys.argv[0]:
        return

    if not '/' in test_mod_file:
        test_mod_file = os.getcwd() + '/' + test_mod_file
    d, fn = test_mod_file.rsplit('/', 1)
    sys.path.insert(0, d) if not d in sys.path else 0
    mod = import_module(fn.rsplit('.py', 1)[0])

    fn_md = mod_doc(mod, dest='auto')
    return fn_md


def init_mod_doc(fn_mod):
    """convenience function for test modules"""
    # cannot be done via FLG, need to parse too early:
    if not os.environ.get('make_autodocs'):
        return None, lambda: None
    fn_md = import_mod(fn_mod)
    plot = lambda: plot_build_flow(fn_md)
    return fn_md, plot


def add_flow_json_and_graph_easy_links(fn, T):
    """
    The flags had been causing operators.build to create .graph_easy files before and after build
    and also flow.json files for the before phase.

    Now add those into the markdown.
    """
    # fn like '/home/gk/repos/lc-python/build/autodocs/tests/operators/test_op_ax_socket/test01_sock_comm/_plot_tag_.graph_easy.src'
    d = os.path.dirname(fn)
    ext = '.graph_easy.src'
    # pre = fn.rsplit('/')[-1].split('_plot_tag_', 1)[0]

    def link(f, d=d):
        """Process one plot"""
        fn, l = d + '/' + f + '.flow.json', ''
        s = read_file(fn, dflt='')
        if s:
            p = '\n\n> copy & paste into Node-RED\n\n'
            l = T.closed_admon('Flow Json', p + T.code('js', s), 'info')
            # os.unlink(fn) # will be analysed by ops refs doc page
        s = f.replace(ext, '')
        dl = d.rsplit('/', 1)[-1]
        r = '\n\n![](./%s/%s.svg)\n\n' % (dl, s)
        # when s = 'test_build.py::Sharing::test_share_deep_copy.tests.post_build.svg'
        # then n = 'tests.post_build':
        if l:
            return l + r
        else:
            return T.closed_admon(s, r, 'note')

    ge = [link(f) for f in sorted(os.listdir(d)) if f.endswith(ext)]
    return '\n'.join(ge)


n_func = lambda func: func.__qualname__.replace('.<locals>', '')
d_usecase = lambda d_dest, use_case: d_dest + '/' + n_func(use_case)


def name(obj):
    qn = getattr(obj, '__name__', None)
    if qn:
        return qn
    qn = str(qn)
    return obj.replace('<', '&lt;').replace('>', '&gt;')


class write:
    def flow_chart(d_dest, use_case, clear=True, with_chart=False):
        if clear:
            sys.settrace(None)

        root_ = project.root()
        # we log all modules:
        mods = {}
        # and all func sources:
        sources = {}
        # to find input and output
        have = set()
        os.makedirs(d_usecase(d_dest, use_case), exist_ok=True)
        _ = write.arrange_frame_and_write_infos
        flow_w = [
            _(call, use_case, mods, sources, root_, d_dest, have)
            for call in ILS.call_chain
        ]
        _ = make_call_flow_chart
        fn_chart = _(flow_w, d_dest, fn=with_chart, ILS=ILS) if with_chart else 0
        # post write, clear for next use_case:
        ILS.clear() if clear else 0
        return fn_chart

    def arrange_frame_and_write_infos(call, use_case, mods, sources, root, d_dest, have):
        """Creates
        [<callspec>, <input>, None] if input
        [<callspec>, None, <output>, None] if output
        (for the flow chart)

        and writes module and func/linenr files plus the data jsons
        """
        l = [call]
        frame = call.get('frame')
        if frame in have:
            # the output one, all other infos added already
            have.add(frame)
            l.extend([None, call.pop('output', '-')])
            return l
        have.add(frame)
        fn = call['fn_mod']
        if fn == 'note':
            return [call, 'note', None]
        d_mod = mods.get(fn)
        if not d_mod:
            d_mod = mods[fn] = write.module_filename_relative_to_root(fn, root)
            os.makedirs(d_dest, exist_ok=True)
            shutil.copyfile(fn, d_dest + '/' + d_mod[0])
        d = d_mod[0]
        call['pth'] = d_mod[1]
        call['fn_mod'] = d.rsplit('/', 1)[-1]
        func = sources.get(frame)
        if not func:
            src = inspect.getsource(frame)
            src = deindent(src)
            func_name = frame.f_code.co_name
            if 'lambda' in func_name:
                func_name = src.split(' = ', 1)[0].strip()
            fn_func = '%s.%s.func.py' % (d, call['line'])
            write_file(d_dest + '/' + fn_func, src)
            sources[frame] = func = (fn_func, func_name)
        fn_func, func_name = func
        d = d_usecase(d_dest, use_case)

        m = {
            'line': call['line'],
            'fn_func': fn_func,
            'fn_mod': d_mod[0],
            'dt': call['dt'],
            'name': func_name,
            'mod': '.'.join(d_mod[1]),
        }
        spec = [json.dumps(m), call['input'], call['output']]
        fn = call['fn'] = '%s/%s.json' % (d, call['counter'])
        write_file(fn, '\n-\n'.join(spec))
        # s = json.dumps(call, default=str)
        l.extend([call.pop('input'), None])
        return l

    def module_filename_relative_to_root(fn, root):
        d = (fn.split(root, 1)[-1]).replace('/', '__').rsplit('.py', 1)[0][2:]
        pth = d.split('__')
        return (d + '.mod.py'), pth
