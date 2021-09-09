# Tips

## Developing Long Running Multiple Command Sequences

Say we want to document how you set up a complete cloud system. Alone the
initial node creation takes minutes. It would take ages to always restart from scratch and fix
command by command.

Here sessions and testbeds are very practical:

- Kick off a tmux session with e.g. `new_session=AWS` in an initial lp block
- Evaluate: `lp_eval=mycloud_tutorial mkdocs build` -> tmux is running the session
- In a terminal attach: `tmux att -t AWS`. You can now fix broken command residues and always start
  over at any point of the sequence.
- In a helper page, say `test.md`, then try the next commands, e.g. droplet creation, then
  configuration, ... all one by one
- **Interactively** you can manually fix broken commands, look around, test. 
- Evaluate `test.md` until the next command is working
- Copy it over into `mycloud_tutorial.md`
- Rinse and repeat until all is working.

!!! tip "Alternative: Use block level skips"

    The header exclusive argument `<lang> lp skip_<this|other|below|above>` will skip block execution
    accordingly, i.e. you can also work from within the original page, from block to block. 




## Evaluating Single LP Blocks

When you want to test only certain blocks within a longer document, then add "`mymatch`" to the
header and evaluate like this:

```
lp_eval=mymatch mkdocs build
```


This restricts evaluation to matching blocks only (in the given lp documents).


!!! hint
    To cause more than one block evaluated simply add the "bogus" keyword argument in all the
    headers

For consecutive or single blocks please mind the `<lang> lp skip_<this|other|below|above>` header
argument.


## Forcing Re-Evaluation

!!! warning
    The following only applies if the block is not skipped or eval is set to never or another page.

The cache hash (which determines re-evaluation on change) is built just including [certain headers](./eval.md), in order to allow format changes, w/o *having* to
re-eval.
BUT: The full body, including whitespaces is *always* going into the hash.

I.e. to force a re-evaluation, simply add an empty line or a space in the body of an lp block.


## Multiline Commands / Here Docs in Sessions

!!! tip 
    Here Docs come handy when you have dynamic variable from a previous command, which you need to set into a file.

Like this, i.e. use the '> ' indicator at beginning of lines, which should be run as single
commands.


```bash
 ```bash lp session=DO asserts=foobarbazXsecond_line
 foo () { echo bar; }
 cat << EOF > test.pyc
 > foo$(foo)baz
 > second_line
 > EOF
 cat test.pyc | sed -z "s/\n/X/g" | grep 'foobarbazXsecond_line'
 ```
```

```bash lp session=DO asserts=foobarbazXsecond_line
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


## CI/CD

When building pages on CI/CD servers, keep in mind that builds which may succeed on your local machine may fail on clean
CI/CD environments due to timeouts, building e.g. caches. 

Consider the pros and cons of keeping those caches present
over repeated builds versus longer build times but higher reproducability.
- You can adjust the timeout of commands as shown above.
- You can have hybrid setups, partially created by CI/CD, partially locally, by committing result
  files and setting `lp_eval=on_page_change` in a [page lp](./syntax.md) block.



