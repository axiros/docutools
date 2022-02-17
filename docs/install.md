# Installation

Installing `docutools` as a non development dependency makes not much sense, the toolset is intended
for generating documentation while/after developing. Means: You want a [Development Installation](./dev_install.md):

Add `docutools = "^<version>"` as a development dependency, e.g. within a :srcref:fn=pyproject.toml file.

## Airtight Environment

("airtight"=no Internet access)

Configure the package server in your build framework (e.g. poetry like [this](https://python-poetry.org/docs/repositories/)).

!!! note

    Some features do require CDN hosted javascript and CSS libs, pulled by the browsers of the
    readers - e.g. jquery.




