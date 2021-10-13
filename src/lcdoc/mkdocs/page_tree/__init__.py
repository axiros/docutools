from mkdocs.config import config_options
from lcdoc.mkdocs.tools import MDPlugin, app
from lcdoc.tools import read_file, write_file
import os

exists = os.path.exists


def url(base, p):
    try:
        return '/' + base + '/' + p.url
    except Exception as ex:
        return url(base, p.children[0])


def on_config_add_footer_partial(plugin, config):
    s = '/lcdoc/'
    fnf = __file__.split(s, 1)[0] + s + 'assets/mkdocs/lcd/partials/footer.html'
    s = read_file(fnf)
    d0 = config['theme'].dirs[0]
    fnt = d0 + '/partials/footer.html'
    if not exists(fnt):
        os.makedirs(d0 + '/partials', exist_ok=True)
        write_file(fnt, s)
    else:
        so = read_file(fnt)
        if so == s:
            return app.info('footer.html alrady replaced')
        app.warning('Backing up original footer.html', orig=fnt, backup=fnt + '.orig')
        write_file(fnt + '.org', so)
        write_file(fnt, s)
        app.warning('Have written lcd-page-tree aware footer', fn=fnf)


class PageTreePlugin(MDPlugin):
    config_scheme = (('join_string', config_options.Type(str, default=' - ')),)

    def on_config(self, config):
        on_config_add_footer_partial(self, config)

    def on_pre_page(self, page, config, files):
        # skip if pages are not yet included in the mkdocs config file
        if not page.title:
            return page
        base = page.canonical_url.split('/', 4)[3]
        join_str = self.config['join_string']
        me = [[page.title, url(base, page)]]
        if page.ancestors:
            tree_titles = [(x.title, url(base, x)) for x in page.ancestors[::-1]] + me
            page.parent_titles = join_str.join([x[0] for x in tree_titles])
            page.parent_links = tree_titles
        else:
            page.parent_titles = page.title
            page.parent_links = []

        return page
