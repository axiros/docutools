#  docutools

```yaml lp mode=make_badges write_readme eval=always
docs # lp: value=pagecount
gh-action # lp: action=ci
pypi
ruff
```


## [MkDocs Documentation](https://axiros.github.io/docutools/) Tools For Developers

This repo is providing a set of plugins for [mkdocs material](https://squidfunk.github.io/mkdocs-material/) compatible documentation.

It is meant to be used as a development dependency for projects, intended to be used mainly by the
developers themselves, i.e. for the more technical, code centric parts of software project documentation.

Most notable feature: **[Literate Programming](./features/lp/)**, i.e. dynamic code execution - tightly integrated within the mkdocs framework.


> Most plugins should work in [other](https://www.mkdocs.org/dev-guide/themes/) mkdocs themes as well. No guarantees though.


## [Feature](https://axiros.github.io/docutools/features/) Gallery



```python lp:python eval=always
'''
Finds all shots, starting with "gl_" and creates a table:
'''
import os
from lcdoc.tools import read_file, insert_file

dr = os.environ['LP_PROJECT_ROOT']
os.chdir(dr)
height = lambda fn: imagesize.get(fn)[1]

def spec(fnf):
    '''title and link is to foo for .../foo/img/gl_bar.png'''
    fn = fnf.split('docs/', 1)[1]
    ti, n = fn.split('/img/', 1)
    t = ti.rsplit('/', 1)[-1]

    # Special convention: gl_foo__bar.png -> we set bar.md as target, if exists:
    n = n.rsplit('.', 1)[0].split('__')
    fnmd = 'docs/' + ti + '/' + n[-1]
    if os.path.exists(fnmd+'.md'):
        t = n[-1]
        ti += '/' + n[1]

    return {'fn': fn, 'lnk': ti, 'tit': t}

imgs = os.popen("fd -L gl_ docs | grep '.png$'").read().splitlines()
imgs = [spec(fn) for fn in imgs]
imgs = sorted(imgs, key=lambda m: m['tit'])

rows, columns = int(len(imgs)/3+1), 3

def img(spec):
    t = '<a href="{lnk}/">{tit}</a><br/>'
    return (t + '<img onclick="event.stopPropagation();" src="{fn}" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>').format(**spec)

R = ['<table id=gallery>']
add = R.append
o = ['odd', 'even']
nr = 0
for r in range(rows):
    add('<tr>')
    for c in range(columns):
        nr += 1
        oe = o[nr % 2]
        lnk = imgs[0]['lnk'] if imgs else ''
        add(f'<td style="cursor: pointer" title="{lnk}" class="{oe}" onclick="window.location.href=\'{lnk}\'">')
        if imgs:
            i = imgs.pop(0)
            add(img(i))
        add('</td>')
    add('</tr>')
add('</table>')
R = '\n'.join(R)
show(R, md=True)

# Put the table also into our README.md, with links adapted:
D = 'https://axiros.github.io/docutools/'
R = R.replace('href="', f'href="{D}')
R = R.replace('src="', f'src="{D}')
insert_file(dr + '/README.md', R, sep='<!-- gallery -->')

```
<!-- lightbox on image click -->
`lp:lightbox outer_match='#gallery '`

<!-- wide output -->
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

???+ "General Questions and Feature Requests"
    `lp:python show=comments`

Last modified: :ctime:
