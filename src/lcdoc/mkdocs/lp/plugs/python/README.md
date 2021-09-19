# python


This runs the block within a python session.

All context available in the `ctx` dicts.

Result will be what is printed on stdout.

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied.


## Examples

```python lp mode=python eval=always addsrc
print([k for k in ctx.keys()])
```




```python lp:python eval=always addsrc

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
show('!!! note "You can create *markdown* as well"')
show('    will be rendered normally')
```



## Alternatives

For rather code centric documentation have a look at these

- https://pypi.org/project/mkdocs-jupyter/ (there are other [notebook converters][1] as well)

[1]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins#navigation--page-building
