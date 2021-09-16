# Find-Pages :srcref:fn=src/lcdoc/mkdocs/find_pages/__init__.py,t=

Adds pages to your nav tree, even when not referenced in `mkdocs.yml`.

The adding is done by inspecting the location of the files within the docs tree.


Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-find-pages,t=m

Example: The Literate Programming [plugin docs](../lp/plugs/overview/) are added to nav via find-pages:

In this repos's `mkdocs.yml` we have

```yaml
- lcd-lp
- lcd-find-pages:
      find-pages:
        - features/lp/plugs/
```

- lcd-lp at config hook time will link all existing plugin docs to the docs tree
- lcd-find-pages, with config above adds them to nav

Note: `find_pages` can be also additionally supplied via an environ variable.
