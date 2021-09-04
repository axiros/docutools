# Installation

- Add `docutools = "^<version>"` as a dev dependency.

If in an airtight environment:

Configure the package server in your build framework (e.g. poetry like [this](https://python-poetry.org/docs/repositories/)).

## Development Installation

When you want to add / modify or only debug stuff, we recommend a development installation.

- Clone the repo, maybe checkout the tag you want to inspect
- Create and activate a virtual environment with minimum python3.7
- `poetry install`
- Optionally source the `environ` or `make` file, to get a few shortcuts (`make` w/o arguments lists them)

!!! tip "environ file"

    I source the `environ` file on `cd` (if not yet sourced) in a shell function. It activates my [conda][cond]
    based virtual environment. But this is not a must.



[cond]: https://docs.conda.io/en/latest/miniconda.html



