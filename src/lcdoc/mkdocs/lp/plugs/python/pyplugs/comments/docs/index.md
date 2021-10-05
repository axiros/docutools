# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/comments/__init__.py,t=Comments

Adds a Comments Section, using [`utteranc.es`](https://utteranc.es/)

The comments are hosted by github issues and fetched via a central bot at `utteranc.es`.

!!! important
    - Based on a central bot
    - Works for public repos hosted on github *exclusively*. 


## Features

- Supports mkdocs materials' [`navigation.instant`](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/), i.e. comments sections are (re-)loaded on nav clicks.
- Supports hiding the comments within collapsed details sections

## Syntax

```
`lp:python show=comments`
```

### Parameters

```python lp mode=show_src delim=comments_defaults dir=src/lcdoc/mkdocs/lp eval=always
```

## Example


Code: 

```

 ??? "Questions and Comments?"
     `lp:python show=comments eval=always`


```

Renders:

??? "Questions and Comments?"
    `lp:python show=comments eval=always`


