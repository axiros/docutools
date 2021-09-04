# Literate Programming


The ["LP"](https://en.wikipedia.org/wiki/Literate_programming) feature of `docutools` allows to
embed executable **code** within markdown sources and insert into the rendering result the
**evaluated** output, before html build time. This is done through a plugin, with an `on_markdown`
hook, i.e. before html is generated.


!!! note
    This is a feature of `docutools`, not a third party plugin. It is inspired by emacs' [org-babel](https://orgmode.org/worg/org-contrib/babel/).

## Features

- Concise **[Syntax](./syntax.md)**: Does not distract when reading source

- [**Stateless**](./stateless.md): Single Shot Evaluations

- [**Stateful**](./sessions.md): The code to evaluate is sent into parametrizable [tmux](https://en.wikipedia.org/wiki/Tmux) windows and
  executed there. Means you can inspect and even change what's going on, during page evaluation.
  Anything set within the tmux session (e.g. environ, variables) is available in later calls.

- **Assertions**: You can assert on the evaluation result, means you can turn the code blocks into a
  functional test suite, documented through your markdown around the blocks.

- **Caching**: Results are cached and only re-evaluated when source changes. You can edit the
  markdown around, w/o triggering possibly expensive evaluation runs. 
  By deciding to commit the cache files you can opt to prevent CI from executing code which is only
  runnable on certain machines (e.g. where you have your cloud infra keys)

- **Debugging**: Execution can be halted and context inspected

- **Async Results Fetching**: Big evaluation results may be fetched only on demand, e.g. on click on
  otherwise non expanded "Output" tabs.



## Security

Documentation is source code.

!!! danger "Documentation Building Runs Arbitrary Code"

    Consequence: Treat other people's documentation sources with the same care than you treat e.g.
    their test code: **Untrusted sources should be built only within proper sandboxes!**


