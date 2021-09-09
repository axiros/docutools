"""
## Stats

Prints collected stats on stdout after build.

Intended for piping into / consolidation with [jq](https://stedolan.github.io/jq/download/).

### Config

    config_scheme = (('round_digits', config_options.Type(int, default=4)),)

"""
import json
import os

from mkdocs.config import config_options

from lcdoc.const import LogStats, PageStats, Stats
from lcdoc.mkdocs.tools import MDPlugin, app
from lcdoc.tools import dirname, project, write_file


class StatsPlugin(MDPlugin):
    config_scheme = (
        # :docs:stats_config
        # if not starting with "/": relative to project root.
        # for stdout: set file="-"
        ('file', config_options.Type(str, default='build/lcd-build-stats.json')),
        # round floats to this precision:
        ('round_digits', config_options.Type(int, default=4)),
        # omit zero values:
        ('filter_0', config_options.Type(bool, default=True)),
        # :docs:stats_config
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
        fn = self.config['file']
        if not fn:
            return app.info('no stats file configured')
        if fn == '-':
            return print(json.dumps(s, sort_keys=True))
        if not fn[0] == '/':
            fn = project.root(config) + '/' + fn
        os.makedirs(dirname(fn), exist_ok=True)
        write_file(fn, json.dumps(s, sort_keys=True, indent=4))
        app.info('Have written stats', keys=len(s), file=fn)
