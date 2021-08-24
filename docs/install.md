# Installation

- Add `docutools = "^<version>"` as a dev dependency.

If in an airtight environment:

Configure the package server in your build framework (e.g. poetry like [this](https://python-poetry.org/docs/repositories/)).

## Development Installation

When you want to add / modify / debug stuff, we recommend a development installation.

- Clone the repo, maybe checkout the tag you want to inspect
- Create and activate a virtual environment with minimum python3.7
- `poetry install`

!!! note "environ file"
    There is an `environ` file with I source on `cd` (if not yet sourced), which activates my conda
    based virtual environment. But this is not a must.



