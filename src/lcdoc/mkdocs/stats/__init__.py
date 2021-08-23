"""
## Stats

Prints collected stats on stdout after build.

Intended for piping into / consolidation with [jq](https://stedolan.github.io/jq/download/).

### Config

    config_scheme = (('round_digits', config_options.Type(int, default=4)),)

"""
from lcdoc.const import Stats, LogStats, PageStats
from mkdocs.config import config_options
from lcdoc.mkdocs.tools import MDPlugin, app
import json


class StatsPlugin(MDPlugin):
    config_scheme = (('round_digits', config_options.Type(int, default=4)),)

    def on_post_build(self, config):
        from lcdoc.tools import flatten

        rd = self.config['round_digits']

        s = {'Global': Stats, 'Pages': PageStats, 'Log': LogStats}
        s = flatten(s, sep='.', tpljoin='')
        for k, v in s.items():
            if type(v) == float:
                s[k] = round(v, rd)
        app.info('Collected Stats', hint='pipe into jq to format / consolidate')
        print(json.dumps(s))
