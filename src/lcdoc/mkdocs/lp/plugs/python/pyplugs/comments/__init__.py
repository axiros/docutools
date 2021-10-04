import os
from functools import partial

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import add_post_page_func, script

config, page, Session = (python.config, python.page, python.Session)


def register(fmts):
    """registering us as renderer for show(<pyplot module>) within lp python"""
    fmts['comments'] = comments


dflts_comments = {
    # :docs:comments_defaults
    'theme': 'github-dark',  # "github-light" "github-dark" "preferred-color-scheme" "github-dark-orange" "icy-dark" "dark-blue" "photon-dark" "boxy-light"
    'issue_term': 'pathname',  # url, title, og:title (specific issue number and title not supported)
    # :docs:comments_defaults
}


T = '''<div id="utterance_comments"></div>'''
gh = 'https://github.com/'
marker = '<!--- utterance_comments -->'


def add_fetcher_script(output, page, config, js=None, **kw):
    return output.replace(marker, js)


reload_iframe = '''
var scr = document.createElement('script');
scr.setAttribute('src','https://utteranc.es/client.js');
scr.setAttribute('repo','%(repo)s');
scr.setAttribute('issue-term','%(issue_term)s');
scr.setAttribute('theme','%(theme)s');
scr.setAttribute('crossorigin','anonymous');
document.getElementById('utterance_comments').appendChild(scr);

'''
style = '''
.utterances {max-width: 100% !important}
'''
# var cmt_el = document.getElementById('comments')
# if (typeof window.comment != "undefined") {
#     cmt_el.innerHTML = window.comment
# } else {
#     function wait_loaded (shot) {
#         window.setTimeout(function() {
#             if (document.getElementsByClassName('utterances-frame').length) {
#                 if (!shot) return wait_loaded(1);
#                 window.comment = document.getElementById('comments').innerHTML
#                 return
#             }
#             console.log('waiting for utterances comments...')
#             return wait_loaded()
#         }, 1000)}
#     wait_loaded ()
# }


def comments(s, **kw):
    d = dict(dflts_comments)
    d.update(kw)
    repo = d.get('repo_url', config().get('repo_url'))
    while repo[-1] == '/':
        repo = repo[:-1]
    if not gh in repo:
        python.app.die('comments only work with github', your_mkdocs_repo_url=repo)
    d['repo'] = repo.split(gh, 1)[1]
    js = T
    a = {'footer': {'script': reload_iframe % d, 'style': style}}
    Session.cur['assets'].setdefault('page_assets', {})['comments'] = a
    add_post_page_func(python.lpkw(), partial(add_fetcher_script, js=js))
    return {'nocache': True, 'res': marker}
