# Image :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/convert/__init__.py,t=Convert

Current feature set:

- Creates thumbnails of pdfs, linked to their source.
- Creates image slideshows from pdfs

## Parameters

```python lp mode=show_src delim=convert_defaults dir=src/lcdoc
```

## Thumbnails

When you specify only one page to be converted, we'll create a thumbnail for the pdf link:

```python lp:python addsrc
show('convert', pdf='img/sample.pdf', xpng='img/my_sample.png', width=100) # implicit: pages=0 
```

or using the more [concise](../_tech.md)


`lp:python:convert pdf=img/sample.pdf width=200 pages=2 addsrc`

## Slideshow

When you specify more than one pages to be converted, we'll create a slideshow, incl. a lightbox.


`lp:python:convert pdf=img/sample.pdf width=1000 thumbwidth=200 pages=0-4 addsrc`


## Requirements


You need to have [imagemagick][im][^1] installed (`convert` command available).

!!! tip
    If you use [conda](https://docs.conda.io/en/latest/miniconda.html) for your virtual env, you
    have it, w/o root, via `conda install -c conda-forge imagemagick`

[^1]: Copyright: © 1999-2020 ImageMagick Studio LLC
[im]: https://imagemagick.org/index.php



