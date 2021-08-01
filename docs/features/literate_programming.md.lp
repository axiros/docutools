# Literate Programming

!!! note
    This is a feature of `docutools`, not a third party plugin. It is inspired by emacs' [org-babel](https://orgmode.org/worg/org-contrib/babel/).

The ["LP"](https://en.wikipedia.org/wiki/Literate_programming) feature of `docutools` allows to embed executable **code** within markdown sources and insert into the rendering result the **evaluated** output, before html build time. This is done through a preprocessor, offered by the `doc` script (`doc pre_process`).

It uses either python's `subprocess`, for single shot executables or tmux, when there needs to be a session.

## Security

Evaluation is triggered (only) by supplying the flag '--lit_prog_evaluation=md' to `doc pre_process`.

!!! danger "Documentation Building Runs Arbitrary Code"

    Documentation is source code.

    Consequence: Treat other people's documentation sources with the same care than you treat e.g.
    their test code: **Untrusted sources should be built only within proper sandboxes!**


## Features

### Direct Embedding

Adding this into your markdown...

```python
 ```bash lp
 ls -lta --color=always /etc | head -n 15; echo -e "With \x1b[1;38;5;124mAnsi Colors"
 ```
```
...generates this in the rendered result (both tabs):

```bash lp asserts=['root', 'rwx']
ls -lta --color=always /etc | head -n 15; echo -e "With \x1b[1;38;5;124mAnsi Colors"
```

### Assertions

You can avoid publishing broken docu by asserting on the evaluation results like that:

- `bash lp asserts dwrx` or
- `bash lp asserts=['root', 'dwrx']` or even
- `bash lp asserts='[root and dwrx] and not fubar' (see [here](https://github.com/axiros/pycond) for valid expressions)




Your docu build will exit with error on an assertion failure.


### Multiple Commands

Supply an array of strings (or dicts for more control, e.g. supplying a timeout):

```python
 ```bash lp new_session=test
 [{'cmd': 'n=foo', 'timeout':1}, 'echo $n']
 ```
```

generates:

```bash lp new_session='test', asserts='[foo and oo] and not fuubar'
[{'cmd': 'n=foo', 'timeout':1}, 'echo $n']
```

Simple Commands you may also only line separate:

```bash
 ```bash lp new_session=test
 echo foo
 echo bar
 ```
```

generates:

```bash lp new_session=test
echo foo
echo bar
```




### Named Stateful Sessions

- `session=<name>` reuses existing / starts new sessions if not existing
- `new_session=<name>` kills any running old session before starting a new one

```python
 ```bash lp new_session=test
 name=Joe;echo $name
 ```
```

```bash lp new_session=test
name=Joe;echo $name
```

i.e. state is available later:

```python
 ```bash lp session=test
 echo "Hi $name"
 ```
```

```bash lp session=test
echo "Hi $name"
```


### Async Fetching

The output content is fetched after page load as soon as the user clicks on the tab.

```python
 ```bash lp session=test fetch=test_usecase
 ls -lta /
 ```
```

```bash lp session=test fetch=test_usecase
ls -lta /
```




## Design

The feature is *not* realized via a markdown/mkdocs plugin but within the doc
`pre_process` step.

I.e. we favored an explicit two pages approach over an implicit mkdocs plugin, evaluating *and* rendering within one run.

### Rationale

1. Especially with sessions, it might get complex and requires interactive tuning, to get to a wanted result, so having
   an explicit command available is helpful
2. Results, especially those full of ansi escape codes distract from the original source. This way we keep the results
   out from the original primary docs source, rendering them into secondary page you never edit. Note: The async feature
   achieves this also, offloading the results into files downloaded only at page viewing time.
3. The two pages approach allows to choose WHEN to evaluate:
    - Either while writing docs, then committing the secondary page or
    - at CI/doc build, only committing the primary source and have CI running the evaluation (recommended for
      reproducability but not always practical)


### Primary and Secondary Pages

Primary markdown sources with lp statements must have a special extension `<name>.md.lp`. They are rendered into secondary ones: `<name>.md`, which are turned into html.

!!! hint "Secondary pages"

    Those, and and not the primary files you have to put into your `mkdocs.yml`.

    They may be "gitignored", except if you want to see the different results in
    your version history.
    Usually this is not the case, and ever varying output like timestamps will
    bloat your git object db.



### Evaluation Time

`doc pre_process` triggers the evaluation of all substring matching markdown source files. You can control which pages are evaluated via a flag (see `doc pp -hf`)

??? hint "Automatic Eval and Render on Change"

    If you have the live reloader running (`mkdocs serve --livereload`) you can have automatic evaluation done, using a file monitor like [`entr`](https://eradman.com/entrproject/).

    ```console
    $ # in one terminal
    $ mkdocs serve --livereload

    $ # in another - the touch is required since we write the primary first, causing mkdocs to start building:
    $ find -name *.lp | entr -s 'bash -c "doc pp -lpe $0"'

    ```

    This patches the live reloader of mkdocs to only reload on changes of `.md` files, i.e. no premature building
    will be triggered when you save an `.lp` file:

    `doc pp --patch_mkdocs_filewatch_ign_lp`


### Command Runtime Environment: `subprocess.check_output` or tmux

Without a `session` or `session_name` argument, commands are simply run `subprocess.check_output` style.

Alternatively, commands are run within tmux sessions with tmux' logging feature on, so the
output can be acquired, including ansi esacpe sequences and state is kept
between runs.


!!! success "Session Advantages"
    - LP stanzas are guaranteed to be run top down, i.e. in order.
    - Running in tmux therefore allows you to maintain state between various command
    runs.   
    - You can attach to the session and check what is going on.
    - You can issue commands which start subprocesses, e.g. poetry shell and continue the flow (set `expect=False`, see
      below)

Again: Running commands in persistent tmux sessions allows you to attach to it and
inspect what is going on, while `doc pre_process` renders the page and runs
the commands.

!!! danger "Set tmux base index to 1"
    This is the setting pretty much any tmux user seems to have but deviates from the default (0).
    Our functional tests for LP are all running a against a tmux with this setting and we do not guarantee LP to work with a base
    index of 0.

    To make this change persistent, put this command in your `~/.tmux.conf`:
    `set -g base-index 1`


Also any command has stdin and out available and renders output accordingly.

Example: You do not need to supply `--color=always`, when running e.g. `ls`, in order to get the ansi escape codes.

!!! tip "Automatic Re-attach"
    When you destroy the session over repeated runs then keep your terminal attaching to the sessions for inspection
    like this: `while true; do tmux att -t my_lp_session; sleep 0.1; done`



#### Session Execution Environment

In non session mode the executing process is a child of the process in which the literal_eval is started, i.e. has
`$PATH` and `$PYTHONPATH`. Not so in tmux. If you require those set then supply the `with_paths[=true]` header argument.


#### Debugging Sessions

Via a flag you can instruct `doc pre_process` to enter an interactive mode:

```bash lp fmt=xt_flat assert=step_mode
doc pp -hf lit_prog
```

!!! hint
    More flexibilty is given via breakpoints, directly within the `lp.py` module. API entry from `doc pre_process` plugin is `def run`.


### ANSI Escape Codes


Results are written into the secondary markdown source or, when bigger, into files which are pulled via Javascript asynchronously from the server at page view time only.


!!! success "Efficiency"
    In the mkdocs build we include [xtermjs](https://xtermjs.org/) which renders the escape codes correctly in HTML.  
    This is far more efficient than using [svg](https://yarnpkg.com/package/ansi-to-svg) or png formats.

## Formats

We support via the `fmt` parameter

- `mk_cmd_out`: Displays two tabs, with command and output
- `xt_flat`: Command and output in one go, xterm formatted ANSI escape codes
- `mk_console`: An mkdocs console fenced code statement is produced, no ANSI escape formatting by xterm (the command is highlighted by mkdocs).

!!! danger "xt_flat output must be visible at page load"
    Due to a technical restriction you currently cannot hide embedded or fetched xt_flat output within closed admonitions. You may use `???+ note "title"` style closeable admonitions though.


## Syntax

lp statements are to be enclosed in fenced code fragments, to still allow code
highlighting and docs builds, w/o cluttered sources.

To have `docs pre_process` find the code to evaluate append the term "lp" behind "python"

```python
 ```bash lp <header arguments>
 (your lp expression)
 ```
```

### Header Arguments

Those parametrize the lp run.

#### Syntax

They may either be delivered python signature compliant or "easy args" style:

```
 ```bash lp foo='bar', f=1.23, foo=True bar=True # python sig compliant
 ```bash lp foo=bar f=1.23 foo=true bar          # easy args. =true is default

```

When easy args parsing fails, then python signature mode is tried.

!!! caution "Easy Args Conventions and Restrictions"
    - No spaces in `key=value` allowed for easy args
    - `mykey` allowed, identical to `mykey=true`
    - Casting canonical: 1.123 considered float, 42 considered int, true considered bool, else string




### Reference Table

| arg           |S |C|value        | Meaning
| -             |- | |-            | - 
| `assert`      |  |x| match string| Except if the expected string is not found in the result of an evaluation
| `asserts`     |  |x| match strings| Alias for assert, which can be used as keyword in python style signatures, thus allowing to supply lists of assertions to be checked
| `cwd`         |  | |directory    | chdir before running
| `cmd_prepare` |  | |cmd string   | Run this before the (output recorded) commands
| `dt_cache`    |  | |seconds      | Only evaluate when run time is later than age of last result
| `expect`      |x |x|string/False | Wait for this string to show up in the output (e.g. when command blocks forever). The string is included. Also per command (dict). If set to `False` then all we stop collecting results when `timeout` is reached (no timeout error then)
| `fmt`         |  | |             | mkdocs compliant output format. Supported: `mk_console`, `mk_cmd_out`, `xt_flat`
| `fn_doc`      |  | |filepath     | Filename of markdown document containing the block. Automatically set by  `doc pre_process`. Determines location of files created for async fetching.
| `hide_cmd`    |  | |bool         | When set to `True` then command wont' be displayed. 
| `kill_session`|x | |bool         | tmux session killed after last command output collected
| `make_file`   |  | |filename     | Create a file with given name. See below for details. fn req, chmod supported.
| `mode`        |n | |(multiple)   | See mode section below
| `new_session` |x | |session name | Spawn a new tmux terminal to run the command. Kill any existing one with that name
| `nocache`     |  | |`True/False` | Never cache, always run
| `prompt`      |x | |`'$ '`       | `$PS1` (set at session init)
| `session`     |x | |session name | Run the command in this tmux session (create it when not present  - otherwise attach)
| `silent`      |  |x|True         | Run the command(s) normally but do not create any markdown
| `timeout`     |x |x|float        | Time until timeout error is raised. 
| `with_paths`  |x | |true         | Before a sequence of commands is run, we export invoking process' `$PATH` and `$PYTHONPATH` within tmux

!!! note "Columns"
    - "S": **Only** supported for tmux/session mode" (with n: NOT supported in session mode)
    - "C": Also supported per command when given as dict"

!!! note "`cwd` behaviour"
    - Silent change of dir before running command. Has no effect on an already running tmux session(!) - consider `new_session`
    - Back to previous dir after command. To *constantly* change the cwd use `cmd_prepare`

!!! note "`expect` behaviour"
    When no expect string is given we append a command to the given one, echoing out a conventional string
    which we match one. It will be removed from the returned (and rendered) command output. That won't work if the command
    is blocking, e.g. `redis-server` - supply an expect string then, after which we will consider the output complete.   
    If you supply `False`, then we wait for the timeout to occur then complete these command. 


!!! note "`timeout`"
    Can be set away from the default of 1 sec per command, per block but also globally via a flag (see `doc -hf timeout`)

!!! note "`asserts`"

    - single string: substring match in result
    - list of strings: substring match in result combined with `and`
    - valid [pycond](https://github.com/axiros/pycond) expression: Evaluated using string matching
      of pycond keys, via a custom lookup function



### Presets

| key          | value
| -            | -   
| `dir_repo`   | Set to directory of the repository 
| `dir_project`| Set to project root directory 

Example: 

```
    ```bash lp session=project    cwd=dir_repo # easy args style
    ```bash lp session='project', cwd=dir_repo # sig args style
```


### Available Environment Variables

If you want to work with/generate assets relative to your docu, these should be practical: 

```bash lp fmt=xt_flat assert=DT_DOCU_FILE and DT_PROJECT_ROOT and DT_DOCU and docutools
env | grep DT_
```
These are also put into new tmux sessions (at `new_session`):

<!-- grep colorizes the match, can only match on DT_ -->
```bash lp fmt=xt_flat new_session=dt_test assert=DT_ and DOCU_FILE and PROJECT_ROOT and DOCU and docutools
env | grep DT_
env | grep TMUX
```


You can reference any env var as a dollar var within your header args.

### Commands

#### Single Commands
- Can be single multiline strings, then run with Enter key hit in tmux or as a whole in subprocess.check_output
- Alternatively, can be dict. De-serialization via `literal_eval`, if failing `json`. Works only with tmux/sessions. 
    - cmd: the command to run
    - timeout: overwriting the default 1sec timeout
    - expect: An expect string per command


#### Multi Commands

Must be given as List, i.e. starting with `[`.

- Commands then run one by one 
- De-serialization via `literal_eval`, if failing `json`.


#### Special Commands

- `wait 1.2`: Causing the process to sleep that long w/o logging (tmux only). You can attach and check output.
- `send-keys: C-c`: Sends a tmux key combination (here Ctrl-C).


##### Example

This command waits for user input, blocking - we collect its output for 1 second then send `Ctrl-C`:

```json
    ```bash lp expect=false new_session=flags fmt=xt_flat
    ['export init_at="$HOME/foo"; export log_level=30',
     {'cmd': 'ops project --environ_flags', 'timeout': 1},
     'send-keys: C-c'
    ]
    ```
```

!!! hint "tests"

    See also the `test_lp.py` module for more features.


### Modes

The `mode` header argument determines how the command is run fundamentally.
Default is to run the command as suprocess as given.


#### Mode `python`

When supply the header argument `mode=python` then the command will be executed as python script and the result is whatever is printed on stdout.

!!! hint Debugging
    When the string "breakpoint()" is found within the "command", then stdout will not be redirected to catch the
    printed result.


#### Mode `show_file`

Generate output by `cat`-ting a file

Example:

```
 ```console lp fn=/etc/hosts mode=show_file
 ```
```

Resulting Markdown:

     ```console
     $ cat /etc/hosts
     127.0.0.1 localhost localhost.localdomain
     ```


#### Mode `make_file`

When supply the header arguments `mode=make_file fn=/tmp/foo` then the 'command' will be the content of that file.

- The file is physically created and won't be deleted, i.e. can be used in subsequent commands.

- Result is same as of `mode=show_file`

Example:

```
 ```python lp fn=/tmp/foo mode=make_file chmod=755
 class Foo:
    bar = 'baz'
 ```
```

Resulting Markdown:

     ```python
     $ cat /tmp/foo
     class Foo:
        bar = 'baz'
     ```


# Tips

## Developping LP Blocks

When you want to test only certain blocks within a longer document, then set:

```
--lit_prog_debug_matching_blocks=mymatch
```

to restrict evaluation to matching blocks only (in the given lp documents).

Example: `doc pp -lpe flags -lpdmb flagtest` will only run blocks matching "flagtest" for lp file flag.md.lp and
print the generated markdown, with all other blocks not evaluated, to stdout.

!!! hint
    To cause more than one block evaluated simply add a "bogus" keyword argument in the header which matches.




## CI/CD

When building pages on CI/CD servers, keep in mind that builds which may succeed on your local machine may fail on clean
CI/CD environments due to timeouts, building e.g. caches. Consider the pros and cons of keeping those caches present
over repeated builds versus longer build times but higher reproducability. You can adjust the timeout of commands as shown above.




## Editor Config

### Vim

If you use vim, here a few tips on config.

- detect `.lp` files as markdown
- syntax highlighting of fenced code blocks
- spelling and autocompletion

??? hint "`.vimrc` config items"

    ```vim

    function! s:file_type_handler()
      if &ft =~ 'mkd\|markdown'
        " no! java here (https://vi.stackexchange.com/a/18407/25379)
        for lang in ['yaml', 'vim', 'sh', 'bash=sh', 'python', 'c',
              \ 'clojure', 'clj=clojure', 'scala', 'sql', 'gnuplot', 'json=javascript']
          call s:syntax_include(split(lang, '=')[-1], '```'.split(lang, '=')[0], '```', 0)
        endfor

        setlocal spell
        " autocompletion from spellfile
        set complete+=kspell
        setlocal textwidth=120
        " nnoremap <silent> ,r :MarkdownPreview<CR>
      endif

      " unrelated but useful (,e -> breakpoint around line of code):
      if &ft =~ 'python'
        map ,e Otry:<Esc>j^i<TAB><Esc>oexcept Exception as ex:<CR>print('breakpoint set')<CR>breakpoint()<CR>keep_ctx=True<Esc>^
      endif

    endfunction


    augroup vimrc
      " literate programming files are markdown:
      au BufNewFile,BufRead *.lp       set filetype=markdown
      au FileType,ColorScheme * call <SID>file_type_handler()
    augroup END


    set spelllang=en
    set spellfile=$HOME/.config/nvim/spell/en.utf-8.add


    ```



