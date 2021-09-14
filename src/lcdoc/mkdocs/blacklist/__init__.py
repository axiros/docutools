"""
## Blacklist

When any word of `$blacklisted_words` (e.g. "mypass::mycompany::myuser")
occurs in non git ignored sources, we die.

This prevents private information being pushed to a public repo.

Set `$blacklisted_words` e.g. via `$(pass show my/sensitive_words)` in an environ file.

This is run after config is read and scans all docs folder content, not just the .md
files.

Requires rg ([ripgrep](https://github.com/BurntSushi/ripgrep)) tool.

"""


from lcdoc.mkdocs.tools import MDPlugin, app, config_options
from lcdoc.tools import os, project, require, sys


def fail_on_blacklisted_words(config, envkey, envsep):
    l = os.environ.get(envkey)
    if not l:
        return app.debug('No $%s to check for blacklisted words' % envkey)
    here = os.getcwd()
    try:
        os.chdir(project.root(config))  # ['docs_dir'])
        require('rg --version', name='ripgrep')
        H = False
        words = [s.strip() for s in l.split(envsep)]
        for w in words:
            if not w.strip():
                continue
            h = os.popen("rg -i '%s'" % w).read()
            if h.strip():
                H = True
                f = app.die if not 'serve' in sys.argv else app.error
                f('Found blacklisted word', word=w, json=h.splitlines()[:10])
        if not H:
            app.info(
                'Blacklist check passed: No occurrance of %s blacklisted words'
                % len(words)
            )
    finally:
        os.chdir(here)


class BlacklistPlugin(MDPlugin):
    config_scheme = (
        ('envkey', config_options.Type(str, default='blacklisted_words')),
        ('envsep', config_options.Type(str, default='::')),
    )

    def on_config(self, config):
        fail_on_blacklisted_words(config, self.config['envkey'], self.config['envsep'])
