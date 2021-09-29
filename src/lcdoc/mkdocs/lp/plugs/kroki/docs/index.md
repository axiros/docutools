# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/kroki/__init__.py,t=kroki

Support for [kroki](https://kroki.com/) diagrams.


Kroki is a metahub for various kinds of diagram types, incl. [plantuml](https://plantuml.com/) (our default).

These are just a few of the growing selection of supported formats:

![](img/gl_kroki_cheat.png)

## Syntax

- Set the `mode` parameter to `kroki[:diagtype]`, with plantuml the default type.
- Set fn to the svg to be produced, relative to your page.
- Diagram source:

    - In the lp block body supply the source
    - Alternatively you could also supply the source as `src` header argument, relative to the page
      or absolute path
      

Default Parameters:

```python lp:show_src delim=lp_kroki_dflts dir=src/lcdoc/mkdocs eval=always
```


## Examples

```bash lp:kroki fn=img/k1 addsrc
rectangle "Main" {
  (main.view)
  (singleton)
}
rectangle "Base" {
  (base.component)
  (component)
  (model)
}
rectangle "<b>main.ts</b>" as main_ts

(component) ..> (base.component)
main_ts ==> (main.view)
(main.view) --> (component)
(main.view) ...> (singleton)
(singleton) ---> (model)

```


`lp:kroki:excalidraw fn=img/k2 addsrc src=excali.json`

`lp:lightbox`

