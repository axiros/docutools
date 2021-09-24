import os
import shutil

from lcdoc.mkdocs.lp.plugs import python
from lcdoc.mkdocs.tools import app
from lcdoc.tools import read_file

config, page, Session = (python.config, python.page, python.Session)


def match(s, inner_kw):
    """We want to be the default for listed data - no requirement for a typ kwarg"""
    if not s or not isinstance(s, list):
        return
    c = inner_kw.get('columns')
    if c:
        if len(c) == len(s[0]):
            return True
    else:
        return is_dict_list(s)


def is_dict_list(s):
    return isinstance(s[0], dict) and isinstance(s[-1], dict)


def register(fmts):
    """registering us as renderer for show(<pyplot module>) within lp python"""
    fmts[match] = make_data_table


S = lambda: python.Session.cur
st = '''
<style>
%s
</style>
'''

# https://datatables.net/manual/tech-notes/3 (=> retrieve: true)
js = '''
<script>
function do_%(id)s () {
    let data = %(data)s
    
    $('#%(id)s_datatbl').DataTable( { data: data, columns: %(columns)s, retrieve: true } );
}
do_%(id)s()
</script>
'''

here = os.path.dirname(os.path.abspath(__file__))


def make_data_table(s, **inner_kw):
    columns = inner_kw.get('columns', ())
    if is_dict_list(s):
        if not columns:
            columns = list(s[0].keys())
        if not isinstance(columns[0], dict):
            columns = [{'data': i, 'title': i} for i in columns]
    else:
        if not isinstance(columns[0], dict):
            columns = [{'title': i} for i in columns]
    kw = python.Session.kw
    a = S()['assets'].setdefault('page_assets', {}).setdefault('datatables', {})
    a['mode'] = ['jquery', 'jquery_datatables']
    # user can disable by setting to empty - and provide his own via mkdocs
    fn_style = kw.get('fnstyle', 'jquery.dataTables.css')
    if fn_style:
        styl = st % read_file(here + '/data_table/' + fn_style)
        a['header'] = styl
    kw['data'] = s
    kw['columns'] = columns
    S()['assets']['footer'] = js % kw  # the per block js
    return '<table id="%(id)s_datatbl" class="display" width="100%%"></table>' % kw
