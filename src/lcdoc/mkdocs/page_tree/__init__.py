from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin


def url(p):
    try:
        return p.url
    except Exception as ex:
        return url(p.children[0])


class PageTreePlugin(BasePlugin):
    config_scheme = (('join_string', config_options.Type(str, default=' - ')),)

    def __init__(self):
        self.enabled = True
        self.total_time = 0

    def on_pre_page(self, page, config, files):
        # skip if pages are not yet included in the mkdocs config file
        if not page.title:
            return page

        join_str = self.config['join_string']
        me = [[page.title, url(page)]]
        if page.ancestors:
            tree_titles = [(x.title, url(x)) for x in page.ancestors[::-1]] + me
            page.parent_titles = join_str.join([x[0] for x in tree_titles])
            page.parent_links = tree_titles
        else:
            page.parent_titles = page.title
            page.parent_links = me

        return page
