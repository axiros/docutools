"""
## Stats

Prints collected stats on stdout after build.

Intended for piping into / consolidation with [jq](https://stedolan.github.io/jq/download/).

### Config

    config_scheme = (('round_digits', config_options.Type(int, default=4)),)

"""
from lcdoc import log
import json
import os
import sys

from mkdocs.config import config_options

from lcdoc.const import LogStats, PageStats, Stats
from lcdoc.mkdocs.tools import MDPlugin, app
from lcdoc.tools import dirname, exists, project, read_file, write_file

last_stats = {}


def get_fn_and_set_last(self, config):
    """On serve and '-' we work with the cached last stats. Else we read the file if present"""
    fn = self.config['dump_stats']
    if not fn:
        app.info('no stats file configured')
        return None

    if fn == '-':
        return fn
    else:
        fn = project.abs_path(fn, config, mkdirs=True)
        if exists(fn):
            os.rename(fn, fn + '.prev.json')
        if last_stats:
            return fn
        l = read_file(fn + '.prev.json', dflt='')
        if l:
            last_stats.update(json.loads(l))
        return fn

        # write_file(fn, json.dumps(s, sort_keys=True, indent=4))
        # app.info('Have written stats', keys=len(s), file=fn)


def get_diff(s, minval):
    isminv = lambda v, m=minval: isinstance(v, float) and v == m
    d, o = {'added': {}, 'changed': {}}, last_stats
    d['removed'] = [k for k in o if not k in s and not isminv(o[k])]
    for k, v in s.items():
        vo = o.get(k)
        if vo is None:
            if isinstance(v, float) and v < 2 * minval:
                continue
            d['added'][k] = v
        elif vo != v:
            if isinstance(vo, float) and isinstance(v, float):
                if int(vo * 10) == int(v * 10):
                    continue
            d['changed'][k] = [vo, v]
    d['changed'].pop('Filtered_0_Values', 0)
    for k in {'added', 'removed', 'changed'}:
        if not d.get(k):
            d.pop(k)
    return d


def filter_logs(sever):
    """beyond info we kept all logs in a ram cache (log_majors)
    Here we return those incl. and beyond sever(=warning or error or fatal)
    """

    l = log.log_majors
    if not sever or not sever in l:
        return
    logs = []
    m = log.log_levels
    [logs.append([k, l.get(k)]) for k in m[m.index(sever) :] if l.get(k)]
    return logs, sum([len(i[1]) for i in logs])


def by_ts(store):
    def d(l, L):
        l.insert(1, log.level_by_name[L])
        if not l[-1]:
            l.pop()
        return l

    k = lambda i: i[0]
    return sorted([d(l, L) for L, logs in store.items() for l in logs], key=k)


class StatsPlugin(MDPlugin):
    # :docs:stats_config
    C = config_options.Choice
    log_maj = lambda d, C=C: C(['warning', 'error', 'fatal', 'none'], default=d)
    config_scheme = (
        # if not starting with "/": relative to project root.
        # for stdout: set file="-"
        ('dump_stats', config_options.Type(str, default='build/lcd-stats.json')),
        # round floats to this precision:
        ('round_digits', config_options.Type(int, default=2)),
        # omit zero values:
        ('filter_0', config_options.Type(bool, default=True)),
        # helpfull to see changes at serve
        ('print_diff', config_options.Type(bool, default=True)),
        # write the logs as json (same dir than fn)
        ('dump_logs', config_options.Type(str, default='build/lcd-logs.json')),
        # print all logs from this level again at end of build:
        ('repeat_major_log_events', log_maj('warning')),
        # fail mkdocs build on errors, you don't want broken docs published:
        ('fail_build_on_log_events', log_maj('error')),
    )
    # :docs:stats_config

    def on_post_build(self, config):
        from lcdoc.tools import flatten

        fn = get_fn_and_set_last(self, config)
        rd = self.config['round_digits']
        minval = 5 * 10 ** -rd
        filter_0 = self.config['filter_0']

        s = {'Global': Stats, 'Pages': PageStats, 'Log': LogStats}
        s = flatten(s, sep='.', tpljoin='')
        if rd:
            r = lambda v: round(v, rd) if type(v) == float else v
            s = dict([(k, r(v)) for k, v in s.items()])
        l = len(s)
        if filter_0:
            s = dict(filter(lambda x: x[1] > minval, s.items()))
        f = l - len(s)
        if f:
            s['Filtered_0_Values'] = f

        if last_stats and self.config['print_diff']:
            diff = get_diff(s, minval=minval)
            msg = 'Stats changes since last run'
            msg = ('No s' + msg[1:]) if not diff else msg
            app.info(msg, json=diff)

        last_stats.clear()
        last_stats.update(s)
        kw = dict(filtered_near_zero_vals=filter_0)
        if filter_0:
            kw['minval'] = minval
        if fn == '-':
            app.info('Collected Stats', hint='pipe into jq to consolidate', **kw)
            print(json.dumps(s, sort_keys=True))
        elif fn:
            write_file(fn, json.dumps(s, sort_keys=True, indent=4))
            app.info('Have written stats', keys=len(s), file=fn, **kw)

        sever = self.config['repeat_major_log_events']
        logs, cnt = filter_logs(sever=sever)
        if logs:
            app.info('Logs of severity %s and higher' % sever, json=logs, count=cnt)

        l = log.log_majors
        fn = self.config['dump_logs']
        if fn:
            fn = project.abs_path(fn, config, mkdirs=True)
            if exists(fn):
                os.rename(fn, fn + '.prev.json')
            ol, j = by_ts(l), json.dumps
            write_file(fn, '\n'.join(j(i, default=str) for i in ol))
            app.info('Dumped logs', fn=fn, count=len(ol))

        bsever = self.config['fail_build_on_log_events']
        if bsever != sever:
            logs, cnt = filter_logs(sever=bsever)

        if logs:
            # won't interrupt server mode for this
            m = app.error if 'serve' in sys.argv else app.die
            m('Build is broken, have %s critical logs' % cnt)

        [i.clear() for k, i in l.items()]
