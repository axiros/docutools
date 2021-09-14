# Changelog :srcref:fn=src/lcdoc/mkdocs/changelog/__init__.py,t=

Creates a CHANGELOG.md (using [git-changelog](https://pypi.org/project/git-changelog/)).

- Heavily based on the work of ["pawamoy"](https://github.com/pawamoy).
- Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-changelog,t=m
- File created: `<project root>/CHANGELOG.md`.
- Example: This repo's [Changelog Page](../../about/changelog.md).


!!! warning "Example Only for Demo Purpose of the Plugin"

    I include this CHANGELOG.md to show off, what this plugin **could** do, when commits *would* be proper.

    Naturally the changelog will be no good marketing for your project, if your commits are bad.
    This might be okayish, when you work alone - but in teams it is a no go.

    The author's diszipline sucks - but up to now I work alone on this repo :sweat:.






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

----

Reminder: Mkdocs includes work like:

```bash
~/repos/docutools❯ cat docs/about/changelog.md
{ !CHANGELOG.md!} # w/o the space between `{` and `!`.
```

Lastly:

- https://joshuatauberer.medium.com/write-joyous-git-commit-messages-2f98891114c4


