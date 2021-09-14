# python


This runs the block within a python session.

All context available in the `ctx` dicts.

Result will be what is printed on stdout.

Decide via the language argument (```&lt;language&gt; lp mode=python) what formatting should be applied.





## Example

```python lp mode=python eval=always addsrc
print([k for k in ctx.keys()])
```
