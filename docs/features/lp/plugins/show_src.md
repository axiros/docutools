# show_src


Copies delimitted stanzas within arbitrary files (usually source code) into your docs
and creates links to those files on the repo server.

Format within the source file: :docs:matchstring (no space)

## Parameters

- delim: "matchstring" in the example above (without the ":docs:" prefix).
- dir: Start directly, relative to repo root dir or absolute path
- hide: Optional. True or String: will result in collapsed block

The plugin uses ripgrep to find matches.

## Example

<!-- :docs:this_example -->
### show_src

We included this sentence and the header between match strings....

<!-- :docs:this_example -->

```python lp mode=show_src delim=this_example hide="This Example" addsrc dir=docs/features/lp eval=always
```

