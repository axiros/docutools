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
import json
import os
import string
import subprocess as sp
import sys
import time
from functools import partial as p
from importlib import import_module
from lcdoc.tools import app, write_file
import pycond

# important (colorize)
I = lambda s: s if not sys.stdout.isatty() else '\x1b[1;32m%s\x1b[0m' % s

env = os.environ
wait = time.sleep
now = time.time
exists = os.path.exists
user = env['USER']
env['PATH'] = 'bin:%s' % env.get('PATH', '')

# ---------------------------------------------------------------------------- Utilities
def check_assert(ass, res):
    msg = 'Assertion failed: Expected "%s" not found in result (\n%s)'
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
            raise Exception(msg % (ass, s))
        return

    if not isinstance(ass, (list, tuple)):
        ass = [ass]

    for a in ass:

        if not a in s:
            raise Exception(msg % (a, s))


# aliases = {}
to_list = lambda s: s if isinstance(s, list) else [s]


def repl_dollar_var_with_env_val(s, die_on_fail=True):
    if not '$' in s:
        return s
    for k in env:
        if k in s:
            s = s.replace('$' + k, env[k])
    if '$' in s:
        print('Not defined in environ: $%s' % s)
    return s


def spresc(cmd):
    """subprocess run - with escape sequences escaped (for tmux)"""
    return sprun(cmd.encode('unicode-escape'))


def sprun(*a, **kw):
    """Running a command as subprocess"""
    if not kw and len(a) == 1:
        print('', a[0])
    else:
        print('', a, kw)  # for the user (also in view messages)
    return p(sp.check_output, shell=True, stderr=sp.STDOUT)(*a, **kw)


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
            app.error('Command missing', res=o, cmd=orig_cmd)
            c['cmd'] = orig_cmd
        if not 'res' in c:
            app.error('Result missing', res=o, cmd=orig_cmd)
            c['res'] = 'Not available (%s)' % orig_cmd

        c['res'] = c['res'].replace('\n```', '\n ``')
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


def check_inline_lp(cmd, fn_lp):
    if not isinstance(cmd, str):
        return
    l = cmd.rsplit(' # lp: ', 1)
    if len(l) == 1 or '\n' in l[1]:
        return
    err, res = parse_header_args(l[1], fn_lp=fn_lp)
    if err:
        msg = 'Inline lp construct wrong: %s. Valid e.g.: "ls -lta /etc # lp: '
        msg += 'expect=hosts timeout=10". Got: %s %s'
        raise Exception(msg % (cmd, res[0], res[1]))
    res[1]['cmd'] = res[1].get('cmd', l[0])
    return res[1]


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
    print(s)


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
        return cmd
    r = []
    while lines:
        l = lines.pop(0)
        r.append(l)
        while lines and lines[0].startswith('> '):
            l = lines.pop(0)
            r[-1] += '\n' + l[2:]
    return [cmd for cmd in r if cmd.strip()]


def run_if_present_and_is_dict(kw, if_present):
    """utility for a frequent use case"""
    if not isinstance(kw, dict):
        return
    cmd = kw.get(if_present)
    if cmd:
        if os.system(cmd):
            raise Exception('%s run failed: %s. kw: %s' % (if_present, cmd, str(kw)))


def eval_lp(cmd, kw):
    # deprecated alias, not any more docued, did not work for py style args:
    assert_ = kw.get('asserts') or kw.get('assert')

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

    # mode = kw.get('xmode')
    # # in python we need tmux session (to start python first):
    # if not kw.get('session') and mode == 'python':
    #     kw['session'] = mode
    ns = kw.pop('new_session', None)
    if ns in (True, False):
        msg = 'Variable new_session must be string (the name of a session which is '
        msg += 'guaranteed a new one)'
        raise Exception(msg)
    if ns:
        from lcdoc import lp_session

        lp_session.tmux_kill_session(ns)
        kw['session'] = ns
    session_name = kw['session_name'] = kw.pop('session', None)
    # with sessions we do it IN tmux:
    if not session_name:
        run_if_present_and_is_dict(kw, 'pre')

    mode = kw.get('mode', 'bash')
    plug = get_or_import_plug(mode)

    g = lambda k, d=None: getattr(plug, k, d)
    if g('multi_line_to_list'):
        cmd = multi_line_to_list(cmd)

    r = g('run')

    kw['fmt'] = kw.get('fmt') or g('fmt_default') or dflt_fmt
    res = None
    if not r:
        app.error('Missing run method in plugin', mode=mode)
    else:
        res = r(cmd, kw)
        if isinstance(res, str):
            res = {'cmd': cmd, 'res': res}

    if not session_name:
        run_if_present_and_is_dict(kw, 'post')
    check_assert(assert_, res)
    # cwd header only for the current block:
    if cwd:
        os.chdir(here)
    return res


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
        res = eval_lp(cmd, kw)

    ret = {'raw': res}

    if not kw.get('silent'):
        res = prepare_and_fmt(res, orig_cmd=cmd, **kw)
        res = rpl(res, kw)
    else:
        res = ''

    i = int(kw.get('addsrc', 0))
    # if 'param' in fn_doc: breakpoint()  # FIXME BREAKPOINT
    if i:
        b = '\n' + kw.get('sourceblock', 'n.a.')
        m = {
            'blocksource1': b.replace('\n', '\n '),
            'blocksource4': b.replace('\n', '\n    '),
            'res': res,
            'res4': ('\n' + res).replace('\n', '\n    '),
        }
        f = getattr(BlockSrc, 'fmt_%s' % i, BlockSrc.fmt_1)
        res = f % m
    ret['formatted'] = res
    return ret


class BlockSrc:
    fmt_1 = '''

LP Source:

```bash
%(blocksource1)s
```

Result: 

%(res)s
'''

    fmt_2 = '''

=== "LP Source"

    ```bash
    %(blocksource4)s
    ```

=== "Result" 

    %(res4)s
'''


# from lcdoc import session  # noqa
