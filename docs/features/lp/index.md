# Literate Programming :srcref:fn=src/lcdoc/mkdocs/lp/__init__.py,t=

The ["LP"](https://en.wikipedia.org/wiki/Literate_programming) feature of `docutools` allows to
embed executable **code** within markdown sources and insert into the rendering result the
**evaluated** output, before html build time. This is done through a plugin, with an `on_markdown`
hook, i.e. before html is generated.



## Motivation

This plugin is heavily inspired by emacs' [org-babel](https://orgmode.org/worg/org-contrib/babel/).

The main benefit of LP is to keep documentation in sync with the system you are documenting.

And [vice versa](./parameters.md#asserts).


## Features

[Here](./parameters.md) the list of parameters for the default mode: Evaluation in a shell.

Highlights:

- Concise **[Syntax](./syntax.md)**: Does not distract when reading source

- **Stateless** and [**Stateful**](./sessions.md) Evaluation, using
  [tmux][tmux]  

  Means you can inspect and change what's going on, before, after and during page evaluation.
  Anything set within the tmux session (e.g. environ, variables) is available in later mkdocs build
  runs, except when you decide to [kill](./parameters#kill_session) the session.

- [**Assertions**](./parameters.md#asserts): You can assert on the evaluation result, means you can
  turn the code blocks into a functional test suite, documented through your markdown around the
  blocks.

- [**Various Output Formats**](./parameters.md#fmt)

- [**Various Builtin Evaluation Plugins**](./plugins.md). Extendable with your own.

- [**Caching**](./eval.md): Results are cached and only re-evaluated when source changes. You can edit the
  markdown around, w/o triggering possibly expensive evaluation runs. 
  By deciding to commit the cache files you can opt to prevent CI from executing code which is only
  runnable on certain machines (e.g. where you have your cloud infra keys)

- [**Debugging**](./parameters.md#pdb): Execution can be halted and context inspected

- [**Full Terminal Color Support**](./xterm.md): Colorized terminal output via `xterm.js`  

- [**Async Results Fetching**](./async.md): Big evaluation results may be fetched only on demand, e.g. on click on
  otherwise non expanded "Output" tabs

- [**Coverage Backrefs**](./plugins/cov_report.md): Dynamic coverage contexts, optionally with
  [backrefs](../../about/coverage.md) to the markdown source line of the LP block, triggering the evaluation


Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-lp,t=m

## Requirements

- [tmux][tmux]
- [ripgrep][rg]
- [fd][fd]



## Security

Documentation is source code.

!!! danger "Documentation Building Runs Arbitrary Code"

    Consequence: Treat other people's documentation sources with the same care than you treat e.g.
    their test code: **Untrusted sources should be built only within proper sandboxes!**



[tmux]: https://en.wikipedia.org/wiki/Tmux
[rg]: https://github.com/BurntSushi/ripgrep
[fd]: https://github.com/sharkdp/fd
