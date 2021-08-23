"""
# Tests for the literate programming (LP) feature.

We turn code tags with lp as argument after the language into evaluated result blocks incl Ansi Escape sequences, which are processed by xterm on the client, possibly remote fetched.

"""
import json
import os
import shutil
import sys
import time
import unittest

import pytest
from devapp.app import init_app_parse_flags

# from lcdoc.py_test.auto_docs import gen_mod_doc, wrap_funcs_for_call_flow_docs
from devapp.tools import define_flags, deindent, exists, project, read_file, write_file

import lcdoc.call_flow_logging as cfl
from lcdoc import lp
from lcdoc.auto_docs import mod_doc
from lcdoc.plugins.doc_lcdoc.pre_process import FLG, LP, Flags

define_flags(Flags)
init_app_parse_flags('pytest')
# just for reference, the unwrapped original:
# orig_gen_markdown = make_badges.gen_markdown
# first_test_was_run = []

D = deindent
now = time.time


def d_test():
    r = project.root() + '/tmp/lp_tests'
    return r


fn_test = lambda: d_test() + '/test.md.lp'
test_content = '\n'.join(['line0', ' \x1b[38;5;124mline1\x1b[0m', 'line2'])


def run_lp(md, raise_on_errs=None):
    dw, fn = d_test(), fn_test()
    breakpoint()  # FIXME BREAKPOINT
    # FUCK
    # shutil.rmtree(dw, ignore_errors=True)
    os.makedirs(dw, exist_ok=True)
    write_file(dw + '/test_content', test_content)
    return LP.run_md_page(md, fn, raise_on_errs=raise_on_errs)


def err_msg(l, res):
    # just to not have too much lines in breakpoint below
    msg = 'Expected line in produced markdown not in result!\nline: %s\nres: %s'
    msg = os.environ['PYTEST_CURRENT_TEST'] + '\n' + msg
    msg = msg % (l, res)
    print(msg)
    return msg


def check_lines_in(res, *blocks):
    """Are all non empty lines of the blocks in the result?
    More strict we don't go, for changes in newlines would kill all tests
    Plus "the dot, which we'll remove some day ..."
    """
    res = [l.rstrip() for l in res.splitlines()]
    for b in blocks:
        for l in b.splitlines():

            if l.strip():
                try:
                    # res is  a LIST - whole line must match
                    assert l.rstrip() in res
                except Exception as ex:
                    err_msg(l, res)
                    breakpoint()
                    sys.exit(1)


class extract(unittest.TestCase):
    'Detecting LP blocks in Markdown'

    def extract(md):
        r = LP.extract_lp_blocks(md=D(md), fn_lp=__file__)
        return r

    # the test md, where we play with the header of the first LP block:
    md = '''
        hi
        ```js lp %s
        foo = bar
        ```
        there

        no lp code:
        ```py k lp

        # also not since in other one:
        ```py lp
        outer non lp closes here:
        ```
        second lp one, indented, ok:

           ```foo lp 
            second lp code
           ```
        '''

    gen_md = lambda header: extract.md % header

    @classmethod
    def check_norm(cls, header):

        h = cls.gen_md(header)
        spec, dest = cls.extract(h)
        assert dest == [
            'hi',
            'LP_PH: 0.',
            'there',
            '',
            'no lp code:',
            '```py k lp',
            '',
            '# also not since in other one:',
            '```py lp',
            'outer non lp closes here:',
            '```',
            'second lp one, indented, ok:',
            '',
            'LP_PH: 1.',
        ]
        # all blocks
        assert isinstance(spec, list)
        # would indent the result like the original lp block:
        assert spec[1]['indent'] == '   '
        assert spec[1]['code'] == [' second lp code']
        assert spec[1]['lang'] == 'foo'
        assert spec[1]['nr'] == 1

        spec = spec[0]
        assert spec['code'] == ['foo = bar']
        assert spec['indent'] == ''
        assert spec['lang'] == 'js'
        assert spec['nr'] == 0
        return spec

    def test_find_block_without_attrs(self):
        spec = extract.check_norm('')
        assert spec['args'] == ()
        assert spec['kwargs'] == {}

    def test_find_block_with_easy_attrs(self):
        spec = extract.check_norm('foo=bar  i=42 b=true   f=1.2')
        assert spec['args'] == ()
        assert spec['kwargs'] == {'b': True, 'f': 1.2, 'foo': 'bar', 'i': 42}

    def test_find_block_with_py_sig_attrs(self):
        spec = extract.check_norm("'foo', 'bar', a='b', c='23', d={'foo': 'bar'}")
        assert spec['args'] == ('foo', 'bar')
        assert spec['kwargs'] == {'a': 'b', 'c': '23', 'd': {'foo': 'bar'}}

    def test_header_parse_error(self):
        spec = extract.check_norm("'foo 'bar', a='b', c='23', d={'foo': 'bar'}")
        assert spec['args'] == LP.header_parse_err
        assert 'SyntaxError' in repr(spec['kwargs'][LP.py_err])
        assert spec['kwargs'][LP.easy_args_err]


