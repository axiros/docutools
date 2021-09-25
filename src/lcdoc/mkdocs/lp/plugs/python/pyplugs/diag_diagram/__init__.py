import os
from lcdoc.mkdocs.lp.plugs import python
from lcdoc.tools import read_file
from lcdoc.mkdocs.tools import app
import shutil

config, page, Session = (python.config, python.page, python.Session)

try:
    from diagrams import Node

    have_diagrams = True
except:
    have_diagrams = None


def copying_icon_loader(self, c={}):
    exists = os.path.exists
    if not c:
        bd = python.config()['docs_dir'] + '/icons_diagrams'
        os.makedirs(bd, exist_ok=True)
        c.update({'build_dir': bd})

    bd = c['build_dir']
    orig = self._orig_load_icon()
    pth = orig.split('/resources/', 1)[1].replace('/', '_')
    dest = bd + '/' + pth
    if not exists(dest):
        shutil.copyfile(orig, dest)
    return dest


if have_diagrams:
    Node._orig_load_icon = Node._load_icon
    Node._load_icon = copying_icon_loader


def register(fmts):
    """registering us as renderer for show(<pyplot module>) within lp python"""
    fmts['diagrams.Diagram'] = make_diag


# from ast import literal_eval as le


# def copy_and_repl_imgs(fn, diag):
#     b = str(diag.dot.body)
#     diag.dot.body = le(b.replace('/home/gk/repos/docutools', '../../..'))

T = '''
<div class="diagrams_container" id="%(id)s">
<svg%(body)s
</div>
'''


def make_diag(diag, fn=None, **kw):
    if not have_diagrams:
        app.die('Please pip install diagrams')

    diag.render()
    if diag.outformat == 'svg':
        dd = python.config()['docs_dir'] + '/'
        pth = python.page().file.src_path.split('/')
        pth.pop() if pth[-1] == 'index.md' else 0
        drel = '../' * (len(pth) - 0)
        f = diag.filename + '.' + diag.outformat
        s = read_file(f)
        s = s.split('<svg', 1)[1]
        s = s.replace(dd, drel).replace('>\n', '>')
        # s = s.replace('"black"', '"#cccccc"')
        # s = s.replace('<polygon ', '<polygon fill-opacity="0.1" ')
        s = T % {'body': s, 'id': python.Session.kw['id']}
        os.unlink(f)
        return s
    else:
        # create pngs normally otherwise:
        app.die('diagrams plugin only supports svg')
