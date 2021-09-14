"""
###  `load_mermaid`

Adds mermaid support to the page.

"""
from lcdoc.tools import read_file, dirname

multi_line_to_list = False

eval = 'always'

M = '''
<pre class="mermaid"><code>%s
</code></pre>
'''
import html

js = [0]


def run(cmd, kw):
    """
    """
    m = M % html.escape(cmd)
    fn = dirname(__file__) + '/assets/mermaid'
    if not js[0]:
        T = read_file(fn)
        js[0] = T
    return {'res': m, 'formatted': m, 'add_to_page': {'mermaid': js[0]}}
