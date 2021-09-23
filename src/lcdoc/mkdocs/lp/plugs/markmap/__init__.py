# page_assets = {
#     'header': {
#         'script': [
#             'https://unpkg.com/d3@6.7.0/dist/d3.min.js',
#             'https://unpkg.com/markmap-lib@0.11.5/dist/browser/index.min.js',
#             'https://unpkg.com/markmap-view@0.2.6/dist/index.min.js',
#         ]
#     }
# }

page_assets = {
    'mode': 'd3',
    'header': [
        '//unpkg.com/markmap-lib@0.11.5/dist/browser/index.min.js',
        '//unpkg.com/markmap-view@0.2.6/dist/index.min.js',
    ],
}


R = '''
<svg id="%(id)s" style="width: %(width)s; height: %(height)s"></svg>
'''

JSF = '''

<script>
function do_%(id)s () {
    const md=`%(md)s`
    const transformer = new markmap.Transformer();
    const {root, features} = transformer.transform(md.replaceAll('X_R', '`'));
    const { styles, scripts } = transformer.getUsedAssets(features);

    if (styles) markmap.loadCSS(styles);
    if (scripts) markmap.loadJS(scripts, { getMarkmap: () => markmap });
    markmap.Markmap.create('#%(id)s' , {}, root);
}
do_%(id)s ()

</script>



'''


def run(cmd, kw):
    ctx = {
        'md': cmd.replace('`', 'X_R'),
        'id': kw['id'],
        'width': kw.get('width', '100%'),
        'height': kw.get('height', '100%'),
    }
    lpjs = JSF % ctx
    return {'res': R % ctx, 'formatted': True, 'footer': lpjs}