class embedded_no_sessions(unittest.TestCase):
    'Embedded Blocks, not remote fetched'

    def test_no_session_cmd_out(self):
        """First a test w/o sessions"""
        run = 'head %s/test_content |grep --color=never line' % d_test()
        md = '''
        ```bash lp
        %s
        ```
        '''
        cmd = '''
        === "Cmd"
            ```console
            $ %s
            ```
        '''
        out = '''
        === "Output"
            <xterm />
                line0
                 \x1b[38;5;124mline1\x1b[0m
                line2
        '''
        res = run_lp(md % run)
        check_lines_in(res, cmd % run, out)

    def test_asserts_work(self):
        run = 'head %s/test_content |grep --color=never line' % d_test()
        md = '''
        ```bash lp assert=line1
        %s # lp: expect=line
        ```
        '''
        cmd = '''
        === "Cmd"
            ```console
            $ %s
            ```
        '''
        out = '''
        === "Output"
            <xterm />
                line0
                 \x1b[38;5;124mline1\x1b[0m
                line2
        '''
        res = run_lp(md % run)
        check_lines_in(res, cmd % run, out)

    def test_asserts_fail(self):
        run = 'head %s/test_content |grep --color=never line' % d_test()
        md = '''
        ```bash lp assert=XXXX
        %s
        ```
        '''
        cmd = '''
        === "Cmd"
            ```console
            $ %s
            ```
        '''
        out = '''
        === "Output"
            <xterm />
                line0
                 \x1b[38;5;124mline1\x1b[0m
                line2
        '''
        with pytest.raises(Exception, match='XXX'):
            res = run_lp(md % run, raise_on_errs=True)

    def test_escape(self):
        """Single Escapes Working?"""
        md = '''
        ```bash lp 
        echo -e "With \x1b[1;38;5;124mAnsi\x1b[0m"
        ```
        '''
        cmd = '''
        === "Cmd"
            ```console
            $ echo -e "With \x1b[1;38;5;124mAnsi\x1b[0m"\n
            ```
        '''
        out = '''
        === "Output"
            <xterm />
                With \x1b[1;38;5;124mAnsi\x1b[0m\n
        '''
        res = run_lp(md)
        check_lines_in(res, cmd, out)


