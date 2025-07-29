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

- `mode`: The `mode` parameter determines the block processing mode. Default is shell mode ("bash") may also be supplied via a keyword parameter:  
  `lang lp:foo` equal to `lang lp mode=foo`.

- `lang`: The word before "lp" is for Markdown not for LP. It is declaring the
  code block *formatting* language, and is *not* relevant for LP itself.


## Short Form

There is a **short form**, for blocks without a body:

```
 `lp:<mode> [parameters]`
```

In the short form the mode *must* be added to `lp:`. See below for more about the short form.

## Detection

- We parse the markdown source line by line.
- We have a state variable `fenced`, initially `False`.


### Normal Form

#### Block Start

1. `fenced` is `False`
1. A line must start with `n` spaces ( `n` ≥ 0 )
1. Followed by 3 backticks. `fenced` is set to `True`.
1. Followed by a word (any letter except space), the formatting language
1. Followed by "`lp`" then a space OR "`lp:`" then a word, the `mode` parameter

All following lines are the block body - until:

#### Block End

1. `fenced` is True
1. A line starts with `m` spaces ( `m` = `n` )
1. Followed by 3 backticks
1. Followed by any number of spaces. `fenced` is set to `False`

#### Example

!!! note "An Admonition With An Inner LP Block"

    ```bash lp addsrc
    echo "hello world"
    ```

#### Summary

In general this means that LP blocks look like normal fenced code blocks except:

- The first (header) line has more parameters than just the formatting language
- They are also detected within HTML, if the criteria are met:

HTML Example:

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

*See [here](./python/_tech.md) regarding the show function.*

### Short Form

1. `fenced` is False
1. A line must start with `n` spaces ( `n` ≥ 0 )
1. Followed by 1 backtick
1. Followed by `lp:`
1. Followed by `k` characters except space, with `k` ≥ 1 )
1. The line ends with a backtick, followed by any number of spaces.


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

Normal Form:

```
 :fences:my_lang lp:page foo=bar # or: :fences:my_lang lp mode=page foo=bar
 :fences:
```

Short Form:

```
`lp:page foo=bar`
```

i.e. by specifying the keyword "`page`" as `mode`

!!! caution "Position matters"

    The parameters in `mode=page` headers are only valid for all lp blocks **below** the declaration.

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


You can reference any env var as a "dollar var" within your header args.


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


If you do have a (short) body, you may supply it via the [body](./parameters.md#body) parameter:

```
 `lp:python body=print(42)`
```




`lp:column`
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
        ls /usr/bin |grep env
        ```

#### On Timeouts
In [session][s] mode, we expect commands to complete within a given time, otherwise we raise.


#### On Assertions

We can also force normally exitting commands to fail, when certain strings are not occuring in the
result, see the [`asserts`](./parameters.md#asserts) parameter. That way you can turn lp into a stateful ([sessions][s]) or stateless functional testsuite.


[s]: ./parameters.md#session

