from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin


class PageTreePlugin(BasePlugin):
    config_scheme = (('join_string', config_options.Type(str, default=' ')),)

    def __init__(self):
        self.enabled = True
        self.total_time = 0

    def on_pre_page(self, page, config, files):
        # skip if pages are not yet included in the mkdocs config file
        if not page.title:
            return page

        join_str = self.config['join_string']

        if page.ancestors:
            tree_titles = [x.title for x in page.ancestors[::-1]] + [page.title]
            page.tree_title = join_str.join(tree_titles)
        else:
            page.tree_title = page.title

        return page
