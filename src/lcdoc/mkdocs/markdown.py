from lcdoc.tools import exists, read_file, write_file, hostname, time, os, sys, app

auto_gen_cmt = '''
<!-- AUTOMATICALLY GENERATED FILE - DO NOT DIRECTLY EDIT!

Direct edits will be gone after next CI build.
By: %s@%s (%s)
Command Line:

    %s
-->
'''


def mark_auto_created(fn):

    if exists(fn):
        s = read_file(fn)
    else:
        s = fn
    h = auto_gen_cmt % (
        os.environ.get('USER'),
        hostname(),
        time.ctime(),
        ' '.join(sys.argv).replace(' -', ' \\\n     -'),
    )
    s = h.lstrip() + '\n' + s
    if exists(fn):
        write_file(fn, s)
    app.info('Marked content as autocreated')
    return s


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


indent = lambda s: ('\n' + s).replace('\n', '\n    ')[1:]


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
