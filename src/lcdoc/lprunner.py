import os
import sys

import httpx

from lcdoc.const import lprunner_sep as sep
from lcdoc.mkdocs.tools import split_off_fenced_blocks
from lcdoc.tools import app, dirname, exists, read_file, write_file


class S:
    fn = None


class Unconfirmed(Exception):
    pass


def confirm(msg):
    print(msg)
    r = input('[q/Y] ? ')
    if r.lower() in ('q', 'n'):
        raise Unconfirmed()


def extract_md_src_from_url(url):
    a = url
    a = (a + '/') if not a.endswith('/') else a
    a += 'runner.md'
    src = httpx.get(a).text
    S.fn = a.split('/', 3)[3].replace('/', '_')
    return src


def parse_cli():
    args = list(sys.argv[1:])
    while args:
        a = args.pop(0)
        if exists(a):
            S.fn = a
        elif a.startswith('http'):
            src = extract_md_src_from_url(a)
            write_file(S.fn, src)
    S.fn = os.path.abspath(S.fn)
    app.name = os.path.basename(S.fn)


class mock:
    def page():
        class page:
            src_path = abs_src_path = S.fn
            stats = {}

        return page

    def config():
        return {'docs_dir': dirname(S.fn)}


def show_md(md):
    md = [md] if isinstance(md, str) else md
    for m in md:
        print(m)


def run_lp(spec):
    src = spec['kwargs'].get('source', '')
    show_md(src)
    if not spec['kwargs'].get('runner'):
        return
    try:
        res = LP.run_block(spec)
    except Unconfirmed as ex:
        print('unconfirmed - bye')
        sys.exit(1)


def run_fn():
    markdown = read_file(S.fn)
    LP.page = mock.page()
    LP.config = mock.config()
    LP.previous_results = {}
    LP.cur_results = {}
    LP.fn_lp = S.fn
    mds, lp_blocks = split_off_fenced_blocks(
        markdown, fc_crit=LP.is_lp_block, fc_process=LP.parse_lp_block
    )
    l = lp_blocks
    while mds:
        show_md(mds.pop(0))
        run_lp(lp_blocks.pop(0)) if lp_blocks else None


def main():
    global LP
    from lcdoc.mkdocs.lp import LP

    parse_cli()
    if not S.fn:
        app.die('Require filename or URL')
    run_fn()


if __name__ == '__main__':
    main()
