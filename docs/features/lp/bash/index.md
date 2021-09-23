# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/bash/__init__.py,t=bash

This is the default evaluation mode, i.e. run when no `mode` parameter is given in the header.

It runs the given statements within a bash shell, [`subprocess.call`](https://docs.python.org/3/library/subprocess.html) style.

Alternatively, When you supply a `[new_]session` parameter, we will [send the statements over into tmux](./sessions.md) and run
them there.


Available parameters: See [here](../parameters.md).

