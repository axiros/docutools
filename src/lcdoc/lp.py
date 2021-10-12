#!/usr/bin/env python
"""
Literate Programming / Language of Babel style

Edit: We support this now not only from emacs but also from normal mkdocs markdown.
See the documentation.



Old emacs centric docs follow:

Org Mode / Mkdocs Helper Script. 

Usage: See e.g. repos/lc/docs/.../getting_started.org

Basics: 
    In you org file have this:


#+BEGIN_SRC python :exports none :results silent :session pyroot
from sys import modules as m; m.pop('lp') if 'lp' in m else 0; import lp
#lp.alias('lcm', '$d_repos/lc/build/make')
run = lp.p(lp.run, fmt='mk_cmd_out')
root = lp.p(run, root=True)
#+END_SRC

which you execute at any change of the module (reloads)

Set this:

:PROPERTIES:
:header-args:python: :session pyroot :exports results :results html
:END:

Then using is like

#+BEGIN_SRC python
root([
      {
        'cmd': 'm -l run lnr -d',
        'expect': '\n/opt/repos/lc/node-red#',
        'timeout': 15,
      },
      {
        'cmd': "ax/start -p ''",
        'expect': 'Started flows',
        'timeout': 10,
        'cmt': "-p '': no project"
      },
      ], new_session='root_nr')
#+END_SRC


"""
import hashlib
import html
import json
import os
import string
import subprocess as sp
import sys
import time
from functools import partial as p
from importlib import import_module

import pycond

from lcdoc import lprunner as mdr
from lcdoc.mkdocs.tools import page_dir
from lcdoc.tools import app, dirname, write_file

# important (colorize)
I = lambda s: s if not sys.stdout.isatty() else '\x1b[1;32m%s\x1b[0m' % s
L = lambda s: s if not sys.stdout.isatty() else '\x1b[0;2;38;5;242m%s\x1b[0m' % s

is_lprunner = [0]
env = os.environ
wait = time.sleep
now = time.time
exists = os.path.exists
user = env.get('USER', 'root')  # in docker: Key error, else.
env['PATH'] = 'bin:%s' % env.get('PATH', '')


_ = lambda f, msg, *a, **kw: f(str(msg) + ' '.join([str(i) for i in a]), **kw)
dbg = p(_, app.debug)
nfo = p(_, app.info)


# ---------------------------------------------------------------------------- Utilities
def check_assert(ass, res):
    def raise_():
        msg = 'Assertion failed: Expected "%s" not found in result' % ass
        app.error(msg, asserts=ass, json={'result': res})
        raise Exception(msg)

    if ass is None:
        return
    s = str(res)
    is_pycond = False
    if isinstance(ass, str) and ' and ' in ass or ' or ' in ass or 'not ' in ass:
        is_pycond = True
    elif isinstance(ass, list) and ass[1] in {'and', 'or'}:
        is_pycond = True
    if is_pycond:

        def f(k, v, state, **kw):
            return (k in state['res'], v)

        r = pycond.pycond(ass, f)
        a = r(state={'res': s})
        if not a:
            raise_()
        return

    if not isinstance(ass, (list, tuple)):
        ass = [ass]

    for a in ass:

        if not a in s:
            raise_()


# aliases = {}
to_list = lambda s: s if isinstance(s, list) else [s]


def repl_dollar_var_with_env_val(s, die_on_fail=True):
    if not '$' in s:
        return s
    for k in env:
        if k in s:
            s = s.replace('$' + k, env[k])
    if '$' in s:
        dbg('Not defined in environ: $%s' % s)
    return s


def spresc(cmd):
    """subprocess run - with escape sequences escaped (for tmux)"""
    return sprun(cmd.encode('unicode-escape'))


def sprun(*a, no_fail=False, report=False, **kw):
    """Running a command as bash subprocess
    W/o executable we crash on ubuntu's crazy dash, which cannot even echo -e
    """
    if report:
        if not kw and len(a) == 1:
            report('', a[0])
        else:
            report('', a, kw)  # for the user (also in view messages)
    show_res = False
    if is_lprunner[0]:
        if isinstance(a[0], str) and not str(a[0]).startswith('tmux'):
            show_res = True
            mdr.confirm('Run %s' % ' '.join(a))

    c = p(sp.check_output, shell=True, stderr=sp.STDOUT, executable='/bin/bash')
    try:
        res = c(*a, **kw)
        if show_res and res:
            print('Result:')
            print(res.decode('utf-8'))
        return res
    except Exception as ex:
        if not no_fail:
            raise
        app.error('Failure', args=a, kw=kw, exc=ex)
        return err(str(ex))


