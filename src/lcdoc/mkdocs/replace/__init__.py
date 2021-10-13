"""
## Markdown Replace

Allows to add replacements into the markdown source, which are replaced by values given
by a python module.

The python module (default is: docs/mdreplace.py) must have a table attribute, either
dict or callable.

When callable and kw args in the signature, it will be called with a lot of context, incl. the mkdocs config and the
current line. Otherwise it will be simply called.


### Features

- The replace values can themselves be callable, and if so, are called at replacement
  time with contextual information: 

  ```python
    replace(
                mdblock=md,
                plugin=self,
                plugin_file=__file__,
                config=config,
                page=page,
                markdown=markdown,
            )
  ```

- If the callable does not require kw args (e.g. time.ctime) we will not pass them
- The callable can return a replacement for the whole line, by returning a dict like
  `{'line': ....}`, i.e. with a "line" key.
- If the replace values are lists (also as returned by the callable), they will be
  properly indented as multiline text.

#### Controlling Replacements Within Fenced Blocks
    - fenced blocks are omitted EXCEPT:
    - if the replacement key is specified like this `key:all:` - then even `:key:` in
      fenced blocks is replaced

### Config

- `seperator`: ':' by default.  
    Example: `':curtime:'`, for `{"cur_time": time.ctime}` based replacements.
- `replacement_file`: when not starting with '/' we'll prefix with docs_dir. Default: "mdreplace.py"
"""


import importlib

from mkdocs.config import config_options

from lcdoc.mkdocs.tools import MDPlugin, app, split_off_fenced_blocks
from lcdoc.tools import exists, now, os, read_file, sys
import inspect

fn_ts = [0]
last_check = [0]


def load_replacement_file(plugin, config):
    fn = plugin.config['replacement_file']
    if now() - last_check[0] < 2:
        return
    try:
        fnmod = fn.rsplit('.py', 1)[0]
        if not fn[0] == '/':
            fn = config['docs_dir'] + '/' + fn
        if fn_ts[0] and os.stat(fn)[7] != fn_ts[0]:
            app.info('Change detected - reloading', fn=fn)
            # cannot reload - have to exec second time. No breaks work then with linenr
            s = read_file(fn)
            m = {}
            exec(s, globals(), m)
            table = m.get('table')
        elif plugin.table:
            return
        else:
            app.debug('Try loading replacement file', fn=fn)
            if not exists(fn):
                return app.info('Will not mdreplace, no lookup file found', fn=fn)
            sys.path.append(os.path.dirname(fn))
            mod = importlib.import_module(fnmod)
            table = getattr(mod, 'table', None)
        fn_ts[0] = os.stat(fn)[7]
        if not table:
            app.warning(
                'Replacement mod requires table attribute', fn=fn, err='no md-replace'
            )
            plugin.table = {}
            return
        d = table(config) if callable(table) else table
        s = plugin.config['seperator']
        l = lambda v: v.splitlines() if isinstance(v, str) and '\n' in v else v
        d1 = {k: v for k, v in d.items() if not ':all:' in k}
        d2 = {k: v for k, v in d.items() if ':all:' in k}
        d2 = {k.replace(':all:', ''): v for k, v in d2.items()}
        plugin.table = dict([('%s%s%s' % (s, k, s), l(v)) for k, v in d1.items()])
        plugin.t_all = dict([('%s%s%s' % (s, k, s), l(v)) for k, v in d2.items()])
    except Exception as ex:
        app.warning('replacement table load error', exc=ex)
        plugin.table = {}


def has_kw(func, _h={}):
    if func in _h:
        return _h[func]
    r = _h[func] = '**' in str(inspect.signature(func))
    return r


def replace(**kw):
    r = []
    mdlines = kw['mdblock']
    stats = kw['page'].stats
    stats['total'] = 0
    t = kw['table']
    while mdlines:
        l = mdlines.pop(0)
        # if 'plugin_do' in str(l): breakpoint()  # FIXME BREAKPOINT
        for k in t:
            if not k in l:
                continue
            stats['total'] += 1
            v = t[k]
            if callable(v):
                stats['func'] = stats.get('func', 0) + 1
                if has_kw(v):
                    v = v(line=l, **kw)
                else:
                    v = v()  # simple funcs like time.ctime
            if isinstance(v, list):
                stats['multiline'] = stats.get('multiline', 0) + 1
                ind = ' ' * len(l.split(k, 1)[0])
                v = ind.join([i for i in v])
            if isinstance(v, dict):
                # a replacement func may deliver the whole new line:
                l = v['line']
            else:
                l = l.replace(k, v)
        r.append(l)
    return r


from functools import partial


class MDReplacePlugin(MDPlugin):
    table = None
    fn_replace = None
    fn_replace_ts = None

    config_scheme = (
        ('seperator', config_options.Type(str, default=':')),
        ('replacement_file', config_options.Type(str, default='mdreplace.py')),
    )

    def on_pre_build(self, config):
        load_replacement_file(self, config)

    def on_page_markdown(self, markdown, page, config, files):
        # a lot of context for the replacement funcs:
        repl = partial(
            replace,
            plugin=self,
            plugin_file=__file__,
            config=config,
            page=page,
            markdown=markdown,
        )
        # hot reload feature:
        load_replacement_file(self, config)
        lines = markdown.splitlines()
        if not getattr(self, 't_all', None):
            return
        lines = repl(mdblock=lines, table=self.t_all)

        # if 'features' in page.url: breakpoint()  # FIXME BREAKPOINT
        mds, fcs = split_off_fenced_blocks(lines)
        MD = ''
        for md in mds:
            MD += '\n'.join(repl(mdblock=md, table=self.table))
            if fcs:
                MD += '\n' + '\n'.join(fcs.pop(0)) + '\n'
        return MD
