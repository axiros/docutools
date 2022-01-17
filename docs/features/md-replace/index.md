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
- The callable can return a replacement for the whole line, by returning a dict like
  `{'line': ....}`, i.e. with a "line" key.
- If the replace values are lists (also as returned by the callable), they will be
  properly indented as multiline text.

#### Controlling Replacements Within Fenced Blocks
    - fenced blocks are omitted EXCEPT:
    - if the replacement key is specified like this `key:all:` - then even `:key:` in
      fenced blocks is replaced

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