# ----------------------------------------------------------------------- Plugins(modes)

our_plugs = 'lcdoc.mkdocs.lp.plugs'


class plugs:
    pass


def get_or_import_plug(mode):
    p = getattr(plugs, mode, None)
    if p:
        return p
    try:
        p = import_module(mode)
        if not hasattr(p, 'run'):
            raise ModuleNotFoundError('')
    except ModuleNotFoundError:
        try:
            p = import_module(our_plugs + '.' + mode)
        except ModuleNotFoundError as ex:
            msg = ' - If this is a custom module add its directory to your PYTHONPATH'
            raise type(ex)(str(ex) + msg)
    setattr(plugs, mode, p)
    return p


# ------------------------------------------------------------------------------ Formats
# seems we don't need the stupid dot anymore for the javascript xterm part (?)
# mk_cmd_out = '''

# === "Cmd"

#     ```console
#     %(cmds)s
#     ```

#     .

# === "Output"

#     %(ress)s

# '''

mk_console = '''
```%(lang)s
%(cmd)s
%(res)s
```
'''


mk_cmd_out = '''

=== "Cmd"
    
    ```console
    %(cmds)s
    ```

=== "Output"

    %(ress)s

'''


class mk_cmd_out_fetch:
    org = '''


#+begin_tab:Command

#+BEGIN_SRC console :eval no

%(cmds)s

#+END_SRC

#+end_tab:Command


#+begin_tab:Output

%(ress)s

#+end_tab:Output

'''
    mkdocs = mk_cmd_out


xt_flat = '''
<xterm %(root)s/>

    %(ress)s

'''

xt_flat_fetch = '''
    <xterm />

         remote_content

    ![](%(fn_frm)s)
'''


# xt_flat_fetch_test = """
##+begin_tab:foo

#    <xtf %(root)s xtfrm=file:%(fn_frm)s></xtf>

##+end_tab:foo
# """

# this not yet sane:
##+begin_tab:foo

#    <xterm></xterm>

#        ansiremotecontent

#    [ ](file:./media/info_flow_adm.ansi)

##+end_tab:foo


dflt_fmt = 'mk_cmd_out'


class T:
    def xt_flat(resl, **kw):
        add_cmd = kw.get('add_cmd', True)
        root = '' if not kw.get('root') else 'root'
        r = []
        for cr in resl:
            cmdstr, res = get_cmd(cr), cr.get('res')
            if add_cmd and not cmdstr in res:
                res = cmdstr + '\n' + res
            r.append(res)
        ress = '\n'.join(r)
        fetch = kw.get('fetch')
        if fetch:
            fn_frm = kw['fn_frm'] = file_.write_fetchable(ress, **kw)
            t = xt_flat_fetch
            ress = t % locals()
        else:
            ress = ress.replace('\n', '\n    ')
            ress = xt_flat % locals()
        return ress

    def mk_cmd_out(res, **kw):
        root = '' if not kw.get('root') else 'root'

        def add_prompt(c, r, kw=kw):
            """
            We don't do it since console rendering requires $ or # only for syn hilite
            """
            c, cmd = (c.get('cmd'), c) if isinstance(c, dict) else (c, {'cmd': c})
            if c:
                p = kw.get('prompt', '#' if root else '$')
                c = '%s %s' % (p, c)
                cmt = cmd.get('cmt')
                if cmt:
                    if len(c) + len(cmt) > 80:
                        c = '%s # %s:\n%s' % (p, cmt, c)
                    else:
                        c = '%s # %s' % (c, cmt)
            return {'cmdstr': c, 'cmd': cmd, 'res': r}

        ress = T.xt_flat(res, add_cmd=kw.pop('add_cmd', False), **kw)
        res = [add_prompt(m.get('cmd'), m['res']) for m in res]
        if not any([True for m in res if m['cmdstr']]):
            return ress
        cmds = '\n'.join([r['cmdstr'] for r in res if r.get('cmdstr')])
        fetch = kw.get('fetch')
        if fetch:
            t = getattr(mk_cmd_out_fetch, kw['fetched_block_fmt'])
            r = t % locals()
        else:
            # indent one in:
            cmds = cmds.replace('\n', '\n    ')
            ress = ress.replace('\n', '\n    ')
            r = mk_cmd_out % locals()
        return r

    def mk_console(res, root=False, **kw):
        resl = res
        r = []
        lang = kw.get('lang', 'console')
        for res in resl:
            p = ''
            if lang in ['bash', 'sh']:
                p = '# ' if kw.get('root') else '$ '
                p = kw.get('prompt', p)
            cmd = p + get_cmd(res)
            res = res['res']
            # is the command part of the res? then skip print:
            if cmd.strip() == res.strip().split('\n', 1)[0].strip():
                cmd = 'SKIP-PRINT-OUT'
            r.append(mk_console % locals())

        r = ('\n'.join(r)).splitlines()
        r = [l for l in r if not 'SKIP-PRINT-OUT' in l]
        return '\n'.join(r)


