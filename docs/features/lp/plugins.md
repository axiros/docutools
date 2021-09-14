# Literate Programming (LP) Plugins

There is a very simple plugin machinery, based on the "`mode`" header parameter.

Default for mode is simply "bash", meaning all your evaluation is handled by the `bash.py` plugin.

See [here](./parameters.md) for available parameters.

Here the currently available builtin plugins:

```bash lp cwd=dir_repo fmt=mk_console
ls src/lcdoc/mkdocs/lp/plugs | grep '.py$' | sort
```

They are lazy loaded, i.e. on first use, within a docs build session.

## Supplying your own plugins

Before we look into the directory above, we try import any plugin directly, the first time we need
it.

Therefore, by supplying a `$PYTHONPATH`, pointing to a plugin directory of your own, you can have your
own modes supported (or overwrite the default ones).


## Interface

- The plugins need to supply a `run(cmd, kw)` method. In kw you get any available contextual
information, incl. the mkdocs config, via the LP class.

- You have to return a string (which would be the cached raw result) or a dict with `res` and
optionally
    - a `formatted` key.
    - a `add_to_page` key.

- The `formatted` value has to contain directly the markdown to be displayed, exclusive indentation.
- The `add_to_page` value has to contain plain markdown (or javascript, html, css) added unindented once at
  the end of a page. See the [mermaid](./plugins/mermaid.md) plugin for an example.

- The full `res` will be the (cached) raw result, incl both optional keys.



## Built In Plugins

- [`bash`](./plugins/bash.md): Runs the given statements within a bash shell
- [`cov_report`](./plugins/cov_report.md): Inserts a coverage report
- [`make_badges`](./plugins/make_badges.md): Creates badges
- [`make_file`](./plugins/make_file.md): Creates a file and displays it as if we used cat on it
- [`mermaid`](./plugins/mermaid.md): Creates mermaid charts
- [`python`](./plugins/python.md): Runs the block within a python session
- [`show_file`](./plugins/show_file.md): Cats a file
- [`show_src`](./plugins/show_src.md): Copies delimitted stanzas within arbitrary files (usually source code) into your docs and creates links to the repo server