class embedded_sessions(unittest.TestCase):
    """Format mk_cmd_out (cmd and output tabs)

    This is the default format.
    """

    def test_with_paths(self):
        for k in 'PATH', 'PYTHONPATH':
            os.environ[k] = os.environ.get(k, '') + ':/bin/baz/foobar' + k
        md = '''
        ```bash lp new_session=test with_paths
        echo $PATH
        echo $PYTHONPATH
        ```
        '''
        res = run_lp(md)
        assert '/bin/baz/foobarPATH' in res
        assert '/bin/baz/foobarPYTHONPATH' in res

    def test_session_escape(self):
        """Single Escapes Working?
        Note: Tmux breaks appart the escape sequences, e.g. bold and color,
        so we only send one esc - a color:

        """
        md = '''
        ```bash lp new_session=test
        echo -e "With \x1b[38;5;124mAnsi"
        ```
        '''
        cmd = '''
        === "Cmd"
            ```console
            $ echo -e "With \x1b[38;5;124mAnsi"
            ```
        '''
        out = '''
        === "Output"
            <xterm />
                With \x1b[38;5;124mAnsi"
        '''
        res = run_lp(md)
        check_lines_in(res, cmd)

    def test_multiline(self):
        """ With the '> ' at the beginning, we send those blocks as one command
        the other lines are run one by one, for results per command.
        """
        md = '''
        ```bash lp new_session=test asserts=foobarbaz and line2

        ip () { echo bar; }
        cat << FOO > test.pyc
        > foo$(ip)baz
        > line2 
        > FOO
        cat test.pyc
        ```
        '''
        res = run_lp(md, raise_on_errs=True)
        with open('test.pyc') as fd:
            assert fd.read().strip() == 'foobarbaz\nline2'
        os.unlink('test.pyc')

    def test_multiline_struct(self):
        """ No '> ' required here"""
        md = '''
        ```bash lp new_session=test expect= asserts=foobarbaz and line2
        [{'cmd': 'ip () { echo bar; }'},
        {'cmd': """cat << FOO > test.pyc
        foo$(ip)baz
        line2 
        FOO"""},
        {'cmd': 'cat test.pyc'}]

        ```
        '''
        res = run_lp(md, raise_on_errs=True)
        with open('test.pyc') as fd:
            assert fd.read().strip() == 'foobarbaz\nline2'
        os.unlink('test.pyc')

    def test_cmd_out(self):
        md = '''
        ```bash lp new_session=test
        %s
        ```
        '''
        cmd = '''
        === "Cmd"
            ```console
            $ %s
            ```
        '''
        out = '''
        === "Output"
            <xterm />
                line0
                line2
        '''
        run = 'head %s/test_content |grep --color=never line' % d_test()
        res = run_lp(md % run)
        check_lines_in(res, cmd % run, out)
        # tmux changes the ansi codes slightly and the cmd is
        # repeated in the output, with prompt:
        assert '[38;5;124mline1' in res
        assert run in res.split('Output', 1)[1]

    def test_session_reuse(self):
        md1 = '''
        ```bash lp new_session=test1
        i=23
        ```
        '''
        res = run_lp(md1)
        md2 = '''
        ```bash lp session=test1
        echo $i
        ```
        '''
        res = run_lp(md2)
        o = res.split('Output', 1)[1]
        ind = o.split('<xterm', 1)[0].rsplit('\n', 1)[1]
        assert '\n' + ind + '    $ echo $i' in o
        assert '\n' + ind + '    23' in o

    def test_custom_expect_and_kill(self):
        """expect=... will include the expected string in the output.
        kill terminates the session after last command
        """
        md1 = '''
        ```bash lp new_session=test_foo kill_session=true
        ['echo bar', {'cmd': 'echo foo', 'expect': 'foo'}]
        ```
        '''
        res = run_lp(md1)
        out = '''

        === "Output"
            <xterm />
                $ echo bar
                bar
                $ echo foo
                foo
        '''
        check_lines_in(res, out)
        assert 'test_foo' not in os.popen('tmux ls').read()

    def test_empty_expect_and_ctrl_c(self):
        """This way you start e.g. a service in foreground, then kill it"""
        md1 = '''

        ```bash lp session=test1 fmt=mk_console expect=false
        [{'cmd': 'sleep 5', 'timeout': 0.5}, 'send-keys: C-c']
        ```

        '''
        t0 = now()
        res = run_lp(md1)
        assert now() - t0 > 0.5
        out = '''
        $ sleep 5
        '''
        check_lines_in(res, out)
        # cmd output was skipped since result had it anyway:
        assert len(res.split('$ sleep 5')) == 2

    def test_assert_pycond(self):
        md1 = '''

        ```bash lp session='test1', asserts='bar and foo'
        ['echo foo', {'cmd': 'echo bar'}]
        ```
        '''

        res = run_lp(md1)
        out = '''
        === "Output"
            <xterm />
                $ echo foo
                foo
                $ echo bar
                bar
        '''
        check_lines_in(res, out)
        md1 = '''

        ```bash lp session='test1', asserts='[bar and not foo] or echo'
        ['echo foo', {'cmd': 'echo bar'}]
        ```
        '''
        res = run_lp(md1)
        check_lines_in(res, out)
        md1 = '''

        ```bash lp session='test1', asserts='[bar and not foo]'
        ['echo foo', {'cmd': 'echo bar'}]
        ```
        '''

        with pytest.raises(Exception, match='foo'):
            res = run_lp(md1, raise_on_errs=True)

    def test_assert_inline(self):
        """Use the documentation tool as a little test framework"""
        md1 = '''

        ```bash lp session=test1 assert=foo
        ['echo foo', {'cmd': 'echo bar', 'assert': 'bar'}]
        ```
        '''

        res = run_lp(md1)
        out = '''
        === "Output"
            <xterm />
                $ echo foo
                foo
                $ echo bar
                bar
        '''
        check_lines_in(res, out)

        md1 = '''
        ```bash lp session=test1 assert=foo
        ['echo foo', {'cmd': 'echo bar', 'assert': 'XXX'}]
        ```
        '''
        res = run_lp(md1)
        assert (
            '!!! error "LP error: Assertion failed: Expected "XXX" not found in result'
            in res
        )

        md1 = '''
        ```bash lp session=test1 assert=foo
        ['echo foo', {'cmd': 'echo bar', 'asserts': ['XXX', 'bar']}]
        ```
        '''

        with pytest.raises(Exception, match='XXX'):
            res = run_lp(md1, raise_on_errs=True)

        md1 = '''
        ```bash lp session=test1 assert=foo
        ['echo foo', {'cmd': 'echo bar', 'asserts': ['b', 'bar']}]
        ```
        '''
        res = run_lp(md1, raise_on_errs=False)


