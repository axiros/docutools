# Conda: Homebrew on Stereoids

[Conda][cond] allows to have **python** and **non python** binaries installed

- **distribution** independent
- under an **arbitrary prefix**, self contained, i.e.:
    - transferable between systems of the same architecture
    - cacheable (e.g. in a CI pipeline)
    - mountable (e.g. into container images)

- have those installable as **non root** user.

## Details

All is under one path prefix, definable at *install* (not build) time.

Conda is more like [homebrew](https://brew.sh/) than it is like pip, but w/o the hard dependency on
`/usr/local/bin` - incl. the permissions hassle. Means, you can have many homebrew trees, per user, within one
filesystem.

!!! dev "Mechanics"

    They achieve this not by going the huge "all in" (static binaries) way but by replacing
    placeholders in the executables and libs with the actual prefix at install time. 


Tradeoffs:

- installs are requiring more time - conda environments are not meant to be created at every
  test run but rather cached or present on your "pet systems".
- their binaries may not be as well security maintained as the packages of a huge distribution (which you
  have to install as root, using e.g. dnf or apt-get).

[cond]: https://docs.conda.io/en/latest/miniconda.html
