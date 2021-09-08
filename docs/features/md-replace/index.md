
## Markdown Replace

Allows to add replacements into the markdown source, which are replaced by values given
by a python module.

Usage: :lnksrc:fn:src/lcdoc/assets/mkdocs/mkdocs.yml,m:lcd-md-replace,t:m

You set up replacements in a python file (default is: docs/mdreplace.py), which must have a table
attribute, either dict or callable.

When callable and kw args in the signature, it will be called with a lot of context, incl. the mkdocs config and the
current line. Otherwise it will be simply called.


### Features

- The replace values can themselves be callable, and if so, are called at replacement
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

- If the callable does not require kw args (e.g. time.ctime) we will not pass them
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


### Example

This repo's :lnksrc:docs/mdreplace.py .
