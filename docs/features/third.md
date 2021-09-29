# Plugins

`docutools` will install 3rd party plugins for mkdocs, ready for use right away.

See :srcref:pyproject.toml, for the packages we depend on.


!!! note "Size"
    Those plugins increase the initial download time of documentation, if enabled in `mkdocs.yml`.
    Users which stay on your documentation page, having the libs cached at subsequent visits.


## Which

- We have pretty much all of these:  
https://squidfunk.github.io/mkdocs-material/reference/abbreviations/.

- And a few of these:  
https://facelessuser.github.io/pymdown-extensions/extensions/superfences/

- Plus some standard markdown extensions, e.g. tables.

- And also our own ones, described in this documentation.

See the :srcref:mkdocs.yml file to get an overview.

Below a few important extensions - but check the above pages for details on usage:
 
## Admonitions

!!! hint "A hint"
    this is an admonition.


```
!!! hint "A hint"
    this is an admonition.
```

See https://squidfunk.github.io/mkdocs-material/reference/admonitions/

## Critic

- ==This was marked==
- ^^This was inserted^^
- ~~This was deleted~~


```
- ==This was marked==
- ^^This was inserted^^
- ~~This was deleted~~
```

See https://squidfunk.github.io/mkdocs-material/reference/formatting/


## Details

???+ note "Open styled details"

    ??? danger "Nested details!"
        And more content again.

```
???+ note "Open styled details"

    ??? danger "Nested details!"
        And more content again.


```



## Footnotes

Footnotes[^1] have a label[^@#$%] and the footnote's content.

```
Footnotes[^1] have a label[^@#$%] and the footnote's content.

and elsewhere:

[^1]: This is a footnote content.
[^@#$%]: A footnote on the label: "@#$%".
```

[^1]: This is a footnote content.
[^@#$%]: A footnote on the label: "@#$%".

## Icons and Emojis

See [here](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/) for an emoji search
box.

:fontawesome-brands-linux:
:smile:

- :material-account-circle: – `.icons/material/account-circle.svg`
- :fontawesome-regular-laugh-wink: – `.icons/fontawesome/regular/laugh-wink.svg`
- :octicons-octoface-24: – `.icons/octicons/octoface-24.svg`
- :fontawesome-brands-twitter:{: style="color: #1da1f2" } – Twitter, colorized, using style attr


```
:fontawesome-brands-linux:
:smile:

- :material-account-circle: – `.icons/material/account-circle.svg`
- :fontawesome-regular-laugh-wink: – `.icons/fontawesome/regular/laugh-wink.svg`
- :octicons-octoface-24: – `.icons/octicons/octoface-24.svg`
- :fontawesome-brands-twitter:{: style="color: #1da1f2" } – Twitter, colorized, using style attr

```

### Keyboard Symbols

This `++ctrl+alt+delete++` is rendered: ++ctrl+alt+delete++


## Snippets

Allow to embed complex other content into your markdown.

In your mkdocs.yml you can then supply custom base paths, containing e.g. your own abbreviations, libraries or whatever you require on certain pages.


This is [a demo][demo]. The actual link is provided by an import of a text file (e.g. here :srcref:docs/links.txt ), loaded via a snippet.


```
This is [a demo][demo]. 

And elsewhere, e.g. at the bottom embed the links:

--8<--  
links.txt
--8<--  
```

Note that you can provide, in :srcref:mkdocs.yml , custom locations for such snippets, i.e. within project.

--8<--
links.txt
--8<--



## Style Attributes / Images


![](img/linux.png){: style="height:200px" align=right loading=lazy .zoom }


=== "Source"
    ```
    ![](img/linux.png){: style="height:200px" align=right loading=lazy .zoom }
    ```


--8<--
zoom
--8<--

for the zoom you need the snippet:

## Tables

Table header click to sort:

| Method      | Description                          |
| ----------- | ------------------------------------ |
| `GET`       | :material-check:     Fetch resource  |
| `PUT`       | :material-check-all: Update resource |
| `DELETE`    | :material-close:     Delete resource |


```
| Method      | Description                          |
| ----------- | ------------------------------------ |
| `GET`       | :material-check:     Fetch resource  |
| `PUT`       | :material-check-all: Update resource |
| `DELETE`    | :material-close:     Delete resource |

```

## Tabs

=== "First Tab"
    
    header

    === "First Nested Tab"

        markdown content of first nested tab
        

    === "Second Nested  Tab"

        markdown content of second nested tab
        

=== "Second Tab"

    markdown content of second tab
    

=== "Source"

    ```

    === "First Tab"
        
        header

        === "First Nested Tab"

            markdown content of first nested tab
            

        === "Second Nested  Tab"

            markdown content of second nested tab
            

        

    === "Second Tab"

        markdown content of second tab
        

    ```



## Tasklists


Task List

- [X] item 1
    * [X] item A
    * [ ] item B
        more text
        + [x] item a

```

Task List

- [X] item 1
    * [X] item A
    * [ ] item B
        more text
        + [x] item a
        + [ ] item b

```




See https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/ about styling.


## Md in HTML

<!-- drives the editor syn highlighter crazy -> at the end -->

Works even within markdown, i.e. within tabs:

=== "Source"

    <div markdown="block" style="background-color: purple">

    A *Markdown* paragraph within html setting the background color to purple.

    * A list item.
    * A second list item.

    ```python
    # and some fenced code within the html
    foo = "bar"
    ```

    </div>

=== "Source"
    ```

        <div markdown="block" style="background-color: purple">

        A *Markdown* paragraph within html setting the background color to purple.

        * A list item.
        * A second list item.

        ```python
        # and some fenced code within the html
        foo = "bar"
        ```

        </div>

    ```



