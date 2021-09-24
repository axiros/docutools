# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/lightbox/__init__.py,t=lightbox

Wraps content into [featherlight](https://github.com/noelboss/featherlight) lightboxes.

| click on an image below ||
|---|---|
| ![mountainlake](img/m.jpg)  | ![mountainlake](img/m2.jpeg)




## Syntax

### Matching Many Elements (Lightbox Gallery)

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

### Lightbox For Single Elements

Adding a colon behind the mode `lightbox` will return a button, which will lift the following
element into a lightbox:

All javascript in the element should work:

```python
 `lp:lightbox:`
 
 !!! note "Example"
 
     ```python lp:python
     show([['Joe', 42], ['Jane', 32]], columns=['name', 'age'])
     ```
```

Result:

`lp:lightbox:`

!!! note "Example"

    ```python lp:python
    show([['Joe', 42], ['Jane', 32]], columns=['name', 'age'])
    ```


!!! tech
    
    All javascript in the element should work, since we set `persist` to true, i.e. content is
    moved, not copied. Before close we move the content back, in order to address [this](https://github.com/noelboss/featherlight/issues/300) bug.


`lp:lightbox`