class embedded_multiline(unittest.TestCase):
    def test_simple_multiline_cmd(self):
        """w/o and w/ tmux"""
        for k in '', ' session=test':
            md = '''
                ```bash lp %s
                echo foo
                echo bar
                ```
                '''
            md = md % k
            cmd = '''
                === "Cmd"

                    ```console
                    $ echo foo
                    $ echo bar
                    ```
                '''
            out = '''
                === "Output"
                    <xterm />
                        $ echo foo
                        foo
                        $ echo bar
                        bar
                '''
            res = run_lp(md)
            check_lines_in(res, cmd, out)

    def test_simple_ansi_multiline_cmd(self):
        """w/o and w/ tmux"""
        for k in ('',):
            md = '''
                ```bash lp %s
                echo -e '\x1b[32mfoo'
                echo bar
                ```
                '''
            md = md % k
            cmd = '''
                === "Cmd"

                    ```console
                    $ echo -e '\x1b[32mfoo'\n
                    $ echo bar
                    ```
                '''
            out = '''
                === "Output"
                    <xterm />
                        $ echo -e '\x1b[32mfoo'
                        \x1b[32mfoo
                        $ echo bar
                        bar
                '''
            res = run_lp(md)
            check_lines_in(res, cmd, out)

    def test_simple_multiline_cmd_flat(self):
        for k in '', ' session=test':
            md = '''
                ```bash lp fmt=xt_flat %s
                echo foo
                echo bar
                ```
                '''
            md = md % k
            cmd = '''
                <xterm />
                    $ echo foo
                    foo
                    $ echo bar
                    bar
                '''
            res = run_lp(md)
            check_lines_in(res, cmd)


class multi(unittest.TestCase):
    def test_multicmd_with_one_silent(self):
        md = '''
            ```bash lp new_session=test
            ['n=foo', {"cmd": "echo fubar", "silent": True}, 'echo $n']
            ```
            '''
        cmd = '''

            === "Cmd"
                ```console
                $ n=foo
                $ echo $n
                ```
            '''
        out = '''
            === "Output"
                <xterm />
                    $ n=foo
                    $ echo $n
                    foo
            '''

        res = run_lp(md)
        assert not 'fubar' in res
        check_lines_in(res, cmd, out)


def strip_id(s):
    r, l = [], s.splitlines()
    while l:
        line = l.pop(0)
        if not '<!-- id: ' in line:
            r.append(line)
    return '\n'.join(line)


class mode(unittest.TestCase):
    def test_mode_python(self):
        md = '''
            ```python lp mode=python
            assert ctx.get('hide_cmd') == None
            print('foo')
            ```
            '''
        out = '''
            ```python
            print('foo')
            foo
            '''
        res = run_lp(md)
        check_lines_in(res, out)

    def test_mode_python_cmd_hidden_and_ctx_availability(self):
        md = '''
            ```python lp mode=python hide_cmd=True
            assert ctx['hide_cmd']
            assert ctx['fmt'] == 'mk_console'
            print('foo')
            ```
            '''
        out = '''
            ```python
            foo
            '''
        res = run_lp(md)
        check_lines_in(res, out)
        assert not 'print' in res

    def test_mode_python_header_arg_silent(self):
        md = '''
            ```python lp mode=python silent=True
            assert ctx.get('hide_cmd') == None
            print('foo')
            ```
            '''
        res = run_lp(md)
        assert len(res.split('<!-- id: ')) == 3
        assert not strip_id(res).strip()

    def test_mode_make_file(self):
        fn = '/tmp/test_lp_file_%s' % os.environ['USER']
        md = '''
            ```python lp fn=%s mode=make_file
            foo = bar
            ```
            '''
        md = md % fn
        res = run_lp(md)
        out = '''
            ```python
            $ cat %s
            foo = bar
            ```
            '''
        check_lines_in(res, out % fn)

    def test_mode_show_file(self):
        fn = '/tmp/test_lp_file_%s' % os.environ['USER']
        with open(fn, 'w') as fd:
            fd.write('foo = bar')
        md = '''
            ```console lp fn=%s mode=show_file
            ```
            '''
        md = md % fn
        res = run_lp(md)
        out = '''
            ```console
            $ cat %s
            foo = bar
            ```
            '''
        check_lines_in(res, out % fn)


