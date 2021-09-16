# Literate Programming (LP) Plugins

There is a very simple plugin machinery, based on the "`mode`" header parameter.

Default for mode is simply "bash", meaning all your evaluation is handled by the `bash.py` plugin.

See [here](../parameters.md) for available parameters of the default mode.

Here the currently available builtin plugins:

```bash lp cwd=dir_repo fmt=mk_console
ls src/lcdoc/mkdocs/lp/plugs | grep -v pycache | sort
```

They are lazy loaded, i.e. on first use, within a docs build session.

## Supplying your own plugins

Before we look into the directory above, we try import any plugin directly, the first time we need
it.

Therefore, by supplying a `$PYTHONPATH`, pointing to a plugin directory of your own, you can have your
own modes supported (or overwrite the default ones).

!!! note "README.md required"
    Those are linked over to the docset.


## Interface

- The plugins need to supply a `run(cmd, kw)` method. In kw you get any available contextual
information, incl. the mkdocs config, via the LP class.

- You may also declare `run="cmd"`, which will put the full lp block body as a result - as is.

- You have to return a string (which would be the cached raw result) or a dict with `res` and
optionally
    - a `formatted` key.
    - a `add_to_page` key.

- The `formatted` value has to contain directly the markdown to be displayed, exclusive indentation.
- The `add_to_page` value has to contain plain markdown (or javascript, html, css) added unindented once at
  the end of a page. 
- Alternatively you may declare an `add_to_page` dict on module level, with understood keys:

    - header (html added before the first `<link>` tag
    - footer (html added before `</body>`
    - md (markdown source added at footer of page)

    See the [mermaid](./mermaid.md) plugin for an example.

- The full `res` will be the (cached) raw result, incl both optional keys.

### Post Page Modifications

Some LP plugins, e.g. mermaid or chartist require additional javascript or CSS to be included into the page.

They can declare or imperatively add such add ons for either

- header
- footer
- md

Even if there are more than one occurrances of 


## Example

```python lp mode=show_src delim=add_to_page_example dir=src/lcdoc/mkdocs/lp/plugs eval=always
```


## Built In Plugins

:lp_plugins_descr:

