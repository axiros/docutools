# LP Plugins Mechanics

Guide to creating custom plugins.


There is a very simple plugin machinery, based on the "`mode`" header parameter.

Default for mode is simply "bash", meaning all your evaluation is handled by the `bash.py` plugin.

See [here](../parameters.md) for available parameters of the default mode.

!!! important
    Plugins are lazy loaded, i.e. only on first use, within a docs build session.

## Creating your own plugins

Before we look into the directory above, we try import any plugin directly, the first time we need
it.

Therefore, by supplying a `$PYTHONPATH`, pointing to a plugin directory of your own, you can have your
own plugins supported (or overwrite the default ones).

!!! note "docs folder required"
    The docs are linked over to the docset at `lp/plugs` and inserted into nav via the
    [`find-pages`](../../../find-pages/) plugin.


## Interface

- The plugins need to supply a `run(cmd, kw)` method. In kw you get any available contextual
information, incl. the mkdocs config, via the LP class.

- You may also declare `run="cmd"`, which will put the full lp block body as a result - as is.

- You have to return a string (which would be the cached raw result) or a dict with `res` and
optionally
    - a `formatted` key.
    - a `nocache=<bool>` key
    - a `page_assets` key
    - `header`, `footer`, `md` (see below, page assets)

- The `formatted` value has to contain directly the markdown to be displayed, exclusive indentation.
  If simply `True` then the `res` value is taken.
- The `page_assets` value has to contain plain markdown (or javascript, html, css) added unindented once at
  the end of a page. 
- You may provide `formatted` and `nocache` also on module level
- Also you may declare a `page_assets` dict on module level, with understood keys:

    - `md`: markdown source added to markdown of page, will go into to-html rendering
    - `header`: html (e.g. scripts) added at start of container element, added after rendering
    - `footer`: html added at end of container element, added after rendering

    See the [chartist](../chartist/) plugin for an example.

    Note: https://github.com/squidfunk/mkdocs-material/issues/2338 only inside

- The full `res` will be the (cached) raw result, incl both optional keys.

### Adding Page Assets

Some LP plugins, e.g. mermaid or chartist require additional javascript or CSS to be included into the page.

They can declare or imperatively add such add ons for either

- header
- footer
- md

There are assets which are required once and others which you require per block.

!!! note "mkdocs material's nav.instant"

    Note that instant loading will, at page navigation events, (**only**) (re-)evaluate all script
    tags [**that are part of the container
    component**](https://github.com/squidfunk/mkdocs-material/issues/2338).

    Means: Manually adding assets *after* the content, e.g. via assets won't work. This is why LP assets mechnics add
    the scripts and css *within* the container component. 

    Here is how we do it:
    

Normal way to achieve this (example, declare on module level):

```python lp mode=show_src delim=page_assets_example dir=src/lcdoc/mkdocs/lp/plugs eval=always
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

Alternatively you may return `True` for `formatted`, then we treat `res` like it:

```python
def run(cmd, kw):
    ...
    return {
        'formatted': True,
        'res': <what will be within the block, indented>,
        'footer': <block specific js>}
    }
```

#### Multi Purpose Assets

Sometimes more than one plugin require sth like jquery. You can declare those by their own
namespace, using the `mode` key as in:

```python
page_assets = {
    'mode': 'jquery', # or ['jquery', ...]
    'footer': {
        'script': '//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight.min.js',
        'css': '//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight.min.css',
```

where the string 'jquery' is a known asset:

```python lp mode=show_src delim=known_page_assets dir=src/lcdoc/mkdocs/lp eval=always
```

If your multipurpose asset is now known, than declare the full dict under the `mode` key.


