# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/make_badges/__init__.py,t=make_badges

Creates badges. Optionally writes the README.md

## Format

Line separated badge function names with statement level lp parameters.

### Builtin Functions

Those (optional) functions will create badges autonomously:

- axblack
- docs (with value=[pagecount], default "mkdocs-material")
- gh_action (with action parameter, default ci)
- pypi

### Params

With these you can create static badges (or overwrite values set by the functions):

- value
- label (if not a function name, we take the lp statement value, see example below)
- lnk
- color (default: gray)
- img (when external svg, supply the url)

## LP Header Parameters

`write_readme`: Inserts the badges within your `README.md`, between separators.

`lp:show_src delim=insert_readme_badges dir=src/lcdoc lang=python`

## Example

```bash lp addsrc mode=make_badges eval=always
hello # lp: value=world lnk=http://github.com 

```

!!! note
    You can also use dicts to supply params (`{'value': 'world', 'lnk': ...}`).
