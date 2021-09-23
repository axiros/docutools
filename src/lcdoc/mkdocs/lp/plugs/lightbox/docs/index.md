# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/lightbox/__init__.py,t=lightbox

Wraps content into [featherlight](https://github.com/noelboss/featherlight) lightboxes.

| click on an image below ||
|---|---|
| ![mountainlake](img/m.jpg)  | ![mountainlake](img/m2.jpeg)


`lp:lightbox`


## Syntax

At the bottom of your page add an lp stanza like this

```
 `lp:lightbox [match=... target=...]`
```

or the normal form:

```
 ```sth lp:lightbox match=img target=src
 ```
```

The library works not only on markdown images but also on html images or other content. 

You may specify jquery element matchers and featherlight targets also in the body (then with more
than one), like this:

```python
 ```b lp:lightbox addsrc
 [{'match': 'img', 'target': 'src'}, # the default (you may omit this)
  ...
 ]
 ```
```




