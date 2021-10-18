# Python Plugin Mechanics

This [exec](https://docs.python.org/3/library/functions.html)'s the block within the current python process.

- Namespace is `globals()`
- All LP context available in the `ctx` dicts

Output via 

- `print`: what is printed on stdout (embedded in fenced code, language python, [pformatted](https://docs.python.org/3/library/pprint.html) if not a plain string)
- **`show()`**: Interpreted as markdown, with rendering support supplied by python
  [plugins](./_index.md).

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied for fenced output.


## Features

### Session Support

```python lp mode=python addsrc new_session=pyexample
# fmt not given - then we open and close fenced blocks, based on output mode (print vs show)
keys = [k for k in ctx.keys()]
print('variable `keys` assigned')
show('*The variable is now in session "pyexample"*.')
```

-------

We can refer to the variable later:

```python lp mode=python addsrc session=pyexample fmt=mk_console
# fmt given explicitely - then we show code and result all in one fenced block:
print(keys)
```


## Plugins

- Plugins are addressed via the `show` function
- The rendering of arguments of the `show` function is based on value and type of the argument.

### The `show` function

- Plugins register match keys and rendering functions, which when key is matching, will render the argument of `show`
- Alternatively if the "key" is a callable, it will be called with the object to be shown and can decide if
  returns True - then it's value, the actual rendering function will be called (see e.g. datatables python plugin).
- You can provide your own python plugins, provided you supply an importable module
  `lp_python_plugins`, which, at it's `__init__.py`, imports all your plugins.


!!! important
    
    LP python plugins are *not* lazily imported. Avoid side effects and expensive code at import time
    (which you should anyway, always).

### Rendering Plugin Interface

A plugin must provide a `register(fmts)` function, where fmts is a dict of match keys pointing to
plugin specific rendering functions.

See e.g. the :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/mpl_pyplot.py,t=matplotlib renderer.


### Syntax

#### Normal form:

```python
# in an lp:python block
show(<plugin match>, **plugin kws)
```

#### Short form, w/o kws:

```
`lp:python show=<plugin match>`
```

#### Ultrashort form, with kws:

```
`lp:python:<match> plugin_kw1=val1 plugin_kw2=val2`
```

Example

```
`lp:python:convert pdf=img/sample.pdf width=200 addsrc`
```




## Tips

### Adding Post Page Hooks

Some python plugins want to do sth after the html was rendered.

Say we require in a `show` handler being called back after the html was created, in order to insert
js or embed svgs (...):

```python
from lcdoc.mkdocs.tools import add_post_page_func
add_post_page_func(python.Session.kw, embed_svgs, once=True)
```

The LP plugin registers an [`on_post_page`](https://www.mkdocs.org/dev-guide/plugins/) hook, where it checks all such registered  functions and
calls them in insertion order, with parameters `output`, `page`, `config`. 

!!! tip
    Register a [partial](https://docs.python.org/3/library/functools.html#functools.partial) if you need more infos from during the `show` function call time.
    The hook may return modified html as a string.

See the callflow python plugin for details.


