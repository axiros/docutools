from lcdoc.mkdocs.lp.plugs import python
import os

config, page, Session = python.config, python.page, python.Session


def register(fmts):
    fmts['matplotlib.pyplot'] = matplotlib_pyplot


def matplotlib_pyplot(plt, innerkw):
    fn = config()['site_dir'] + '/' + page().file.src_path
    fn = fn.rsplit('.md', 1)[0] + '/img'
    os.makedirs(fn, exist_ok=True)
    fnp = 'plot_%(id)s.svg' % Session.kw
    fn += '/' + fnp
    plt.savefig(fn, transparent=True)
    if not innerkw.get('clf'):
        plt.clf()
    return '![](./img/%s)' % fnp
