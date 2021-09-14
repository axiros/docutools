# make_badges

Creates badges. Optionally writes the README.md

## Format

Line separated badge function names with statement level lp parameters.

Functions:

- axblack
- docs (with value=[pagecount], default "mkdocs-material")
- gh_action (with action parameter, default ci)
- pypi

Params:

- value
- label (if not a function name, we take the lp statement value, see example below)
- lnk
- color (default: gray)
- img (when external svg, supply the url)

## Parameters

- write_readme: Create the readme with static badges. That file is not managed by mkdocs - so we
  create it.


## Example

```bash lp addsrc mode=make_badges
hello # lp: value=world lnk=http://github.com 

```

