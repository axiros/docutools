"""
Adds mermaid support to the page.

"""
from lcdoc.tools import read_file, dirname
import html

eval = 'always'

M = '''
<pre class="mermaid"><code>%s
</code></pre>
'''

fn = dirname(__file__) + '/page.js'
add_to_page = {'md': read_file(fn)}


def run(cmd, kw):
    h = html.escape(cmd)
    h = M % h
    return {'res': h, 'formatted': h}
