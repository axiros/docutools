# Page Tree :srcref:fn=src/lcdoc/mkdocs/page_tree/__init__.py,t=

Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-page-tree,t=m

![](./img/gl_tree_ex.png)


## Features

- The Next page link is now consisting of a breadcrumb style hirarchy of links.
- The big link areas for previous and next are still kept, when not exactly over such a breadcrumb link.


## Mechanics

- The logical tree with links is built in the `on_pre_page` hook.
- The display is controlled by a custom `footer.html` partial.

!!! warning "Brutally Hammering our footer.html in"

    The plugin, when activated, will write `partials/footer.html` into the first directory in the mkdocs `config['theme'].dirs` list.

    This directory is either

    - your [custom theme](https://squidfunk.github.io/mkdocs-material/customization/#extending-the-theme), when you configured one OR
    - the mkdocs material dir

    In both(!) cases we backup any existing footer.html and then write ours into that dir.

