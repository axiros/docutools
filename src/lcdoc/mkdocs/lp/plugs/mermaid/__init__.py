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
page_assets = {
    'footer': read_file(fn),
    'header': {'script': 'https://unpkg.com/mermaid@8.12.1/dist/mermaid.min.js'},
}


def run(cmd, kw):
    h = html.escape(cmd)
    h = M % h
    return {'res': h, 'formatted': True}
