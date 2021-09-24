"""
###  `lightbox`

"""


from lcdoc.tools import app
from lcdoc.mkdocs.tools import script, style

multi_line_to_list = True

fl = '//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight'
sl = '[data-md-color-scheme="slate"] .featherlight'
fls = style(
    '''
%(sl)s .featherlight-content { background: #2e303e; }
%(sl)s .featherlight-close-icon { background: rgba(255,255,255,.3); color: #fff; }
.featherlight .featherlight-content { min-width: 60%% !important; }
'''
)
fls = fls % {'sl': sl}

# Javascript supporting click events on the 'move next element into a lightbox':
# see https://github.com/noelboss/featherlight/issues/300
next_elmt_into_lightbox = '''
function next_elmt_into_lightbox(id, event) {
    let btn=document.getElementById(id);
    let parent = btn.parentNode;
    function flclose(event) {
        let c = this.$content[0];
        $(parent).after(c);
        $('#foob').focus();
    }
    let el = parent.nextElementSibling;
    $.featherlight({jquery: el, persist: true, beforeClose: flclose})
}
'''


h = ' .button-lightbox       { color: var(--md-default-fg-color--lighter); }'
h += '.button-lightbox:hover { color: var(--md-default-fg-color--light); }'

page_assets = {
    'mode': 'jquery',
    'header': [
        fl + '.min.js',
        fl + '.min.css',
        fl + '.gallery.min.js',
        fl + '.gallery.min.css',
        fls,
        script(next_elmt_into_lightbox),
        style(h),
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

cur_id = [0]


def wrap_next_elmt_into_lightbox():
    cur_id[0] += 1
    id = 'feather_below_%s' % cur_id[0]
    md = '''<span id="%(id)s"
             title="View in Lightbox"
             onclick="next_elmt_into_lightbox('%(id)s')"
             style="float:right">
               :octicons-repo-push-16:{ .button-lightbox }
            </span>
    '''
    md = md % {'id': id}
    return {'res': md, 'formatted': True}


def run(cmd, kw):
    if kw['mode'] == 'lightbox:':
        return wrap_next_elmt_into_lightbox()
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
