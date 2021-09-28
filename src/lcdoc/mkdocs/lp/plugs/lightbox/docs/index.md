# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/lightbox/__init__.py,t=lightbox

Wraps content into [featherlight](https://github.com/noelboss/featherlight) lightboxes.

| click on an image below ||
|---|---|
| ![mountainlake](img/m.jpg)  | ![mountainlake](img/m2.jpeg)




## Syntax

### Matching Many Elements (Lightbox Gallery)

At the bottom of your page add an lp stanza like this

```
 `lp:lightbox [outer_match=... match=... target=...]`
```

or the normal form:

```
 ```sth lp:lightbox match=img target=src ...
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

Default Parameters:

`lp:show_src delim=lightbox-defaults dir=src/lcdoc eval=always`



## Lightbox For Single Elements

Adding a colon behind the mode `lightbox` will return a button, which will lift the **following
element** into a lightbox:

```
`lp:lightbox:`
*Example element with the lightbox button to the right*
```

Renders:


`lp:lightbox:`
*Example element with the lightbox button to the right*

The next element may also be html.

You may even use the tag *witin* html - then wrapped into an outer tag and on a single line, so that
we detect the statement while parsing the source markdown page:

Source:

```html
<div style="color:blue"> Not in box
<p>
`lp:lightbox:`
</p>
<div style="color:red"> In lightbox </div></div>
```

Renders:

<div style="color:blue"> Not in box
<p>
`lp:lightbox:`
</p>
<div style="color:red"> In lightbox </div></div>

Any such lp expression within a page automatically triggers the inclusion of the lightbox and jquery libs into the page.

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
