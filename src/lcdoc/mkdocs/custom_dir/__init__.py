from mkdocs.config import config_options

from lcdoc.mkdocs.tools import MDPlugin, app
from lcdoc.tools import dirname, exists, os, project

link = 'docs/lcd'
d_assets_mkdocs_theme = '/assets/mkdocs/lcd'


def add_cust_dir_link():
    to = project.root() + '/docs/lcd'
    if exists(to):
        return app.info('custom theme exists', location=to)
    import lcdoc

    f = dirname(lcdoc.__file__)
    f += d_assets_mkdocs_theme
    cmd = 'ln -s "%s" "%s"' % (f, to)
    app.warning('Linking custom dir', cmd=cmd)
    os.system(cmd)
    if not exists(to):
        app.die('link creation failed', frm=f, to=to)
    hint = 'to customize please copy the files, they will be default againg, after next lcd update'
    app.info('mkdocs custom theme enabled via link', json=dict(frm=f, to=to, Hint=hint))


class CustomDirPlugin(MDPlugin):
    config_scheme = (('join_string', config_options.Type(str, default=' - ')),)

    def __init__(self):
        """
        Setting the link to custom lcd dir in docs

        We are using that in mkdocs yaml as custom dir but mkdocs won't call any hook
        when this is missing. So we have to do it here already, w/o a proper config
        object.

        So we have to rely on mkdocs build being called the first time within the root
        dir :-/

        """
        if exists(link):
            return
        if not exists('docs'):

            # we cannot raise here, we can't dissallow being started from elsewhere user
            # won't have the link but he'll read the docs hopefully when mkdocs fails
            # with custom dir not found and call correctly the first time then:
            return

        project.root(root=os.getcwd())
        add_cust_dir_link()
