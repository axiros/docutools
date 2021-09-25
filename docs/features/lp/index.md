# Literate Programming :srcref:fn=src/lcdoc/mkdocs/lp/__init__.py,t=

The ["LP"](https://en.wikipedia.org/wiki/Literate_programming) feature of `docutools` allows to

- embed executable parametrizable **code** within markdown sources and
- insert into the rendering result the **evaluated** output, before html build time, including
  possibly

    - javascript helper libraries
    - javascript code
    - styles.

This is done through a plugin, with an `on_markdown` hook, i.e. before html is generated.


## Motivation

> The main benefit of the LP plugin is to keep documentation in sync with the system you are documenting.  
> And [vice versa](./parameters.md#asserts).

!!! note

    The plugin is heavily inspired by emacs' [org-babel](https://orgmode.org/worg/org-contrib/babel/).



## Feature Highlights

- Concise **[Syntax](./syntax.md)**: Does not distract when reading source

- **Stateless** and [**Stateful**](./sessions.md) Evaluation, using
  [tmux][tmux]  

  Means you can inspect and even change what's going on, before, after and during page evaluation.

  Anything set within the tmux session (e.g. environ, variables) is available in later mkdocs build
  runs, except when you decide to [kill](./parameters#kill_session) the session.

- [**Assertions**](./parameters.md#asserts): You can assert on the evaluation result, i.e. you can
  turn the code blocks into a functional test suite, documented through your markdown around the
  blocks.

- [**Various Output Formats**](./parameters.md#fmt)

- [**Various Builtin Evaluation Plugins**](./plugs/_index.md). Extendable with your own.

- [**Caching**](./eval.md): Results are cached and only re-evaluated when source changes. You can edit the
  markdown around, w/o triggering possibly expensive evaluation runs. 
  By deciding to commit the cache files you can opt to prevent CI from executing code which is only
  runnable on certain machines (e.g. where you have your cloud infra keys)

- [**Debugging**](./parameters.md#pdb): Execution can be halted and context inspected

- [**Full Terminal Color Support**](./xterm.md): Colorized terminal output via `xterm.js`  

- [**Async Results Fetching**](./async.md): Big evaluation results may be fetched only on demand, e.g. on click on
  otherwise non expanded "Output" tabs

- [**Coverage Backrefs**](./plugs/cov_report/): Dynamic coverage contexts, optionally with
  [backrefs](../../about/coverage.md) to the markdown source line of the LP block, triggering the evaluation


[Here](./parameters.md) the list of parameters for the default mode: Evaluation in a (bash) shell.

Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-lp,t=m within your `mkdocs.yml` file,
section plugins.

## Requirements

- [tmux][tmux] (sessions for the default evaluation mode: bash)
- [ripgrep][rg] (code searching)
- [fd][fd] (file finding)

## Security

Documentation is source code.

!!! danger "Documentation Building Runs Arbitrary Code"

    Consequence: Treat other people's documentation sources with the same care than you treat e.g.
    their test code: **Untrusted sources should be built only within proper sandboxes!**

## Alternatives

For rather code centric documentation have a look at these

- [Pheasant](https://pheasant.daizutabi.net/)
    - Auto generation of outputs for a fenced code block or inline code in Markdown source using Jupyter client. The code language is not restricted to Python.
    - Auto numbering of headers, figures, tables, and etc. Numbered objects can be linked from other Markdown sources.
- https://pypi.org/project/mkdocs-jupyter/
- There are other [notebook converters][1] as well

[1]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins#navigation--page-building


[tmux]: https://en.wikipedia.org/wiki/Tmux
[rg]: https://github.com/BurntSushi/ripgrep
[fd]: https://github.com/sharkdp/fd
