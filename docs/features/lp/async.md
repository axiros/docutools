# Asynchronous (Lazy) Results Fetching

When results are big, you can prevent the user browser having to fetch them at every page load but
only on demand.

When the [`fmt`](./parameters.md#fmt) parameter puts the results into a tab which is not open at
page load, this will significantly improve page load times and transfer volume, when users do not
open the tabs.



## Mechanics

Simply add the [`fetch`](./parameters.md#fetch)  parameter into the header.

Example:

```
 :fences:bash lp fetch=md_async_example
 <heavy results causing evaluation>
 :fences:
```


Result:

1. At evaluation, the results will then *not* be put into the markdown directly but something like that
  instead (see :srcref:fn=src/lcdoc/lp.py,m=remote_content ).

```html
    <xterm />

         remote_content

    ![](./media/mypage.md_async_example.ansi)
```

1. The results will be written into a `.ansi` file, next to the original markdown page (into a
  subdirectory "media")
1. `fn_frm` will be the link to that file.
1. The javascript shipped with lp will pick up the `xterm` tags and render them. When it sees
   'remote_content`, it will send an XHR to the server, downloading the results. That way the server
   can still remain static.

!!! note
    The results are fetched only when the xterm tag is to be displayed - i.e. not while the tab
    containing it is closed.
