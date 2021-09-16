#  docutools

```yaml lp mode=make_badges write_readme eval=always
docs # lp: value=pagecount
gh-action # lp: action=ci
pypi
axblack

```


## [Documentation](https://axgkl.github.io/docutools/) building tools

This repo is providing a set of plugins for [mkdocs material](https://squidfunk.github.io/mkdocs-material/) compatible documentation.

It is meant to be used as a development dependency for projects.

Most notable feature: **[Literate Programming](./features/lp/)**.

> Most plugins should work in other mkdocs variants as well. No guarantees though.

Note: Some features are not yet documented.


Last modified: :ctime:

!!! note
    ```markdown lp mode=markmap eval=always
    # Root


    - foo
        - asdf
            - asdfasd
                - asdfasd
                    - fooasdfasd
    - foo
    - foo
    - foo
    - foo

## Branch 1

    * Branchlet 1a
    * Branchlet 1b

## Branch 2

    * Branchlet 2a
    * Branchlet 2b
    ```
