import json
import os
import sys
import time

from pygments import highlight
from pygments.lexers import JsonLexer

from lcdoc.const import LogStats, PageStats, Stats, now_ms, t0

now = time.time

B = lambda s: '\x1b[1m%s\x1b[0m' % s
V = lambda s: '\x1b[2m%s\x1b[0m' % s
L = lambda s: '\x1b[2;38;5;245m%s\x1b[0m' % s
M = K = B


try:
    from pygments.formatters import Terminal256Formatter
except:
    from pygments.formatters.terminal import TerminalFormatter

    Terminal256Formatter = TerminalFormatter


# ready to make partials for changing the defaults:
def coljhighlight(
    s,
    style=None,
    indent=4,
    sort_keys=True,
    add_line_seps=True,
    # logger might be set to colors off, e.g. at no tty dest:
    colorize=True,
    # automatic indent only for long stuff?
    no_indent_len=0,
    jsl=[0],
):
    if not jsl[0]:
        jsl[0] = JsonLexer()
    if not isinstance(s, str):
        if indent and no_indent_len:
            if len(str(s)) < no_indent_len:
                indent = None
        try:
            s = json.dumps(s, indent=indent, sort_keys=sort_keys, default=str)
        except Exception:
            try:
                # the sort may fail: TypeError: '<' not supported between instances of 'int' and 'str'
                s = json.dumps(s, indent=indent, default=str)
            except Exception:
                from lcdoc.tools import flatten

                return coljhighlight(
                    flatten(s, sep='.', tpljoin='_'),
                    style=style,
                    indent=indent,
                    sort_keys=sort_keys,
                    add_line_seps=add_line_seps,
                    colorize=colorize,
                    no_indent_len=no_indent_len,
                )

    if colorize:
        # we may be called by structlog, then with style (from
        # FLG.log_dev_coljson_style)
        # or direct
        res = highlight(s, jsl[0], Terminal256Formatter())
    else:
        res = s

    if add_line_seps:
        res = res.replace('\\n', '\n')

    return res


def tokw(kw):
    n = app.name
    n = (L(' [%s] ' % n)) if n else ''
    j = kw.pop('json', 0)
    m = ' '.join(['%s:%s' % (L(str(k)), B(str(v))) for k, v in kw.items()])
    m += (n + '\n' + coljhighlight(j)) if j else n
    return m


ign_errors = os.environ.get('ignore_err', '').split('::')


def log(level_name, meth, msg, kw, _err_levels={'error', 'fatal', 'die'}):
    if ign_errors and level_name in _err_levels:
        if any([p for p in ign_errors if p in msg]):
            return app.warning('Ignored Err, level %s' % level_name, orig_msg=msg, kw=kw)
    store = log_majors[level_name]
    dt = now_ms() - t0[0]
    if store is not None:
        store.append([dt, app.name, msg, kw])
    app.log_stats[level_name] += 1
    meth(B(msg + '  ') + tokw(kw))


log_levels = ['debug', 'info', 'warning', 'error', 'fatal']
log_majors = {k: [] if k[:3] not in ['deb', 'inf'] else [] for k in log_levels}
level_by_name = {n: (i + 1) * 10 for n, i in zip(log_levels, range(len(log_levels)))}


class app:
    """
    Provider of app.info, app.die, ...

    """

    name = None
    level = 20
    log_stats = LogStats

    def die(msg, **kw):
        outputter[0] = print
        app.fatal(msg, **kw)
        sys.exit(1)

    def setup_logging(logging_system, name=None, c=[0]):
        app.name = name if name is not None else app.name
        try:
            # only one logging system => only once:
            if c[0]:
                return
            ls = p = logging_system
            for lm in log_levels:
                h = getattr(ls, lm)
                setattr(app, lm, lambda msg, lm=lm, h=h, **kw: log(lm, h, msg, kw))
            try:
                while not p.handlers:
                    p = p.parent
            except Exception as ex:
                app.level = 20
                return
            app.level = p.handlers[0].level
        finally:
            c[0] = True


for lm in log_levels:
    setattr(app, lm, lambda msg, lm=lm, **kw: log(lm, printout, ('[%s] ' % lm) + msg, kw))
    app.log_stats[lm] = 0


def printout(msg):
    outputter[0](msg)


outputter = [print]
