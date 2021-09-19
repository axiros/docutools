import os
from functools import partial

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.tools import dirname

config, page, Session = (python.config, python.page, python.Session)
make_img = python.make_img


def register(fmts):
    fmts['matplotlib.pyplot'] = matplotlib_pyplot


def matplotlib_pyplot(plt, fn=None, clf=True, **kw):
    f = partial(plt.savefig, transparent=True)
    try:
        return make_img(f, fn=fn)
    finally:
        plt.clf() if clf else 0
