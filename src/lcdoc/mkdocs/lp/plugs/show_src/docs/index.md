# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/show_src/__init__.py,t=show_src

Copies delimitted stanzas within arbitrary files (usually source code) into your docs.

Also creates links to those files on the repo server.

Format within the source file: `:docs:matchstring` (no space after the colon)

## Parameters

- delim: "matchstring" in the example above (without the ":docs:" prefix).
- dir: Start directly, relative to repo root dir or absolute path
- hide: Optional. True or String: will result in collapsed block

The plugin uses ripgrep (`rg`) to find matches.

## Example

<!-- :docs:this_example -->
### show_src

We included this sentence and the header between match strings....

<!-- :docs:this_example -->

```python lp mode=show_src delim=this_example hide="This Example" addsrc dir=src/lcdoc/mkdocs/lp/plugs eval=always
```



!!! tip
    For the shortform you may want to use the `lang` parameter, to get proper highlighting:

    ```
      `lp:show_src delim=this_example hide="This Example" dir=src/lcdoc/mkdocs/lp/plugs lang=python`
    ```
