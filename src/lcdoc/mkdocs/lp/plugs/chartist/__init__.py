# :docs:page_assets_example
page_assets = {
    'header': [
        '//cdn.jsdelivr.net/chartist.js/latest/chartist.min.css',
        '//cdn.jsdelivr.net/chartist.js/latest/chartist.min.js',
    ]
}
# :docs:page_assets_example


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


C = '<div class="ct-chart %(aspect)s" id="%(id)s"></div>'

JSF = '''

<script >
function do_%(id)s () { %(body)s };
do_%(id)s();
</script>

'''


P2J = '''
var data = %(data)s;
var options = %(options)s;
new Chartist.%(type)s('_id_', data, options);
'''


def py_to_js(cmd):
    ml, mg = {}, {}
    exec(cmd, mg, ml)
    ml['options'] = ml.get('options', {})
    return P2J % ml


def run(cmd, kw):
    ar = kw.get('aspect', 'ct-square')
    kw['aspect'] = AR.get(ar, ar)
    div = C % kw
    lpjs = py_to_js(cmd) if kw.get('lang') == 'python' else cmd
    lpjs = lpjs.replace('_id_', '#' + kw['id'])
    lpjs = JSF % {'body': lpjs, 'id': kw['id']}
    return {'res': div, 'formatted': True, 'footer': lpjs}