T.xtf = T.xt_flat


def get_cmd(res):
    cmd = res.get('cmd', '')
    return get_cmd(cmd) if isinstance(cmd, dict) else cmd


# def alias(k, v):
#     aliases[k + ' '] = v + ' '


def prepare_and_fmt(res, orig_cmd, **kw):
    # allow plugs to do their formatting:
    if isinstance(res, dict) and 'formatted' in res:
        return res['formatted']
    res = to_list(res)
    o = res
    i = -1
    for c in res:
        i += 1
        if not isinstance(c, dict):
            c = res[i] = {}
        if not 'cmd' in c:
            app.debug('Command missing', res=o, cmd=orig_cmd)
            c['cmd'] = orig_cmd
        if not 'res' in c:
            app.error('Result missing', res=o, cmd=orig_cmd)
            c['res'] = 'Not available (%s)' % orig_cmd
        r = c['res']
        if isinstance(r, str):
            c['res'] = r.replace('\n```', '\n ``')
        else:
            c['res'] = json.dumps(r, indent=4)
        if kw.get('hide_cmd'):
            c['cmd'] = ''

    fmt = f = kw.get('fmt', dflt_fmt)
    fmt = getattr(T, fmt, None)
    if not fmt:
        raise Exception(
            'Format not found (%s) - have: %s'
            % (f, [k for k in dir(T) if not k[0] == '_'])
        )
    return fmt(res, **kw)


letters = string.ascii_letters + string.digits + '_'


# ----------------------------------------------------------------------- header parsing
def cast(v):
    if v and v[0] in ('{', '['):
        return json.loads(v)
    try:
        return int(v)
    except:
        try:
            return float(v)
        except:
            return {'true': True, 'false': False}.get(v, v)


apos = ["'", '"']
neutrl_chars = [[' ', '\x01'], [',', '\x02'], ['=', '\x04']]


def neutralize(s, mode=None):
    for f, t in neutrl_chars:
        if mode == 'rev':
            f, t = t, f
        s = s.replace(f, t)
    return s


def parse_kw_str(kws, header_kws=None, try_json=True):
    """for kw via cli"""
    if not kws.strip():
        return {}
    header_kws = {} if header_kws is None else header_kws
    if try_json:
        if kws and kws[0] in ('{', '['):
            try:
                return json.loads(kws)
            except:
                pass
    # neutralize all within apos:
    for apo in apos:
        parts = kws.split('=' + apo)
        s = parts.pop(0)
        while parts:
            s += '='
            p = parts.pop(0)
            l = p.split(apo)
            if not len(l) == 2:
                msg = 'Unparsable apostrophes: %s - %s'
                raise Exception(msg % (kws, apo))
            s += neutralize(l[0]) + l[1]
        kws = s

    # quoted values possible:
    if ', ' in kws:
        raise Exception('No comma allowed')
    kw = {}
    parts = kws.split(' ')
    kw.update(
        {
            p[0]: cast(neutralize(p[1], 'rev'))
            for p in [(k if '=' in k else k + '=true').split('=') for k in parts]
        }
    )
    # breakpoint()  # FIXME BREAKPOINT
    # if '"' in kws or "'" in kws:
    #     r = []
    #     while kw:
    #         k, v = kw.pop(0)
    #         for apo in apos:
    #             if v[0] == apo:
    #                 v = v[1:]
    #                 if v.endswith(apo):
    #                     v = v[:-1]
    #                     break
    #                 while kw:
    #                     nk, _ = kw.pop(0)
    #                     if nk.endswith(apo):
    #                         v += ' ' + nk[:-1]
    #                         break
    #                     else:
    #                         v += ' ' + nk
    #                 break
    #         r.append([k, v])
    #     kw = r
    # kw = {k: cast(v) for k, v in kw}

    kw = {k: header_kws.get(v, v) for k, v in kw.items()}
    return kw


