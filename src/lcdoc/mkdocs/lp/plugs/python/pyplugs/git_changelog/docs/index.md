# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/git_changelog/__init__.py,t=Changelog

Creates a changelog (using [git-changelog](https://pypi.org/project/git-changelog/)).

- Heavily based on the work of ["pawamoy"](https://github.com/pawamoy).
- Example: This repo's [Changelog Page](../../../../about/changelog.md).

## Syntax

```
`lp:python show=git_changelog style=angular`
```

## Parameters

```python
    style      = Choice(['angular', 'basic', 'atom'], default='angular')
    versioning = Choice(['auto', 'semver', 'calver'], default='auto')
```

"auto": When set to "`auto`", we derive versioning scheme by inspecting your last git tag - if like `X.foo.bar`, with `X` a
number > 2000, we set to calver.

You can set `$versioning` also via environ, which will have precedence then.


!!! caution "Works only with full git history"
    On many CI systems the repo is fechted with --depth=1. If docu is built there, then commit the
    cache file for the changelog page and have it built locally.

Lastly:

- https://joshuatauberer.medium.com/write-joyous-git-commit-messages-2f98891114c4


