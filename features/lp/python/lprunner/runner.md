# Local LP Blocks :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/lprunner/__init__.py,t=Runner 

Via this you can offer the reader of a page to run all or some LP blocks of a page locally on his
computer.

Add this to your markdown page and an instruction regarding how to run LP blocks with a `runner`
header argument will be presented to the user:

`lp:python show=lprunner addsrc`


All blocks with the `runner` header parameter will then be executed locally, e.g.:


```bash lp runner addsrc
echo "Hello World" 
```

If the user now calls the documentation URL with the `mdrun` script he will see sth like this:

```bash
$ mdrun "https://axiros.github.io/docutools/features/lp/python/lprunner/"

(...) # local tmux window opens, showing the markdown source plus the blocks ready to run:

Via this you can offer the reader of a page to run all or some LP blocks of a page locally on his
computer.

Add this to your markdown page and an instruction regarding how to run LP blocks with a `runner`
header argument will be presented to the user:


All blocks with the `runner` header parameter will then be executed locally, e.g.:

Run echo "Hello World"
a:yes for all e:yes for all, then exit q:quit s:shell y:confirm
[a|e|h|q|s|Y(default)] ?

```

Means the user by default needs to confirm every block run.


This currently works for [bash mode](../../bash/), with or without sessions and is intended to allow
users, trusting you, complex installation automation without tedious copy paste processes. 


## Tech
The `show('lprunner')` statement causes the markdown source of the page to be copied over to site dir, as `runner.md`, so that it is
available to be downloaded by a http client, contained within the `mdrun` script.



## Requirements

The user needs to have the docutools package installed, plus tmux, with minimum version 3.0.


!!! warning "Experimental Feature"

    A more minimal required runner package should be offered, after gathering some feedback, regarding value of
    such "read and run" documentation.
