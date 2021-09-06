# Literate Programming


The ["LP"](https://en.wikipedia.org/wiki/Literate_programming) feature of `docutools` allows to
embed executable **code** within markdown sources and insert into the rendering result the
**evaluated** output, before html build time. This is done through a plugin, with an `on_markdown`
hook, i.e. before html is generated.


!!! note
    This is a feature of `docutools`, not a third party plugin. It is inspired by emacs' [org-babel](https://orgmode.org/worg/org-contrib/babel/).

## Features

[Here](./parameters.md) is the full list of features.

Highlights:

- Concise **[Syntax](./syntax.md)**: Does not distract when reading source

- **Stateless** and [**Stateful**](./sessions.md) Evaluation, using
  [tmux][tmux]  
  Means you can inspect and even change what's going
  on, before after and during page evaluation. Anything set within the tmux session (e.g. environ,
  variables) is available in later mkdocs build runs, except when you decide to
  [kill](./parameters#kill_session) the session.

- [**Assertions**](./parameters.md#asserts): You can assert on the evaluation result, means you can
  turn the code blocks into a functional test suite, documented through your markdown around the
  blocks.

- [**Various Output Formats**](./parameters.md#fmt)

- [**Caching**](./eval.md): Results are cached and only re-evaluated when source changes. You can edit the
  markdown around, w/o triggering possibly expensive evaluation runs. 
  By deciding to commit the cache files you can opt to prevent CI from executing code which is only
  runnable on certain machines (e.g. where you have your cloud infra keys)

- [**Debugging**](./parameters.md#pdb): Execution can be halted and context inspected

- **Full Terminal Color Support**:   
  Fenced code blocks can 'only' highlight per language - but cannot "understand" terminal output and
  their [color escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code).  
  Therefore in the mkdocs build we include [xtermjs](https://xtermjs.org/), which renders the escape codes correctly within HTML.  
  This is far more efficient than using [svg](https://yarnpkg.com/package/ansi-to-svg) or png formats.

- [**Async Results Fetching**](./async.md): Big evaluation results may be fetched only on demand, e.g. on click on
  otherwise non expanded "Output" tabs.


```bash lp cwd=dir_project

pwd


```

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
