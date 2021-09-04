# Supported Parameters

Except when otherwise noted, these parameters can be given
- per environment
- per page
- per block and
- per statement

They work in session or non session mode.

Syntax details [here](./syntax.md/#parametrization).

```page lp addsrc
```

### addsrc
(boolean)

??? hint "Adds the lp source into the rendered page"

    All examples on this page use that header, given as page parameter.



### asserts
`asserts=<match string or condition>`
??? hint "Raises an exception, if the expected string is not found in the result of an evaluation."

    Via this you can use LP as an (additional) functional test suite. 

    You may specify a single string or a [pycond][pycond] expression.

    !!! note "Example"

        ```bash lp asserts=etc
        ls /
        # statement specific assertion:
        echo hi # lp: asserts="hi and not [bar or etc]"
        ```

    As you can see, if given at block level all results of all evaluations of the block are matched.


### cwd
`cwd=<directory>`
??? hint "change directory before running the command"

    !!! note "Example"

        ```bash lp cwd=/etc asserts=hosts
        ls . | grep hosts
        ```


### pre
`pre=<some command>`
??? hint "Runs something, before the (output recorded) commands"

    !!! note "Examples"

        - Block level:
        ```bash lp=True, cwd='/tmp', asserts='barfoo', pre='touch barfoo|true'
        ls | grep bar
        ```
        - Statement level:
        ```bash lp cwd=/tmp asserts=foobar session=test
        {'pre': 'touch foobar|true', 'cmd': 'ls foo*', 'asserts': 'foobar'}
        ```

    Given at block level, the `pre` command is only run once, even if there are
    more than one individual statements within the body of the block.


### post
`post=<some command>`
??? hint "Runs something after the (output recorded) commands"

    !!! note "Examples"

        - Block level:
        ```bash lp=True, cwd='/tmp', asserts='barfoo', pre='touch barfoo|true', post='rm barfoo'
        ls | grep barfoo
        ```
        - Statement level:
        ```bash lp cwd=/tmp asserts=foobar session=test
        [{'pre': 'touch foobar|true', 'cmd': 'ls foo*', 'asserts': 'foobar', 'post': 'rm foobar'},
        'ls foobar # lp: asserts="cannot"']
        ```
    Given at block level, the `post` command is only run once, even if there are
    more than one individual statements within the body of the block.

### eval
`eval=<never|always|on_change|on_page_change|<page match[:block match]>`
???+ hint "Determines which blocks to evaluate at `mkdocs build` or `mkdocs serve`"

     Please see the [specific chapter](./eval.md) about `eval`.



### expect
`expect=<match string or condition>` or `False`
??? hint "Wait for this string to show up in the output"

    - Makes no much sense in [singleshot](#session) mode, where we simply run commands, until they complete.
      In singleshot mode use [`asserts`](#asserts) to fail if an expected result is not showing up.

    - Useful e.g. when, within sessions, a command blocks forever. As soon as
      the string occurs within the output, we stop listening and return as
      result what we have seen so far.

    - If set to `False` then all we stop collecting results when `timeout` is
      reached (no timeout error then).

    !!! warning

        If the session is not stopped or Ctrl-C is sent (see example), then the
        command will be running even after `mkdocs build`.

    !!! note "Example"

        We set to False, causing evaluation to stop after the timeout - otherwise this would run forever:

        ```bash lp timeout=0.1 session=test
        while true; do date; sleep 0.05; done # lp: expect=false
        send-keys: C-c # we will reuse that session, so we send ctrl-c
        ```


### fmt
`fmt=<mk_console|mk_cmd_out|xt_flat>`
??? hint "Determines Markdown Representation of Results"

    Default is `mk_cmd_out`

    !!! note "Examples"
        - mk_console
        ```bash lp fmt=mk_console
        echo Hello
        ```

        - xt_flat
        ```bash lp fmt=xt_flat
        echo Hello
        ```

        - mk_cmd_out
        ```bash lp fmt=mk_cmd_out
        echo Hello
        ```

### hide_cmd
(boolean)

??? hint "When set to `True` then command itself wont' be displayed."
    
    Currently this is only supported in [singleshot](#session) mode.

    !!! note "Example"

        ```bash lp cwd=/etc hide_cmd
        ls . | grep hosts
        ```


### kill_session
(boolean)

??? hint "When set to `True` then the session will be killed after evaluation"
    
    By definition, this is only supported in [session](#session) mode.

    !!! note "Example"

        ```bash lp kill_session session=kill_test
        tmux list-sessions | grep kill_test
        ls . | grep hosts
        ```

        ```bash lp asserts="not kill_test"
        tmux list-sessions | grep test || true
        ```




[pycond]: https://pypi.org/project/pycond/


| arg           |S |C|value        | Meaning
| -             |- | |-            | - 
| `assert`      |  |x| match string| Alias for asserts, deprected (does not work in python signatures) 
|


| arg           |S |C|value        | Meaning
| -             |- | |-            | - 
| `assert`      |  |x| match string| Alias for asserts, deprected (does not work in python signatures) 
| `asserts`     |  |x| match strings| Except if the expected string is not found in the result of an evaluation, which can be used as keyword in python style signatures, thus allowing to supply lists of assertions to be checked
| `cwd`         |  | |directory    | chdir before running
| `cmd_prepare` |  | |cmd string   | Run this before the (output recorded) commands
| `dt_cache`    |  | |seconds      | Only evaluate when run time is later than age of last result
| `expect`      |x |x|string/False | Wait for this string to show up in the output (e.g. when command blocks forever). The string is included. Also per command (dict). If set to `False` then all we stop collecting results when `timeout` is reached (no timeout error then). Makes no sense in non session mode, where we simply run cmd, until complete.
| `fmt`         |  | |             | mkdocs compliant output format. Supported: `mk_console`, `mk_cmd_out`, `xt_flat`
| `fn_doc`      |  | |filepath     | Filename of markdown document containing the block. Automatically set by  `doc pre_process`. Determines location of files created for async fetching.
| `hide_cmd`    |  | |bool         | When set to `True` then command wont' be displayed. 
| `kill_session`|x | |bool         | tmux session killed after last command output collected
| `lock_page`   |x | |bool         | Writes lock file, preventing re-evaluation of the page.
| `make_file`   |  | |filename     | Create a file with given name. See below for details. fn req, chmod supported.
| `mode`        |n | |(multiple)   | See mode section below
| `new_session` |x | |session name | Spawn a new tmux terminal to run the command. Kill any existing one with that name
| `nocache`     |  | |`True/False` | Never cache, always run
| `prompt`      |x | |`'$ '`       | `$PS1` (set at session init)
| `session`     |x | |session name | Run the command in this tmux session (create it when not present  - otherwise attach)
| `skip_above`  |x | |bool         | skip all blocks before this one when executing the page
| `skip_below`  |x | |bool         | skip all blocks after this one when executing the page
| `skip_other`  |x | |bool         | skip all other blocks when executing the page
| `skip_this`   |x | |bool         | skip this block when executing the page
| `silent`      |  |x|True         | Run the command(s) normally but do not create any markdown
| `timeout`     |x |x|float        | Time until timeout error is raised. 
| `with_paths`  |x | |true         | Before a sequence of commands is run, we export invoking process' `$PATH` and `$PYTHONPATH` within tmux


