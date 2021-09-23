# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/make_file/__init__.py,t=make_file

Creates a file and displays it as if we used cat on it.

## Parameters
- fn
- replace: optional replacements to apply (dict)
- content (the body of the lp block)
- chmod: optional chmod params


## Example

```json lp mode=make_file fn=/tmp/myfile.json addsrc fmt=mk_console
{"foo": "bar"}
```

The file has been created:

```bash lp fmt=mk_console
ls -lta /tmp/myfile.json
```


