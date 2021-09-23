"""
###  `lightbox`

"""


from lcdoc.tools import app

page_assets = {'header': '//cdn.jsdelivr.net/npm/chart.js'}


C = '''<div>
<canvas id="%(id)s"></canvas>
</div>'''

S = '''
<script>
%(body)s
var myChart = new Chart(
    document.getElementById('%(id)s'),
    config
  );
</script>
'''


def run(cmd, kw):
    if isinstance(cmd, str):
        kw['body'] = cmd
    else:
        kw['body'] = 'var config = %s;' % str(cmd)
    js = S % kw
    div = C % kw
    return {'res': div, 'formatted': True, 'footer': js}
