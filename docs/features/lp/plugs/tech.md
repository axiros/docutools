# LP Plugins Mechanics

Guide to creating custom plugins.


There is a very simple plugin machinery, based on the "`mode`" header parameter.

Default for mode is simply "bash", meaning all your evaluation is handled by the `bash.py` plugin.

See [here](../parameters.md) for available parameters of the default mode.

Here the currently available builtin plugins:

```bash lp cwd=dir_repo fmt=mk_console
ls src/lcdoc/mkdocs/lp/plugs | grep -v pycache | sort
```

They are lazy loaded, i.e. on first use, within a docs build session.

## Creating your own plugins

Before we look into the directory above, we try import any plugin directly, the first time we need
it.

Therefore, by supplying a `$PYTHONPATH`, pointing to a plugin directory of your own, you can have your
own plugins supported (or overwrite the default ones).

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
    - `header`, `footer`, `md` (see below, page assets)

- The `formatted` value has to contain directly the markdown to be displayed, exclusive indentation.
  If simply `True` then the `res` value is taken.
- The `add_to_page` value has to contain plain markdown (or javascript, html, css) added unindented once at
  the end of a page. 
- Alternatively you may declare an `add_to_page` dict on module level, with understood keys:

    - header (html added before the first `<link>` tag
    - footer (html added before `</body>`
    - md (markdown source added at footer of page)

    See the [mermaid](./mermaid.md) plugin for an example.

- The full `res` will be the (cached) raw result, incl both optional keys.

### Adding Page Assets

Some LP plugins, e.g. mermaid or chartist require additional javascript or CSS to be included into the page.

They can declare or imperatively add such add ons for either

- header
- footer
- md

There are assets which are required once and others which you require per block.

Normal way to achieve this (example, declare on module level):

```python lp mode=show_src delim=add_to_page_example dir=src/lcdoc/mkdocs/lp/plugs eval=always
```

This will register the assets by key `plugin name (=mode)`.

If the run method's response includes any of `header`, `footer`, `md`, that asset will be registered by id of
the block, i.e. rendered into the final html, guaranteed:


```python
def run(cmd, kw):
    ...
    return {
        'res': <just a raw result, not rendered, since formatted is given. could be empty>,
        'formatted': <what will be within the block, indented>,
        'footer': <block specific js>}
    }
```



