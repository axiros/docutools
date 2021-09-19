# python


This runs the block within a python session.

All context available in the `ctx` dicts.

Output via 

- print: what is printed on stdout (embedded in fenced code, language python, [pformatted](https://docs.python.org/3/library/pprint.html))
- return: what is returned (same mechanics)
- `show()`: Interpreted as markdown, with rendering support for
    - matplotlib

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied.


## Features

### Session Support

```python lp mode=python eval=always addsrc new_session=pyexample
keys = [k for k in ctx.keys()]
print('variable `keys` assigned')
```

refer to it later:

```python lp mode=python eval=always addsrc session=pyexample
print(keys)
```



### Matplotlib Rendering Support

!!! note "Works within Admonitions as well"

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
    show(plt)
    show('??? note "You can create *markdown* via the `show()` function"')
    show('    will be rendered normally')
    ```

- The plot is created as svg directly into your html site directory, i.e. will not show up within
  your docs tree.
- You need to have `pip/conda install matplotlib` and optionally also `pip/conda install numpy`
  within your environment.

!!! important "Implizit `plt.clf()` call"
    The `show` function applied to a pyplot will call `plt.clear()` after having created the svg.
    This is necessary since we exec the lp code in process (of the mkdocs build but also mkdocs
    serve). For serve this is a problem since subsequent runs after page edits
    will therefore remember the imported pyplot module, with all state.

    If you do NOT want to clear the plot but subsequently further extend it, then add `clf=False`:
    `show(plt, clf=False)`


## Alternatives

For rather code centric documentation have a look at these

- https://pypi.org/project/mkdocs-jupyter/
- there are other [notebook converters][1] as well

[1]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins#navigation--page-building



