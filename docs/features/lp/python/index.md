# python


This [exec](https://docs.python.org/3/library/functions.html)'s the block within the current python process.

All context available in the `ctx` dicts.

Output via 

- print: what is printed on stdout (embedded in fenced code, language python, [pformatted](https://docs.python.org/3/library/pprint.html))
- `show()`: Interpreted as markdown, with rendering support for
    - matplotlib

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied.


## Features

### Session Support

```python lp mode=python addsrc new_session=pyexample
# fmt not given - then we open and close fenced blocks, based on output mode (print vs show)
keys = [k for k in ctx.keys()]
print('variable `keys` assigned')
show('*variable is initted now*')
```

-------

We can refer to the variable later:

```python lp mode=python addsrc session=pyexample fmt=mk_console
# fmt given explicitely - then we show code and result all in one fenced block:
print(keys)
```


### Plugins

- The rendering of arguments of the `show` function is based on value and type of the argument.

- Plugins register match keys and rendering functions, which when key is matching, will render the
  argument of `show`

- You can provide your own python plugins, provided you supply an importable module
  `lp_python_plugins`, which at it's `__init__.py` imports all your plugins.


#### Plugin Interface

A plugin must provide a `register(fmts)` function, where fmts is a dict of match keys pointint to
rendering functions.

See the :srcref:fn=src/lcdoc/mkdocs/plugs/python/pyplugs/mpl_pyplot.py,t=matplotlib renderer.


### Matplotlib Rendering Support

This is a builtin plugin for lp python.

You need to have `pip/conda install matplotlib` and optionally also `pip/conda install numpy` within your environment.



!!! note "Works within Admonitions"

    ```python lp:python addsrc

    import matplotlib.pyplot as plt
    import numpy as np
    x = np.linspace(0, 2, 100)
    plt.plot(x, x, label='linear')
    plt.plot(x, x**2, label='quadratic')
    plt.plot(x, x**3, label='cubic')
    plt.xlabel('x label')
    plt.ylabel('y label')
    plt.title("Simple Plot")
    plt.legend()
    show(plt, fn='img/testplot.svg')
    show('??? hint "You can create *markdown* via the `show()` function"')
    show('    this was created from the python block')
    ```

- See [here](https://matplotlib.org/stable/gallery/index.html) for matplotlib example plots
- The plot is created as svg directly into your html site directory, i.e. will not show up within
  your docs tree.
- If for some reason you cannot create the svg on the system where you build your docs:

    1. supply a `fn` (filename) argument to the show function, relative to your page, e.g.
       `show(plt, fn='img/myplot')`. This will result in the plot created within your docs dir, so
       that you can commit it, from a system, where you *can* build the docs.
    1. commit the cache file
    1. optionally, set the [eval policy](../../eval.md) to `always` page wide, and to `on_change` for
       the block, if you want the *other* blocks on the page to be evaluated on the build system
       (e.g. for assertion checks).


!!! important "Implizit `plt.clf()` (clear plot) call"
    The `show` function applied to a pyplot will call `plt.clear()` after having created the svg.
    This is necessary since we exec the lp code in process (of the mkdocs build but also mkdocs
    serve). For serve this is a problem since subsequent runs after page edits
    will therefore remember the imported pyplot module, with all state.

    If you do NOT want to clear the plot but subsequently further extend it, then add `clf=False`:
    `show(plt, clf=False)`



