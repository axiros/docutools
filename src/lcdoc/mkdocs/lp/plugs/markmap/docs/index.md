# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/markmap/__init__.py,t=markmap

Support for [markmap.js](https://markmap.js.org/) style mindmaps.

<script>
console.log('in container makrmak')
</script>

```markdown lp mode=markmap eval=always addsrc width=800px height=400px
# markmap

## Links

- <https://markmap.js.org/>
- [GitHub](https://github.com/gera2ld/markmap)

## Related

- [coc-markmap](https://github.com/gera2ld/coc-markmap)
- [gatsby-remark-markmap](https://github.com/gera2ld/gatsby-remark-markmap)

## Features

- links
- **inline** ~~text~~ *styles*
- `multiline `
-
    ```python
    import lcdoc # for LP
    ```
```

Mouse zoom supported.


!!! success "Works within containers"


    ```markdown lp mode=markmap height=100px eval=always addsrc
    # this
    - bar
    - asd
    ## that
    - foo
        - bar
        - baz
    ```



`lp:python lightbox`
