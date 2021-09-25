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


### Rendering Plugins

- The rendering of arguments of the `show` function is based on value and type of the argument.

- Plugins register match keys and rendering functions, which when key is matching, will render the
  argument of `show`
- Alternatively if the "key" is a callable, it will be called with the object to be shown and can decide if
  returns True - then it's value, the actual rendering function will be called (see e.g. datatables python plugin).
- You can provide your own python plugins, provided you supply an importable module
  `lp_python_plugins`, which, at it's `__init__.py`, imports all your plugins.


!!! important
    
    LP python plugins are not lazily imported. Avoid side effects and expensive code at import time
    (which you should anyway, always).

#### Rendering Plugin Interface

A plugin must provide a `register(fmts)` function, where fmts is a dict of match keys pointing to
plugin specific rendering functions.

See the :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/mpl_pyplot.py,t=matplotlib renderer.