def parse_header_args(header, **ctx):
    """Parsing either python or easy format
    CAUTION: This is used
    - caused here, to parse inline headers ( # lp: ....)
    - in the plugin code as well, to parse markdown headers
    """
    # ctx['dir_repo'] = ctx['fn_lp'].split('/docs/', 1)[0]
    ctx['get_args'] = get_args

    try:
        # if header.rstrip().endswith('"'):
        #    raise Exception("Not tried (apostrophe at end)")
        return 0, ((), parse_kw_str(header, ctx, try_json=False))
    except Exception as ex:
        ex1 = ex
        # evaling now.
        # still - we supply only a minimum eval ctx and prevent
        # imports. But still this won't be totally safe.
        # BUT: Hey - we are about to run code *anyway*, this is LP in the end!
        if not 'import' in header:
            try:
                m = eval('get_args(%s)' % header, ctx, {})
                return 0, (m['args'], m['kw'])
            except Exception as ex:
                ex2 = ex
        return 1, (ex2, ex1)


# ----------------------------------------------------------------------------- sessions


def pb(s):
    try:
        s = s.decode('utf-8')
    except Exception as ex:
        pass
    dbg(s)


def get_args(*a, **kw):
    return {'args': a, 'kw': kw}


def root(cmd, **kw):
    return run(cmd, root=True, **kw)


class file_:
    def write_fetchable(cont, fetch, **kw):
        """write .ansi XTF files"""
        d, fn = kw['fn_doc'].rsplit('/', 1)
        lnk = '/media/%s_%s.ansi' % (fn, fetch)
        fn = d + lnk
        if not exists(d + '/media'):
            os.makedirs(d + '/media')
        s = rpl(cont, kw)
        write_file(fn, s, only_on_change=True)
        return '.' + lnk


def rpl(s, kw):
    'global replacement'
    rpl = kw.get('rpl')
    if rpl:
        if not isinstance(rpl[0], (list, tuple)):
            rpl = [rpl]
        for r in rpl:
            s = s.replace(r[0], r[1])
    return s


def repl_dollar_var_with_env_vals(kw, *keys):
    for k in keys:
        v = kw.get(k)
        if v:
            kw[k] = repl_dollar_var_with_env_val(v)


def multi_line_to_list(cmd):
    """

    ```bash lp session=DO asserts=loadbalancer.tf
    ip () { echo 1.2.3.4; }
    cat << FOO > loadbalancer.tf
    > resource "digitalocean_loadbalancer" "www-lb" {
    >     ipv4 = $(ip)
    >     (...)
    >}
    >FOO
    ls -l
    ```

    """
    if not isinstance(cmd, str):
        return cmd
    lines = cmd.split('\n')
    # when some lines start with ' ' we send the whole cmd as one string:
    if any([l for l in lines if l.strip() and l.startswith(' ')]):
        # echo 'foo
        #      bar' > baz
        return [{'cmd': cmd}]
    r = []
    while lines:
        l = lines.pop(0)
        r.append(l)
        while lines and lines[0].startswith('> '):
            l = lines.pop(0)
            r[-1] += '\n' + l[2:]
    l = [cmd for cmd in r if cmd.strip()]
    return [check_inline_lp(line) for line in l]


def check_inline_lp(cmd):
    if not isinstance(cmd, str):
        breakpoint()  # FIXME BREAKPOINT
        return
    l = cmd.rsplit(' # lp: ', 1)
    if len(l) == 1 or '\n' in l[1]:
        return {'cmd': l[0]}
    err, res = parse_header_args(l[1])
    if err:
        msg = 'Inline lp construct wrong: %s. Valid e.g.: "ls -lta /etc # lp: '
        msg += 'expect=hosts timeout=10". Got: %s %s'
        raise Exception(msg % (cmd, res[0], res[1]))
    res[1]['cmd'] = res[1].get('cmd', l[0])
    return res[1]


