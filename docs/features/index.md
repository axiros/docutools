# Features
## Mkdocs [Plugins](https://www.mkdocs.org/dev-guide/plugins/)
- [Blacklist](blacklist/): Prevents sensitive content showing up in (public) docs
- [Changelog](changelog/): Creates a changelog based on git comments
- [Credits](credits/): Creates a credits page, based on a poetry lock file
- [Find Pages](find-pages/): Adds pages to your nav tree, even when not configured in mkdocs.yml
- **[Literate Programming](lp/)**: Emacs-org babel inspired dynamic evaluation of fenced code blocks
- [Markdown Replace](md-replace/): Replaces markdown before rendering to html. Including or
  excluding replacements within fenced blocks
- [Page Tree](page-tree/): Inserts a breadcrumb into your footer
- [Stats](stats/): Prints a lot of stats about the build process, ready for piping into jq

## Framework

It made sense to bundle all the plugins within one repo, since it offers a few generic features, for
*any* mkdocs plugin.


!!! note

    You still have to enable the plugins you really want, within your `mkdocs.yml` file.  

    The others just waste a little bit of disk space on the build machine but do neither impact
    performance nor size of your builds.

!!! hint "Tech"

    The plugins inherit not directly from `mkdocs.plugins.BasePlugin` but from the intermediate
    `lcdoc.mkdocs.tools.MDPlugin`. This allows their hooks to be wrapped within a metrics and logs
    framework, applicable to all of them.


    - If you want to use the framework for your own plugins, you can inherit from `MDPlugin` as well.

    You gain from

    - an `app` class, providing the log methods and a die method, accepting `**kw` args (see
      [structlog](https://www.structlog.org/en/stable/)), configured during hook run time for the current hook and, when
      applicable, current page.

    - In the stats plugin you can configure, at which log levels you want to have build breaks

    - the plugin and the page have a `stats` dict attribute, in which you can collect metrics. Some
      metrics like run time are collected for you.


    See the [Stats](stats/) plugin for more on this.






