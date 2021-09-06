# Plugins

There is a very simple plugin machinery, based on the "`mode`" header parameter.

Default for mode is simply "bash", meaning all your evaluation is handled by the `bash.py` plugin.

See [here](./parameters.md) for available parameters.

Here the currently available builtin plugins:

```bash lp cwd=dir_repo fmt=mk_console
ls src/lcdoc/mkdocs/lp/plugs | grep '.py$' | sort
```

They are lazy loaded, i.e. on first use, within a docs build session.

## Supplying your own plugins

Before we look into the directory above, we try import any plugin directly, the first time we need
it.

Therefore, by supplying a $PYTHONPATH pointing to a plugin directory of your own, you can have your
own modes supported (or overwrite the default ones).


## Interface

- The plugins need to supply a `run(cmd, kw)` method. In kw you get any available contextual
information, incl. the mkdocs config, via the LP class.

- You have to return a string (which would be the cached raw result) or a dict with `res` and
optionally a `formatted` key.

- res will be the (cached) raw result.

- The formatted value has to contain directly the markdown to be displayed, exclusive indentation.

## Built In Plugins

:plugs_docs:


## Examples

### make_file

```json lp mode=make_file fn=/tmp/myfile.json addsrc fmt=mk_console
{"foo": "bar"}
```

The file has been created:

```bash lp fmt=mk_console
ls -lta /tmp/myfile.json
```


### python

```python lp mode=python eval=always addsrc
print([k for k in ctx.keys()])
```

### show_file

```json lp mode=show_file fn=/tmp/myfile.json addsrc
{"foo": "bar"}
```




<!-- :docs:this_example -->
### show_src

We included this sentence and the header between match strings....

<!-- :docs:this_example -->

```python lp mode=show_src delim=this_example hide="This Example" addsrc dir=docs/features/lp eval=always
```

