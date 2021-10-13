from lcdoc.tools import dirname, exists, os, app


def make_plugin_docs(config):
    """We want the plugins really self contained, incl. all - also the docs
    So we scan whats there and symlink over
    """
    from lcdoc.mkdocs import lp

    def make(pth, dd):
        D = dirname(lp.__file__) + '/plugs' + pth
        dd = config['docs_dir'] + dd
        if not exists(dd):
            os.makedirs(dd, exist_ok=True)

        c = []
        for k in sorted(os.listdir(D)):
            # k e.g. 'mermaid'
            d = D + '/' + k
            fnr, fnp = d + '/docs/index.md', d + '/__init__.py'
            if not exists(fnr) or not exists(fnp):
                continue
            t = dd + '/' + k
            if not exists(t + '/index.md'):
                f = '../../../../src/lcdoc/mkdocs/lp/plugs%s/%s/docs' % (pth, k)
                os.symlink(f, t)
                c.append([f, t])
        if c:
            app.info('Plugs doc symlink created', json=c)

    # TODO: also custom dir?
    make('', '/features/lp/plugs')
    make('/python/pyplugs', '/features/lp/python')


run = make_plugin_docs
