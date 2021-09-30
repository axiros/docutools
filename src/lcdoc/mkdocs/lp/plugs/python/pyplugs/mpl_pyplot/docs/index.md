# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/mpl_pyplot/__init__.py,t=Matplotlib Rendering Support

Matplotlib Support. See [here](https://matplotlib.org/stable/gallery/index.html) for the vast amount of matplotlib's plotting features.

## Requirements

You need to have `pip/conda install matplotlib` and optionally also `pip/conda install numpy` within your environment.


## Examples

!!! note "Works within Admonitions"

    ```python lp:python addsrc eval=always
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

- The plot is created as svg directly into your html site directory, i.e. will not show up within
  your docs tree.
- If for some reason you can *not* create the svg on the system where you build your docs:

    1. supply a `fn` (filename) argument to the show function, relative to your page, e.g.
       `show(plt, fn='img/myplot')`. This will result in the plot created within your docs dir, so
       that you can commit it, from a system, where you *can* build the docs.
    1. commit the cache file
    1. optionally, set the [eval policy](../../eval.md) to `always` page wide, and to `on_change` for
       the block, if you want the *other* blocks on the page to be evaluated on the build system
       (e.g. for assertion checks).


!!! important "Implicit `plt.clf()` (clear plot) call"
    The `show` function applied to a pyplot will call `plt.clear()` after having created the svg.
    This is necessary since we exec the lp code in process (of the mkdocs build but also mkdocs
    serve). For serve this is a problem since subsequent runs after page edits
    will therefore remember the imported pyplot module, with all state.

    If you do NOT want to clear the plot but subsequently further extend it, then add `clf=False`:
    `show(plt, clf=False)`




