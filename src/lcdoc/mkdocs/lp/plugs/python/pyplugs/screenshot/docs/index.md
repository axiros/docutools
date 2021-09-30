# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/screenshot/__init__.py,t=Screenshots

Creates screenshots for URLs, using [chrome-remote-interface](https://github.com/cyrus-and/chrome-remote-interface)

Source from [here](https://dschnurr.medium.com/using-headless-chrome-as-an-automated-screenshot-tool-4b07dffba79a).

## Requirements

- chrome based browser, with path exported as `$browser` or `"$BROWSER"` 
- `node` executable. We check `$nodejs` path variable with preference
- `npm install -g chrome-remote-interface minimist` (small libs to address the remote interface)

## Example


```python lp:python addsrc
show("screenshot",  url="https://github.com", width=600, height=400)
```


## Parameters

Besides `url`:

```python lp:show_src delim=url_shot_defaults dir=src/lcdoc/mkdocs/lp eval=always
```


!!! tip "Can run on CI/CD"
    
    The headless mode of the browser makes it possible to have the screenshooter be running on CI/CD
    as well, i.e. without a graphical environment. Then you may git ignore the `img/http*` images or
    set the `force` flag.


