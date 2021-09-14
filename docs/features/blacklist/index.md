# Blacklist :srcref:fn=src/lcdoc/mkdocs/blacklist/__init__.py,t=

Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-blacklist,t=m

When any word of `$blacklisted_words` (e.g. "mypass::mycompany::myuser")
occurs in non git ignored sources, the build will fail.

This prevents private information being pushed to a public repo.

- Set `$blacklisted_words` e.g. via `$(pass show my/sensitive_words)` in an environ file, sourced at
local builds.
- The build will fail if such words occur in your docs
- Example: This repo's :srcref:environ:blacklisted file.


This is run after config is read and scans all docs folder content, not just the .md
files.

Requires the rg ([ripgrep](https://github.com/BurntSushi/ripgrep)) tool.

