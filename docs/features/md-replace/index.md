## Markdown Replace

Allows to add replacements into the markdown source, which are replaced by

- values or
- function call results,

given by a hot reloaded configurable python module.

Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-md-replace,t=m

You set up replacements in a python file (default is: `docs/mdreplace.py`), which must have a table
attribute, either dict or callable.

When callable it will be called with the mkdocs config and must return a replacement dict.


### Features

- The values of the replacement dict can themselves be callable, and if so, are called at replacement
  time with contextual information: 

  ```python
    replace(
                mdblock=md,
                plugin=self,
                plugin_file=__file__,
                config=config,
                page=page,
                markdown=markdown,
            )
  ```

- If the callable does not require kw args (e.g. `time.ctime`) we will not pass them
- The callable can return a replacement for the whole line, by returning a dict like `{'line':
  ....}`, i.e. with a "line" key.
- The callable can also return content added to top and bottom of the markdown (e.g. for style
  defs), in the returned dict. Keys are `markdown_header`, `markdown_footer`. See e.g.
  :srcref:fn=src/lcdoc/mkdocs/replace/admons.py,t=admons.py
- If the replace values are lists (also as returned by the callable), they will be properly indented
  as multiline text.

#### Controlling Replacements Within Fenced Blocks

    - fenced blocks are omitted EXCEPT:
    - if the replacement key is specified like this `key:all:` - then even `:key:` in fenced blocks
      is replaced

### Config

- `seperator`: ':' by default.  
    Example: `':curtime:'`, for `{"cur_time": time.ctime}` based replacements.
- `replacement_file`: when not starting with '/' we'll prefix with docs_dir. Default: "mdreplace.py"




### Built in Replacments

Some keys are :srcref:fn=src/lcdoc/mkdocs/replace/__init__.py,m=built_in_replacements,t=hardwired
(can be overwritten though, within your replacement module):

`lp:show_src delim=built_in_replacements dir=src/lcdoc/mkdocs/replace lang=python eval=always`


### Example

This repo's :srcref:docs/mdreplace.py .

Here is a `srcref` usage example with title and match string:

```
:srcref:fn=src/lcdoc/lp.py,m=remote_content,t=mytitle
```

We find the first occurance of the match string (m=...) in the file and link to it with given title
(t=...):

Result:

:srcref:fn=src/lcdoc/lp.py,m=remote_content,t=mytitle



## Custom Admonitions

Based on [these][cm] instructions, we provide straightforward custom admonitions via this plugin.

Example:

```
!!! note

    Begin

    !!! :dev: "My Developer Tip"
         
        Some notes for developers....

    End

```

renders:

!!! note

    Begin

    !!! :dev: "My Developer Tip"
         
        Some notes for developers....

    End

Currently the following custom admonitions are defined out of the box:


```python lp:python addsrc
import json
from lcdoc.mkdocs.replace.admons import cust_admons
print(json.dumps(cust_admons, indent=4))
```


### How To Add a Custom Admonition

In your `mdreplace` file:

```python
from lcdoc.mkdocs.replace import admons
# add ours to the predefined ones:
ico = '<svg ....' # raw svg from anywhere. 
ico = 'https://twemoji.maxcdn.com/v/latest/svg/1f4f7.svg' # url
ico = 'material/camera-account.svg' # file in your site-directories/material/.icons
admons.cust_admons['myadmon'] = dict(title="My Default Title", ico=ico, col='rgb(0, 0, 255)', [bgcol=rgba...])
table = {...} # our other replace defs
table.update(admons.admons('dev', 'myadmon', ...))
```

See also the :srcref:fn=docs/mdreplace.py,t=mdreplace.py file in this repo.

The style definition is added once into your page, per used custom admonition. We do not interfere
with any custom style definition in your project.





[cm]: https://squidfunk.github.io/mkdocs-material/reference/admonitions/#customization


