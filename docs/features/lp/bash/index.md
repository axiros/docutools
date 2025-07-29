# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/bash/__init__.py,t=bash

This is the default evaluation mode, i.e. run when no `mode` parameter is given in the header.

It runs the given statements within a bash shell, [`subprocess.call`](https://docs.python.org/3/library/subprocess.html) style.

## Example

```bash lp:bash addsrc
ls -lta --color=always /usr/bin | head -n 20
```

## Parameters and Syntax

We have dedicated sections for those:

- [Parameters](../parameters.md).
- [Syntax](../syntax.md).


## Sessions

When you supply a `session` or `new_session` parameter, we will send the statements over into tmux
and run them there - i.e. you may control blocking subprocesses, including [REPLs](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop), i.e. a nodejs
session (...).

See [here](./sessions.md) for more about that.