def os_system_if_param_present(kw, if_present):
    """utility for a frequent use case"""
    if not isinstance(kw, dict):
        return
    cmd = kw.get(if_present)
    if cmd:
        if os.system(cmd):
            raise Exception('%s run failed: %s. kw: %s' % (if_present, cmd, str(kw)))


def err(msg, **kw):
    app.error(msg, **kw)
    return {'res': {'lp err': msg, 'kw': kw}}


class SessionNS:
    """Namespace for methods related to session parameters

    Including methods when there is no session support
    (but different handling when there is)
    """

    @classmethod
    def init(cls, cmd, kw):
        cls.handle_new_session_param(kw)
        kw['session_name'] = n = kw.pop('session', None)
        cls.pre(n, kw)

    @classmethod
    def handle_new_session_param(cls, kw):
        msg = 'Variable new_session must be string  - (the name of a session which is '
        msg += 'guaranteed a new one)'
        ns = kw.pop('new_session', None)
        if ns == False or isinstance(ns, (int, float)):
            raise Exception(msg)
        if ns == True:
            ns = kw.pop('session')
            if not ns:
                raise Exception(msg)
        if ns:
            cls.delete(ns, kw)
            kw['session'] = ns

    @classmethod
    def delete(cls, session_name, kw):
        raise Exception('No session support', mode=kw.get('mode'))

    @classmethod
    def pre(cls, session_name, kw):
        # pre, if not overwritten here should just os.system it:
        os_system_if_param_present(kw, 'pre')

    @classmethod
    def post(cls, session_name, kw):
        os_system_if_param_present(kw, 'post')


def eval_lp(cmd, kw):
    # deprecated alias, not any more docued, did not work for py style args:
    assert_ = kw.get('asserts') or kw.get('assert')
    mode_chain = kw.get('mode', 'bash').split('|')
    while mode_chain:
        kw['mode'] = mode_chain.pop(0).strip()
        res = eval_single_lp_mode(cmd, kw)
        if mode_chain:
            res = cmd = res.get('result') or res.get('res')
            if isinstance(res, dict) and res.get('header'):
                kw.update(res.get('header'))
                cmd = res.get('body')

    check_assert(assert_, res)
    return res


def eval_single_lp_mode(cmd, kw):
    # `lp:python body='show("http://127.0.0.1:2222")'`:
    if isinstance(cmd, str):
        cmd = kw.get('body', '') + cmd
    full_mode = kw.get('mode', 'bash')
    mode = full_mode.split(':', 1)[0]
    old_name, app.name = app.name, app.name + ':' + mode  # for logging with mode
    plug = get_or_import_plug(mode)
    g = lambda k, d=None: getattr(plug, k, d)
    Session = g('Session', SessionNS)
    Session.init(cmd, kw)

    rk = g('req_kw')
    if rk:
        miss = [k for k in rk if not k in kw]
        if miss:
            return err('Missing required arguments', missing=miss)

    if g('multi_line_to_list'):
        cmd = multi_line_to_list(cmd)
    evl = g('eval')

    kw['fmt'] = kw.get('fmt') or g('fmt_default') or dflt_fmt
    kw['id'] = kw.get('id') or mode + '_%(source_id)s' % kw['LP'].spec

    r = g('run', 'cmd')
    if r == 'cmd':
        res = {'formatted': True, 'res': cmd}
    elif r == 'cmd:escaped':
        res = {'formatted': True, 'res': html.escape(cmd)}
    else:
        res = r(cmd, kw)
    if isinstance(res, str):
        res = {'cmd': cmd, 'res': res}
    if isinstance(res, dict):
        if g('formatted'):
            res['formatted'] = res.get('formatted', True)
        if g('nocache'):
            res['nocache'] = res.get('nocache', True)
        if res.get('formatted') == True:
            res['formatted'] = res['res']
        if evl is not None:
            res['eval'] = evl
        add_assets(res, g('page_assets'), kw, mode)
    Session.post(kw.get('session_name'), kw)
    app.name = old_name
    return res


