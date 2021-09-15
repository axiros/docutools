# :docs:add_to_page_example
add_to_page = {
    'header': {
        'stylesheet': '//cdn.jsdelivr.net/chartist.js/latest/chartist.min.css',
        'script': '//cdn.jsdelivr.net/chartist.js/latest/chartist.min.js',
    }
}
# :docs:add_to_page_example


C = '<div class="ct-chart %(aspect)s" id="%(id)s"></div>'

# for convenience we allow to declare aspect not only as name but also as ratio:
ar = '''
ct-square>1
ct-minor-second>15:16
ct-major-second>8:9
ct-minor-third>5:6
ct-major-third>4:5
ct-perfect-fourth>3:4
ct-perfect-fifth>2:3
ct-minor-sixth>5:8
ct-golden-section>1:1.618
ct-major-sixth>3:5
ct-minor-seventh>9:16
ct-major-seventh>8:15
ct-octave>1:2
ct-major-tenth>2:5
ct-major-eleventh>3:8
ct-major-twelfth>1:3
ct-double-octave>1:4
'''

ar = [l for l in ar.strip().splitlines()]
ar = dict([l.split('>') for l in ar])
AR = {v: k for k, v in ar.items()}

P2J = '''
var data = %(data)s;
var options = %(options)s;
new Chartist.%(typ)s('_id_', data, options);
'''


def run(cmd, kw):
    ar = kw.get('aspect', 'ct-square')
    kw['aspect'] = AR.get(ar, ar)
    kw['id'] = kw.get('id') or 'chartist-%(source_id)s' % kw['LP'].spec
    div = C % kw

    if kw.get('lang') == 'python':
        ml, mg = {}, {}
        exec(cmd, mg, ml)
        ml['options'] = ml.get('options', {})
        cmd = P2J % ml

    body = cmd.replace('_id_', '#' + kw['id'])
    body = '\n<script>\n%s</script>\n' % body
    r = '\n'.join(['', div, '', body, ''])
    return {'res': r, 'formatted': r}
