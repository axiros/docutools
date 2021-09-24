# Literate Programming (lp) Syntax

## Normal Form

lp blocks are special fenced code blocks within a markdown page and look like so:

```bash lp addsrc fmt=mk_console
echo "Hello ${User:-World}"
```

or more general:

```
 :fences:<lang> lp[:mode] [block level (=header) parameters]  <---- lp block header
 statement 1 [per statement parameters]          
 (...)                                                   <---- lp block body
 [statement n]                                  
 :fences:
```

- The `mode` parameter (default is "bash") may also be supplied via a keyword parameter, i.e. these are 
ident: `lang lp:foo` and `lang lp mode=foo`.

- `lang` is not[^1] logically relevant for LP itself, but necessary for the editor and, dependent on the result also
  for the renderer into html.

[^1]: Only exception: [page level](#page-level) blocks.

## Short Form

There is a **short form**, for blocks without a body as well:

```
 `lp:<mode> [parameters]`
```

In the short form the mode *must* be added to `lp:`. See below for more about the short form.

## Detection

We detect the normal form of lp blocks by the "`lp`" keyword as second parameter, after "language" of lines starting
with "S:fences:", where S is any number of spaces.

Therefore syntax wise they are found like any other fenced code block (holds true also with the superfences
plugin active).

So this works:

!!! note "An Admonition With An Inner LP Block"

    ```bash lp addsrc
    echo "hello world"
    ```

Only difference to normal fenced blocks: LP blocks are also found and processed within html:

```html
 <div style="color:gray">
 ```_ lp:python
 import time; now = time.ctime(); show(f"Hello from python, at <b>{now}</b>!")
 ```
 </div>
```
Result:

<div style="color:gray">
```_ lp:python
import time; now = time.ctime(); show(f"Hello from python, at <b>{now}</b>!")
```
</div>



## Parametrization

Evaluation is parametrized by keys and values, which may be given via the environment, per page, per
block and per statement, with priority in this order.

[Here](./parameters.md) is the list of supported parameters, for the default mode:
[`bash`](../bash/).

### Environment

A parameter `foo` may be set to value `bar` for *all* lp blocks within your docs set like so:

```bash
LP_foo=bar mkdocs build
export LP_foo=bar; mkdocs build 

# and for convenience also the lower case form:
lp_foo=bar mkdocs build 
```

### Page Level 

You may specify a parameter for *all* blocks within a *specific* markdown page like so:

```
 :fences:page lp foo=bar
 :fences:
```

i.e. by specifying the conventional keyword "`page`" where normally  "`<language>`" is, i.e. first
param after the opening fences.

!!! caution "Position matters"
    The parameter is only valid for all lp blocks **below** the declaration.

    - You may set to a different value,  mid-page. 
    - You may use more than one `page` block.
    

### Block Level

This sets the value for just *one* block:

```
 :fences:bash lp foo=bar 
 echo Hello
 :fences:
```



### Statement Level

This set the value for just one statement:

```
 :fences:bash lp
 echo Hello # lp: foo=bar
 echo World # while executing this, foo is NOT set (except when defined elsewhere)
 :fences:
```


### Parameter Syntax

Parameters may either be delivered python signature compliant or "easy args" style:

```bash

 # easy args (=true is default):
 :fences:bash lp foo=bar f=1.23 foo=true bar asserts="foo and bar"

 # python signature compliant form:
 :fences:bash lp foo='bar', f=1.23, foo=True, bar=True, asserts="foo and bar"


```

When easy args parsing fails, then python signature mode is tried.

!!! caution "Easy Args Conventions and Restrictions"
    - No spaces in `key=value` allowed for easy args, except when value between double or single
      quotes (`"` or `'`).
    - `mykey` allowed, identical to `mykey=true`
    - Casting canonical: 1.123 considered float, 42 considered int, true considered bool, else string


### Presets

These keywords will be dynamically replaced within headers:

| key          | value
| -            | -   
| `dir_repo`   | Set to directory of the repository 
| `dir_project`| Set to project root directory 

Examples:

```
    :fences:bash lp session=project    cwd=dir_repo # easy args style
    :fences:bash lp session='project', cwd=dir_repo # sig args style
```




### Available Environment Variables

If you want to work with/generate assets relative to your docu, these should be practical: 

```bash lp fmt=xt_flat assert=LP_DOCU_FILE and LP_PROJECT_ROOT and LP_DOCU_DIR and docutools
env | grep LP_ # any env var starting with lp_ or LP_ is put into the session
```
These are also put into new tmux sessions (at `new_session`):

<!-- grep colorizes the match, can only match on LP_ -->

```bash lp fmt=xt_flat new_session=dt_test assert=LP_ and DOCU_FILE and PROJECT_ROOT and DOCU and docutools
env | grep LP_
env | grep TMUX
```


You can reference any env var as a dollar var within your header args.


## Short Form for LP Plugins Without Body

Some plugins do not need a body to evaluate.
Then you can also express lp blocks via the short form:

```
 `lp:<mode(plugin name)> [header params like normal]`
```

Example:

```
 `lp:lightbox match=img`
```

!!! caution "Must be within separate lines"

    The short form can *not* work as inline statement (i.e. between other words in a line). You
    (still) need to have exclusively one statement per line.

## Evaluation

### Statements

Within an lp block can be more than one statement contained. We run the statements consecutively.

Staments can be given per line or a in a structured way:


```
 :fences:bash lp
 echo hello # lp: asserts=hello
 echo world
 :fences:
```

is equivalent to

```python
 :fences:bash lp
 [{'cmd': 'echo hello', 'asserts': 'hello'},
  {'cmd': 'echo world'}]
 :fences:
```

!!! hint
    In structured mode you can omit the list notation, if there is just one command and simply supply
    a dict with cmd and [parameters](./parameters.md).

#### Multiline Commands / Here Docs

Here Docs come handy when you have dynamic variable from a previous command, which you need to set into a file.

Like this, i.e. use the '> ' indicator at beginning of lines, which should be run as single
commands.


```bash lp addsrc session=DO asserts=foobarbazXsecond_line
foo () { echo bar; }
cat << EOF > test.pyc
> foo$(foo)baz
> second_line
> EOF
cat test.pyc | sed -z "s/\n/X/g" | grep 'foobarbazXsecond_line'
```

!!! warning "Picky Syntax"
    - The second space is requred after the '>'
    - No lines with content may start with a space




### Special Statements

- `wait 1.2`: Causing the process to sleep that long w/o logging (tmux only). You can attach and check output.
- `send-keys: C-c`: Sends a tmux key combination (here Ctrl-C).




### Exceptions

#### On Execution Exit Codes
Whenever a statement fails, we stop evaluation and except. 

!!! hint
    If you want to continue even when a statement fails, than add the usual `|| true` after the
    statement.

    !!! note "Example"
        
        ```bash lp
        ls /notexisting || true # would except here without the `|| true`
        ls /etc |grep hosts
        ```

#### On Timeouts
In [session][s] mode, we expect commands to complete within a given time, otherwise we raise.


#### On Assertions

We can also force normally exitting commands to fail, when certain strings are not occuring in the
result, see the [`asserts`](./parameters.md#asserts) parameter. That way you can turn lp into a stateful ([sessions][s]) or stateless functional testsuite.


[s]: ./parameters.md#session

