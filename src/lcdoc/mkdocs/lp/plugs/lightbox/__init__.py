"""
###  `lightbox`

"""


from lcdoc.tools import app

multi_line_to_list = True

fl = '//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight'
sl = '[data-md-color-scheme="slate"] .featherlight'
fls = '''
<style>
%(sl)s .featherlight-content { background: #2e303e; }
%(sl)s .featherlight-close-icon { background: rgba(255,255,255,.3); color: #fff; }
.featherlight .featherlight-content { min-width: 60%% !important; }

</style>
'''
fls = fls % {'sl': sl}

page_assets = {
    'mode': 'jquery',
    'footer': [
        fl + '.min.js',
        fl + '.min.css',
        fl + '.gallery.min.js',
        fl + '.gallery.min.css',
        fls,
    ],
}

fla = '''
$('.md-content %(match)s').featherlightGallery({
    nextIcon: '»',
    previousIcon: '«',
    openSpeed: 300,
    galleryFadeIn: 300,
    targetAttr: '%(target)s'
});
$('.md-content %(match)s').css('cursor', 'zoom-in');
'''

dflt = lambda: {'match': 'img', 'target': 'src'}


def run(cmd, kw):
    if not cmd:
        cmd = ''
    cmds = [cmd] if not isinstance(cmd, list) else cmd
    r = []
    for cmd in cmds:
        d = dflt()
        d.update(kw)
        if isinstance(cmd, dict):
            d.update(cmd)
        r.append(fla % d)
    p = '\n'.join(r)
    return {'res': '', 'formatted': True, 'footer': {'script': p}}
