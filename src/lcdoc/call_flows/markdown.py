from inspect import getsource


class Mkdocs:
    details = '''

<details>
    <summary>%s</summary>

%s

</details>

'''
    code_ = '''

```_code_
%s
```

    '''
    admon_ = '''

!!! %s "%s"

%s 

    '''
    admon_closed_ = admon_.replace('!!!', '???')
    admon_clsabl_ = admon_.replace('!!!', '???+')
    tab_ = '''
=== "%s"

%s

    '''
    js = code_.replace('_code_', 'js')
    py = code_.replace('_code_', 'python')

    code = lambda which, body: Mkdocs.code_.replace('_code_', which) % body
    tab = lambda title, cont, t=tab_: t % (title, indent(cont))
    admon = lambda title, cont, mode='note', widg=admon_: widg % (
        mode,
        title.replace('\n', ''),
        indent(cont),
    )
    closed_admon = lambda *a, _=admon, __=admon_closed_, **kw: _(*a, widg=__, **kw)
    clsabl_admon = lambda *a, _=admon, __=admon_clsabl_, **kw: _(*a, widg=__, **kw)


def to_min_header_level(l, s):
    h = '\n'
    s = '\n' + s
    for k in range(1, l):
        h += '#'
        s = s.replace(h + ' ', ('\n' + '#' * l) + ' ')
    return s


indent = lambda s: ('\n' + s).replace('\n', '\n    ')[1:]


def header(s, level):
    return level * '#' + ' ' + s.strip()


def deindent(
    s, add_code_line_seps=False, dl=lambda l, ws: l[ws:] if l[:ws] == ' ' * ws else l
):
    # can handle first line not indentend as in docstrings starting after """ w/o line sep
    s = s or ''
    if not s.strip():
        return s
    ls = s.splitlines()
    # first line might be special after like '''def foo'''
    # if indented though we use it:
    if len(ls) == 1:
        return ls[0].strip()
    if ls[0].startswith(' ') or ls[0][:4] in ('def ', 'clas'):
        i = 0
    else:
        for i in 1, 2, 3, 4:
            if i > len(ls) - 1:
                i = i - 1
                break
            if ls[i].lstrip():
                break
    # len of indent to remove:
    ws = len(ls[i]) - len(ls[i].lstrip())
    ls = [dl(l, ws) for l in ls]
    if add_code_line_seps:
        ls = line_sep_before_code(ls)
    return '\n'.join(ls).strip()


def line_sep_before_code(ls):
    """for markdown"""
    r, is_code = [], False
    for ln in ls:
        if not is_code:
            if ln.startswith('    '):
                r.append('')
                is_code = True
        else:
            if not ln.startswith('    '):
                is_code = False
        r.append(ln)
    return r


# ----------------------------------------------------- Create markdown from whole tree
def extract_docstr_head(docstr):
    """
    Finding Docstrings

    Example: The one of this func would be 'Finding Docstrings'  
    """
    s, rest = docstr.strip(), ''
    if not s:
        return '', ''
    l = s.splitlines()
    h = len(l[0]) < 80 and (len(l) < 2 or not l[1].strip())
    if len(l[0]) < 80 and (len(l) < 2 or not l[1].strip()):
        rest = '\n'.join(l[1:]).strip()
        l0 = l[0]
        if l0.startswith('#'):
            # remove markdown:
            return l0.split(' ', 1)[1], rest
        return l0, rest
    # no docstring with header:
    return '', docstr


def obj_tree_to_markdown(obj, hir=1):
    """obj as created by auto_docs recurse_into"""
    T = Mkdocs
    r = []
    add = r.append
    if 1:
        n = obj['name']
    head, rest = extract_docstr_head(obj['doc'])
    add(header('`%s` %s' % (n, head), hir))
    add(rest)
    src = obj['source']
    src = T.code('python', src)
    add(Mkdocs.closed_admon('source', src))
    cs, fs = obj.get('classes', ()), obj.get('funcs', ())
    if cs:
        add(header('Classes', hir + 1))
        obj_tree_to_markdown(cs[0], hir + 2)
        [add(obj_tree_to_markdown(c, hir + 2)) for c in cs]
    if fs:
        add(header('Functions', hir + 1))
        [add(obj_tree_to_markdown(f, hir + 2)) for f in fs]

    return '\n'.join(r)
