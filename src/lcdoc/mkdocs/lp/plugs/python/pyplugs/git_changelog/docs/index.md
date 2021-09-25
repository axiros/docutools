# Changelog :srcref:fn=src/lcdoc/mkdocs/changelog/__init__.py,t=

Creates a changelog (using [git-changelog](https://pypi.org/project/git-changelog/)).

- Heavily based on the work of ["pawamoy"](https://github.com/pawamoy).
- Example: This repo's [Changelog Page](../../../../about/changelog.md).


### Templates

Links default jinja templates over to docs/lcd/changelog.
In order to use your own, overwrite that directory.


### Config

```python
    style      = Choice(['angular', 'basic', 'atom'], default='angular')
    versioning = Choice(['auto', 'semver', 'calver'], default='auto')
```

"auto": When set to "`auto`", we derive versioning scheme by inspecting your last git tag - if like `X.foo.bar`, with `X` a
number > 2000, we set to calver.

You can set `$versioning` also via environ, which will have precedence then.


Lastly:

- https://joshuatauberer.medium.com/write-joyous-git-commit-messages-2f98891114c4


