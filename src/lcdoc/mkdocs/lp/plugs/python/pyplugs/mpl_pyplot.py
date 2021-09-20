import os
from functools import partial

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.tools import make_img

config, page, Session = (python.config, python.page, python.Session)


def register(fmts):
    fmts['matplotlib.pyplot'] = matplotlib_pyplot


def matplotlib_pyplot(plt, fn=None, clf=True, **kw):
    f = partial(plt.savefig, transparent=True)
    try:
        return make_img(f, fn=fn, kw=Session.kw)
    finally:
        plt.clf() if clf else 0
