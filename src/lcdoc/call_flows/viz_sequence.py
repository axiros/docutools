from functools import partial

# fmt:off
code = lambda typ, body: '''

```%s
%s
```

''' % (typ, body)

call_seq_diag = '''


[![](.%(f)s.svg)](%(l)scall_sequence.html?src=%(f)s)


'''
# fmt:on


class Viz:
    activate = lambda abbr: 'activate %s' % abbr
    deactivate = lambda abbr: 'deactivate %s' % abbr
    req = lambda frm, to, f=lambda x: x, what='': '%s ->> %s: %s' % (frm, to, f(what))
    rsp = lambda frm, to, f=lambda x: x, what='': '%s -->> %s: %s' % (frm, to, f(what))
    note_over = lambda n, what: 'note over %s: %s' % (n, what)


class Plant(Viz):
    participant = lambda abbr, title: 'participant "%s" as %s' % (title, abbr)
    ext = 'plantuml'
    wrap = lambda r: '@startuml\n%s\n@enduml' % '\n'.join(r)
    # include = lambda fn: '\n![call sequence](.%s.svg)\n' % fn.rsplit('.', 1)[0]
    include = lambda fn, loc: call_seq_diag % {'f': fn.rsplit('.', 1)[0], 'l': loc}
    ls = '\\n'


class Mermaid(Viz):
    participant = lambda abbr, title: 'participant %s as %s' % (abbr, title)
    what = lambda w='': '""' if not w else '%s' % w
    req = partial(Viz.req, f=what)
    rsp = partial(Viz.rsp, f=what)
    ext = 'mermaid'
    wrap = lambda r: code('mermaid', 'sequenceDiagram\n%s' % '\n'.join(r))
    ls = '<br>'
