"""
## Stats

Prints collected stats on stdout after build.

Intended for piping into / consolidation with [jq](https://stedolan.github.io/jq/download/).

### Config

    config_scheme = (('round_digits', config_options.Type(int, default=4)),)

"""
import json

from mkdocs.config import config_options

from lcdoc.const import LogStats, PageStats, Stats
from lcdoc.mkdocs.tools import MDPlugin, app


class StatsPlugin(MDPlugin):
    config_scheme = (
        ('round_digits', config_options.Type(int, default=4)),
        ('filter_0', config_options.Type(bool, default=True)),
    )

    def on_post_build(self, config):
        from lcdoc.tools import flatten

        rd = self.config['round_digits']
        filter_0 = self.config['filter_0']

        s = {'Global': Stats, 'Pages': PageStats, 'Log': LogStats}
        s = flatten(s, sep='.', tpljoin='')
        if rd:
            r = lambda v: round(v, rd) if type(v) == float else v
            s = dict([(k, r(v)) for k, v in s.items()])
        l = len(s)
        if filter_0:
            s = dict(filter(lambda x: x[1] != 0, s.items()))
        f = l - len(s)
        if f:
            s['Filtered_0s'] = f

        app.info('Collected Stats', hint='pipe into jq to format / consolidate')
        print(json.dumps(s))