class header_args(unittest.TestCase):
    def test_presets(self):
        md = '''
            ```bash lp foo=dir_repo bar=dir_project
            stuff
            ```
            '''
        d = project.root()
        fn = d + '/docs/foo.md.lp'
        b = LP.extract_lp_blocks(md, fn_lp=fn)
        assert b[0][0]['kwargs'] == {'bar': d, 'foo': d}


class state(unittest.TestCase):
    def test_assign(self):
        md = '''
            ```bash lp
            name=joe; echo $name
            ```
            '''
        res = run_lp(md)
        assert ' joe' in res.split('Output', 1)[1]

    def test_assign_with_session_state(self):
        """Tmux keeps the state. No NEW session in the second call"""
        md = '''
            ```bash lp new_session=test
            name=joe; echo $name
            ```
            '''
        res = run_lp(md)
        assert ' joe' in res.split('Output', 1)[1]

        md = '''
            ```bash lp session=test
            echo "hi $name"
            ```
            '''
        res = run_lp(md)
        assert ' hi joe' in res.split('Output', 1)[1]


# class lang:
#     def xxtest_lang():
#         md = '''
#         ```js lp session=test timeout=10000
#         echo '{\"json\": true}'
#         ```
#         '''
#         res = run_lp(md)
#         breakpoint()  # FIXME BREAKPOINT
#         assert ' joe' in res.split('Output', 1)[1]


class fetched_mk_cmd_out(unittest.TestCase):
    """Format mk_cmd_out (cmd and output tabs)
        'Blocks now fetched from the server'

        This is the default format.
        """

    def test_with_and_without_session_cmd_fetched_out(self):
        run = 'head %s/test_content |grep --color=never line' % d_test()
        for k in '', 'new_session=test':
            md = '''
                ```bash lp fetch=usecase _k_
                %s
                ```
                '''
            md = md.replace('_k_', k)
            cmd = '''
                === "Cmd"
                    ```console
                    $ %s
                    ```
                '''
            out = '''
                === "Output"
                    <xterm />
                         remote_content
                    ![](./images/test.md_usecase.ansi)
                '''
            res = run_lp(md % run)
            check_lines_in(res, cmd % run, out)
            # done by the js when live:
            s = read_file(d_test() + '/images/test.md_usecase.ansi')
            if k:
                # tmux we have prompt and it changes the ansi slightly:
                s = s.split(run, 1)[1]
                assert '124mline1' in s
            else:
                # prompt is in s but rest is ident:
                s.endswith(test_content)


extr_head = lambda h: LP.extract_header_args(h, 'x')[1]


class headers_easy(unittest.TestCase):
    def test_headers_easy_1(self):
        res = extr_head('```bash lp foo=bar')
        assert res == {'foo': 'bar'}

    def test_headers_easy_2(self):
        res = extr_head('```bash lp foo=bar bar')
        assert res == {'foo': 'bar', 'bar': True}

    def test_headers_easy_3(self):
        res = extr_head('```bash lp foo=bar, bar')
        assert LP.easy_args_err in str(res)


class headers_py(unittest.TestCase):
    def test_headers_py_1(self):
        res = extr_head('```bash lp foo="bar", bar')
        assert LP.easy_args_err in str(res)
        assert 'positional argument follows keyword argument' in str(res)

    def test_headers_py_2(self):
        res = extr_head('```bash lp bar, foo="bar"')
        assert LP.easy_args_err in str(res)
        assert "name 'bar' is not defined"


class features(unittest.TestCase):
    def test_wait(self):

        md1 = '''
        ```bash lp new_session=test1
        ['echo foo', 'wait 0.1', 'echo bar' ]
        ```
        '''
        t = now()
        res = run_lp(md1)
        assert now() - t > 0.1
        out = '''
        === "Output"
            <xterm />
                $ echo foo
                foo
                $ echo bar
                bar
        '''
        check_lines_in(res, out)
