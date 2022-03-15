# Find-Pages :srcref:fn=src/lcdoc/mkdocs/find_pages/__init__.py,t=

Adds pages to your nav tree, even when not referenced in `mkdocs.yml`.

The adding is done by inspecting the location of the files within the docs tree.


Example: The Literate Programming [plugin docs](../lp/plugs/) are added to nav via find-pages:

In this repos's `mkdocs.yml` we have

```yaml
- lcd-lp
- lcd-find-pages:
      find-pages:
        - features/lp/plugs/
```

- lcd-lp plugin will, at config hook time, link all existing plugin docs to the docs tree
- lcd-find-pages, with config above adds them to nav

Notes:

- `find_pages` can be also additionally supplied via an environ variable.
- correct insertion requires a well defined `h1` header - we will take all upper cased words. If
  there are none, we will take filename without `.md` or container directory, if filename is `index.md`.
- correct insertion also requires, that the insertion point of the first doc page not declared in
  nav is following the intended page before it, when you sort ALL filenames, declared and
  undeclared, alphabetically.

You can also *force* a certain insertion point, by supplying the searched dir together with an
`after` key as dict(s), like:

```yaml
nav:
  - Overview: index.md
  - Blueprint:
      - Overview: blueprint/index.md
  - About:
 
(...)

  - lcd-find-pages:
      find-pages:
        - dir: blueprint
          after: blueprint/index.md

```
