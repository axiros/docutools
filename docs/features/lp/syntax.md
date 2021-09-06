# Literate Programming (lp) Syntax

lp blocks are special fenced code blocks within a markdown page and look like so:

```bash lp addsrc fmt=mk_console
echo "Hello ${User:-World}"
```

or more general:

```
 :fences:<lang> lp [block level parameters]           <---- lp block header
 statement 1 [per statement parameters]          
 (...)                                           <---- lp block body
 [statement n]                                  
 :fences:
```

We detect lp blocks by the "`lp`" keyword as second parameter, after "language".

!!! tip "Indentation supported"
    You may indent LP blocks, like any fenced code block, with the superfences plugin active, e.g.:

    !!! note "My Admonition With An Inner LP Block"
        ```bash lp addsrc
        echo "hello world"
        ```



## Parametrization

Evaluation is parametrized by keys and values, which may be given via the environment, per page, per
block and per statement, with priority in this order.

[Here](./parameters.md) is the list of supported parameters.

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
    The parameter is only valid for all lp blocks **below** the declaration. You may set to a different
    value,  mid-page.
    

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
 :fences:bash lp foo='bar', f=1.23, foo=True bar=True, asserts="foo and bar"


```

When easy args parsing fails, then python signature mode is tried.

!!! caution "Easy Args Conventions and Restrictions"
    - No spaces in `key=value` allowed for easy args, except when value between double or single
      quotes (`"` or `'`).
    - `mykey` allowed, identical to `mykey=true`
    - Casting canonical: 1.123 considered float, 42 considered int, true considered bool, else string






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

