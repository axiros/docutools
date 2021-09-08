# Changelog :lnksrc:fn:src/lcdoc/mkdocs/changelog/__init__.py,t:

Usage: :lnksrc:fn:src/lcdoc/assets/mkdocs/mkdocs.yml,m:lcd-changelog,t:m

- Creates CHANGELOG.md (using [git-changelog](https://pypi.org/project/git-changelog/)).
- Example: This repo's [Changelog Page](../../about/changelog.md).
- Heavily based on [Timothée Mazzucotelli](https://github.com/pawamoy)'s work.

- File created: `<project root>/CHANGELOG.md`.

Reminder: Includes work like:

```bash
~/repos/docutools❯ cat docs/about/changelog.md
{ !CHANGELOG.md!} # w/o the space between `{` and `!`.
```



### Templates

Links default jinja templates over to docs/lcd/changelog.
In order to use your own, overwrite that directory.


### Config

```python
    style      = Choice(['angular', 'basic', 'atom'], default='angular')
    versioning = Choice(['auto', 'semver', 'calver'], default='auto')
```

when set to auto we derive by inspecting your last git tag - if like X.foo.bar with X a
number > 2000 we set to calver.

You can set `$versioning` also via environ, which will have precedence then.



