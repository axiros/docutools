"""
###  `lightbox`

"""


from lcdoc.tools import app

page_assets = {
    'mode': 'raphael',
    'header': '//flowchart.js.org/flowchart-latest.js',
}


C = '''<div id="%(id)s"></div>'''
S = '''
<script>
var code = '%(body)s';
var diag = flowchart.parse(code);
diag.drawSVG('%(id)s', %(opts)s);
</script>
'''


def run(cmd, kw):
    kw['opts'] = {}
    if isinstance(cmd, dict):
        kw['opts'] = cmd.get('opts', {})
        code = cmd['code']
    else:
        code = cmd
    kw['body'] = "\\n'\n+ '".join([l for l in code.splitlines()])
    div = C % kw
    return {'res': div, 'formatted': True, 'footer': S % kw}
