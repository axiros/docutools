# Supported Parameters

Except when otherwise noted, these parameters can be given
- per environment
- per page
- per block and
- per statement

They work in session or non session mode.

Syntax details [here](./syntax.md#parametrization).

```page lp addsrc

```

!!! caution "Parameter Support"

    Note that most but not all parameters do make sense for all plugins, e.g. `prompt`.

    - The ones listed are all supported for [`bash`](../bash/) shell mode.
    - The session specific params make sense only for plugins which do support sessions (`bash`,
      `python`)

### addsrc / addsrc=&lt;fmt|title&gt;
(`boolean` or source format or title)

???+ hint "Adds the lp source into the rendered page"

    All examples on this page use that header, set on page level.
    
    See :srcref:fn=src/lcdoc/lp.py,m=AddSrcFormats,t=AddSrcFormats regarding available formats.

    When you say `addsrc=<a string>` then we'll use format number 4 and set that string as the title.

    Example:

    ```bash lp addsrc=example fmt=mk_console
    ls /etc | head -n 3
    ```


### asserts
`asserts=<match string or condition>`
???+ hint "Raises an exception, if the expected string is not found in the result of an evaluation."

    Via this you can use LP as an (additional) functional test suite (and avoid broken docu).

    You may specify a single string or a [pycond][pycond] expression.

    - `bash lp asserts dwrx` or
    - `bash lp asserts=['root', 'dwrx']` or even
    - `bash lp asserts='[root and dwrx] and not fubar' (see [here][pycond] for valid expressions)

    Your docu build will exit with error on an assertion failure.


    !!! note "Example"

        ```bash lp asserts=etc
        ls /
        # statement specific assertion:
        echo hi # lp: asserts="hi and not [bar or etc]"
        ```

    As you can see, if given at block level all results of all evaluations of the block are matched.


### cwd
`cwd=<directory>`
???+ hint "change directory before running the command"

    !!! note "Example"

        ```bash lp cwd=/etc asserts=hosts
        ls  . | grep hosts
        ```


### eval
`eval=<never|always|on_change|on_page_change|<page match[:block match]>`

???+ hint "Determines which blocks to evaluate at `mkdocs build` or `mkdocs serve`"

     Please see the [specific chapter](./eval.md) about `eval`.



### expect
`expect=<match string or condition>` or `False`
???+ hint "Wait for this string to show up in the output"

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


### fetch
`fetch=<use_case_name>`
???+ hint "Async Result Fetching from Server"

    The evaluation output content is fetched after page load as soon as the user clicks on the output tab. This significantly improves pages load times, when there is a lot of output.


    !!! note "Example"

        ```bash lp session=test fetch=async_example
        ls -lt /usr/bin | head -n 12
        ```
    [Here](./async.md) is more about the mechanics.


### fmt
`fmt=<mk_console|mk_cmd_out|xt_flat>`
???+ hint "Determines Markdown Representation of Results"


    - `mk_cmd_out`: Displays two tabs, with command and output
    - `xt_flat`: Command and output in one go, xterm formatted ANSI escape codes
    - `mk_console`: An mkdocs console fenced code statement is produced, no ANSI escape formatting by xterm (the command is highlighted by mkdocs).

    !!! danger "xt_flat output must be visible at page load"

        Due to a technical restriction you currently cannot hide embedded or
        fetched xt_flat output within closed admonitions.
        You may use `???+ note "title"` style closeable admonitions though.


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


    !!! note "Custom Formats"

        Plugins can also [decide](./plugs/_tech.md) to deliver their own formatted markdown.

### hide_cmd
(`boolean`)

???+ hint "When set to `True` then command itself wont' be displayed."
    
    Currently this is only supported in [singleshot](#session) mode.

    !!! note "Example"

        ```bash lp cwd=/etc hide_cmd
        ls . | grep hosts
        ```


### kill_session
(`boolean`)

???+ hint "When set to `True` then the session will be killed after evaluation"
    
    By definition, this is only supported in [session](#session) mode.

    !!! note "Example"

        ```bash lp kill_session session=kill_test
        tmux list-sessions | grep kill_test
        ls . | grep hosts
        ```

        ```bash lp asserts="not kill_test"
        tmux list-sessions | grep test || true
        ```
### mode
`mode=<plugin name>` or `<lang> lp:<mode>`

???+ hint "Pass evaluation into various plugins"

    See [here](./plugs/_index.md) for more information.

### new_session
`new_session=<tmux session name>`
???+ hint "Runs the block within a **new** tmux session"
    
    If the session already exists, it will be destroyed before running.

    !!! note "Example"

        ```bash lp new_session=docutest
        date
        tmux list-sessions | grep docutest
        ```
    [Here](./sessions.md) is more about sessions.


### pdb
(`boolean`)

???+ hint "Enter debug mode before and after evaluation"

    !!! note "Example"

        ```
         :fences:bash lp pdb
         ls .
         :fences:
        ```

        The execution will be halted and you get the chance to inspect
        variables and step through the code.


### post
`post=<some command>`
???+ hint "Runs something after the (output recorded) commands"

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

### pre
`pre=<some command>`
???+ hint "Runs something, before the (output recorded) commands"

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


### prompt
`prompt=<prompt>`
???+ hint "Sets the prompt string"

    Default is '$ '.

    !!! note "Example"

        ```bash lp prompt="/foo/bar>" session=docutest
        echo -e '$ foo'
        ```
    In [sessions](./sessions.md) we do this by exporting `$PS1` to the given value, plus a space, at beginning of the session.


### session
`session=<tmux session name>`
???+ hint "Runs the block within a tmux session"
    
    If the session already exists, it will be re-used.

    !!! note "Example"

        ```bash lp session=docutest
        tmux list-sessions | grep docutest
        ```
    [Here](./sessions.md) is more about sessions.


### silent
(`boolean`)

???+ hint "Run the command(s) normally but do not create any markdown"

    !!! note "Examples"

        ```bash lp
        rm /tmp/silent_test || true
        ```

        ```bash lp silent
        touch /tmp/silent_test
        ```
        nothing is shown for block execution but the command was executed:

        ```bash lp
        ls -lta /tmp/silent_test
        rm /tmp/silent_test # lp: silent
        ```
        The last line shows `silent` on statement level.


### src
`src=<filename, relative to page or absolute>`
???+ hint "References a source file"
    
    This header parameter standardizes the use of external sources, e.g. for diagrams (plantuml,
    drawio, mermaid, ...). Their `mtime` (last modification time) goes into the [hash](./eval.md) of
    the whole LP block, thus triggering re-evaluation (e.g. a diagram to svg conversion) when the
    source changed. Note that the lp block stays constant, i.e. we would otherwise *not* re-eval the block
    when eval policy is the usual `on_change`.

    For plugin convenience this automatically also adds an `abs_src` parameter into the header
    arguments, with the page's absolute directory resolved.
    
 

### timeout
`timeout=<seconds>` (session only cmd)

???+ hint "Time until timeout error is raised, waiting for results in [sessions](./sessions.md)"

    !!! note "Example"

        This would fail with timeout error:

        ```
         ```bash lp timeout=0.1 session=test
         sleep 0.2
         ```
        ```





### with_paths
(`boolean`) (session only cmd)

???+ hint "Before a sequence of commands is run, we export `$PATH` and `$PYTHONPATH` of the calling process within tmux"

    A tmux session is started by issuing the tmux command - which starts the
    tmux server process, when there is non running. It might have a different
    process environment than the mkdocs process. With `with_paths` we export the two critical parameters before starting tmux.

[pycond]: https://pypi.org/project/pycond/
