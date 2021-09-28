#  docutools

```yaml lp mode=make_badges write_readme eval=always
docs # lp: value=pagecount
gh-action # lp: action=ci
pypi
axblack
```


## [Documentation](https://axgkl.github.io/docutools/) building tools

This repo is providing a set of plugins for [mkdocs material](https://squidfunk.github.io/mkdocs-material/) compatible documentation.

It is meant to be used as a development dependency for projects.

Most notable feature: **[Literate Programming](./features/lp/)**.

> Most plugins should work in other mkdocs variants as well. No guarantees though.


## [Feature](https://axgkl.github.io/docutools/features/) Gallery



```python lp:python eval=always
'''
Finds all shots, starting with "gl_" and creates a table:
'''
import os, imagesize
from lcdoc.tools import read_file, insert_file

dr = os.environ['LP_PROJECT_ROOT']
os.chdir(dr)
height = lambda fn: imagesize.get(fn)[1]

imgs = os.popen("fd -L gl_ docs | grep '.png$'").read().splitlines()
imgs = [k[1] for k in sorted([[height(fn), fn] for fn in imgs])]

rows, columns = int(len(imgs)/3+1), 3

def img(fn):
    fn = fn.split('docs/', 1)[1]
    ti = fn.split('/img/', 1)[0]
    t = ti.rsplit('/', 1)[-1]
    t = f'<a href="{ti}/">{t}</a><br/>'
    return t + f'<img src="{fn}" style="max-height: 300px"></img>'

R = ['<table id=gallery>']
add = R.append
o = ['odd', 'even']
nr = 0
for r in range(rows):
    add('<tr>')
    for c in range(columns):
        nr += 1
        oe = o[nr % 2]
        add(f'<td class="{oe}">')
        if imgs:
            i = imgs.pop(0)
            add(img(i))
        add('</td>')
    add('</tr>')
add('</table>')
R = '\n'.join(R)
show(R, md=True)

# into README.md:
D = 'https://axgkl.github.io/docutools/'
R = R.replace('href="', f'href="{D}')
R = R.replace('src="', f'src="{D}')
insert_file(dr + '/README.md', R, sep='<!-- gallery -->')

```

`lp:lightbox outer_match='#gallery '`

<style>
@media only screen and (min-width: 76.25em) {
  .odd { background-color: var(--md-code-bg-color);}
  .md-main__inner {
    max-width: none;
  }
  .md-sidebar--primary {
    left: 0;
    width: 0;
  }
  .md-sidebar--secondary {
    right: 0;
    width: 0;
    margin-left: 0;
    -webkit-transform: none;
    transform: none;   
  }
}

</style>

Last modified: :ctime:

