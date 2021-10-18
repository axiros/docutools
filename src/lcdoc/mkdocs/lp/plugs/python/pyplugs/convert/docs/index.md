# Image :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/convert/__init__.py,t=Convert

Current feature set:

- Creates thumbnails of pdfs, linked to their source.

## Requirements

You need to have [imagemagick][im][^1] installed (`convert` command available).

[^1]: Copyright: © 1999-2020 ImageMagick Studio LLC
[im]: https://imagemagick.org/index.php


## Examples

```python lp:python addsrc
show('convert', pdf='img/sample.pdf', png='img/sample.png', width=100)

```

or using the more concise


`lp:python:convert pdf=img/sample.pdf width=200 addsrc`