def add_assets(res, global_assets, kw, mode):
    """
    Adding the page_assets structure into the result. I.e. these are practically part of
    the result of the evaluation - and cached. Therefore present even when res is not
    evaluated.

    - header, footer, md assets in result( res) are executed per block, indexed by block source id
    - those in page_assets per page - they can be declared on module level or are within
      res, key page_assets.
    """
    # shortcut, when the run adds one of these we assume it's per block, with id:
    for k in ['header', 'footer', 'md', 'func']:
        pa = res.get(k)
        if pa:
            res.setdefault('page_assets', {}).setdefault(kw['id'], {})[k] = pa
    # add the global assets - indexed under the current plugin name (mode):
    a = global_assets
    if a:
        m = res.get('page_assets', {})
        # two same mode blocks will not return *different* page assets:
        m[mode] = M = {}
        for k, v in a.items():
            M[k] = v
        res['page_assets'] = m


def run(cmd, fn_doc=None, use_prev_res=None, **kw):
    """
    rpl: global post run replacement
    fn_doc: required: location of source file (async flow links contain its name)
    """
    # in python sigature format assert would be forbidden, so we allow asserts=...
    repl_dollar_var_with_env_vals(kw, 'fn', 'cwd')
    # you could set this to org:
    kw['fetched_block_fmt'] = kw.get('fetched_block_fmt', 'mkdocs')

    assert fn_doc, 'fn_doc run argument missing'
    kw['fn_doc'] = os.path.abspath(fn_doc)

    if use_prev_res:
        res = use_prev_res
    else:

        cwd = kw.get('cwd')
        if cwd:
            here = os.getcwd()
            try:
                os.chdir(cwd)
                # so that replace works in make_file:
                os.environ['PWD'] = cwd
            except Exception as ex:
                ex.args += ('dest dir: "%s"' % cwd,)
                raise
        try:
            res = eval_lp(cmd, kw)
            if isinstance(res, str):
                res = {'cmd': cmd, 'res': res}
        finally:
            # cwd header only for the current block:
            if cwd:
                os.chdir(here)

    ret = {'raw': res}

    if not kw.get('silent'):
        res = prepare_and_fmt(res, orig_cmd=cmd, **kw)
        res = rpl(res, kw)
    else:
        res = ''
    res = add_src(res, kw)

    ret['formatted'] = res
    return ret


block_indent = lambda s, i: s.replace('\n', '\n' + (' ' * i))


def add_src(res, kw):
    i = kw.get('addsrc', 0)
    title = ' '
    if not i:
        return res
    try:
        i = int(i)
    except:
        title = i
        i = 4

    b = '\n' + kw.get('sourceblock', 'n.a.')
    b_shortform = b.split('```shortform ', 1)[-1]
    if b_shortform.startswith('lp:'):
        b_shortform = b_shortform.split('\n', 1)[0]
        i = 3
    t = kw.get('title', title)
    if isinstance(i, str) and not i.isdigit():
        t = i
        i = 4
    block_body = ''
    if i == 5:
        block_body = '\n'.join(b.strip().split('\n')[1:-1])
    m = {
        'lang': kw['lang'],
        'title': t,
        'shortform': b_shortform,
        'blocksource': block_indent(b, 1),
        'blocksource_body': block_indent(block_body, 1),
        'blocksource4': block_indent(b, 5),
        'res': res,
        'res4': block_indent('\n' + res, 4),
    }
    f = getattr(AddSrcFormats, 'fmt_%s' % i, AddSrcFormats.fmt_1)
    res = f % m
    return res


class AddSrcFormats:

    fmt_1 = '''

LP Source:

```%(lang)s
%(blocksource)s
```

Result:

%(res)s
'''

    fmt_2 = '''

=== "LP Source"

    ```%(lang)s
     %(blocksource4)s
    ```

=== "Result" 

    %(res4)s
'''
    fmt_3 = '''

LP Source (shortform):

```
 `%(shortform)s`
```

Result:

%(res)s
'''

    fmt_4 = '''

=== "%(title)s"

    %(res4)s

=== "Source"

    ```%(lang)s
     %(blocksource4)s
    ```

    '''

    fmt_5 = '''

```%(lang)s
%(blocksource_body)s
```
    '''


# from lcdoc import session  # noqa
