import json

from lcdoc.tools import project, write_file

from lcdoc.call_flows import markdown
from lcdoc.call_flows.viz_sequence import Plant

vizs = {'plantuml': Plant}  # , 'mermaid': Mermaid}


def make_call_flow_chart(flow, d_dest, fn=None, viz_name='plantuml', ILS=None):
    """
    - flow from original ILS.call_chain (list of calls, one req, one resp)
    - reformatted for [ [{<call n>}, <input>, <output>], ...] by arrange_call_and_write_infos

    call: traced frame (frame incl. meta infos as traced)

    ILS: Reference to the call_flow_logging.ILS (all the recorded state is there)
    """
    # breakpoint()  # FIXME BREAKPOINT
    fn = 'call_seq' if fn is None else fn
    r = []
    if not flow:
        print('no flow')
        return
    r_add = r.append
    viz = vizs[viz_name]
    d_root = project.root()
    # flow.insert(
    #    0, [{'counter': 0, 'name': 'intent', 'pth': ('outside',)}, 'null', 'null']
    # )
    last_thread = [0]

    def add_thread(call, have=set(), r_add=r_add, last=last_thread):
        thread = call['thread_req']
        if thread in have:
            return
        have.add(thread)
        last[0] = thread
        r_add(viz.participant(thread, thread))

    # cc is created in biz_func_wrapped_for_call_flow_logging (typ, nr, data)
    # flow.insert(0, [{'thread_req': 't'}])
    [add_thread(c[0]) for c in flow]
    # flow.pop(0)

    def args_str_and_tooltip(c, viz=viz):
        if c == 'null':
            return '-', '(None)'
        try:
            args = json.loads(c)
        except Exception as ex:
            return c.replace('\n', ','), c
        s = ['%s:%s' % (str(k), str(v)) for k, v in args.items()]
        t = '\n'.join(s)
        s = ','.join(s)
        if not s.strip():
            return 'null', 'null'
        return s, t

    def trim(s, distance, viz=viz, chars_between_adjancent_boxes=20):
        """The displayed call args in the links - should be not too long to not
        widen the chart yet more"""
        d = (abs(distance) + 1) * chars_between_adjancent_boxes
        s = s if len(s) < d else s[: d - 2] + '..'
        # s = viz.ls.join(s.splitlines())
        for k in '{', '[', '}', ']':
            s = s.replace(k, ' ')
        return s

    def href(s, tooltip, nr, typ, viz=viz, max_tooltip_len=3000):
        """s the function name, tooltip is the params"""
        if not s:
            return ''
        # [[http://plantuml.com/start{Tooltip for message} some link]]
        s = s.replace('\n', ' ')  # text over arrows should be not multline
        # s = s.split('(', 1)[0]  # .replace('(', '_').replace(')', '_')
        t = tooltip.replace('\n', viz.ls)
        t = t[:max_tooltip_len]  # bigger? he should click then
        t = t.replace('<', ' ').replace('>', '')
        t = t.replace('{', '')
        t = t.replace('}', '')
        r = '%s.json?%s{%s} %s' % (nr, typ, t, s)
        # r = '%s.json?%s{%s} %s' % (nr, typ, 'a', s)
        # r = 'javascript:onmouseover(x=>alert("foo")){foo} foo'
        r = r.replace(']]', '\\]\\]')
        return '[[%s]]' % r

    frm = []  # last req sender, the stack of active functions
    # i = [thread_name(f[0]) for f in flow]
    # breakpoint()  # FIXME BREAKPOINT
    t0 = flow[0][0]['t0']
    tn = flow[-1][0]['t0'] + flow[-1][0].get('dt', 0)
    DT = tn - t0
    for rnd in range(-1, 6):
        j = 1 * round((DT / 10.0), rnd)
        if j != 0:
            break
    dt = j
    time_ = 0
    while flow:
        call, inp, output = flow.pop(0)
        t0 = call['t0']
        thread = call['thread_req']
        if call.get('fn_mod') == 'note':
            msg = call['name'].replace('\n', viz.ls)
            r_add('note over %s: %s' % (thread, msg))
            continue
        nr = call['counter']
        n = call['name']
        if inp:
            if t0 > time_:
                # r_add('d <-> t: %s' viz.req('d', 't', what=str(round(time_, rnd))))
                #% (last_thread[0], round(time_, rnd))
                r_add('[-[#888888]-> MainThread: %s' % round(time_, rnd))
                time_ += dt
            n_with_url = href(n, str(inp), nr, 'req')
            r_add('%s<-[#888888]-]: %s' % (thread, n_with_url))
            # r_add('note left of %s: %s' % (thread, n))
            # r_add('[-[#000033]-> %s: %s' % (thread, ''))
            r_add('activate %s' % thread)

            # if frm:
            #     nfrm = frm[-1]
            #     # breakpoint()  # FIXME BREAKPOINT
            #     # ff = call.get('from_frame')
            #     # if ff:
            #     # nfrm = particips_shorts_by_code[ff.f_code]
            #     # if '"return msg.reconfigure ? [msg, null] : [null, msg]"' in str(inp):
            #     #    breakpoint()  # FIXME BREAKPOINT
            #     s, t = args_str_and_tooltip(inp)
            #     s1 = trim(s, distance=(nfrm - n))
            #     inp = href(s1, t, nr, 'req')
            #     # add the arrow form the calling function to us, with the req params:
            #     r_add(viz.req(nfrm, n, what=inp))
            # add(viz.activate(n))
            # frm.append(n)
        else:
            r_add('deactivate %s' % thread)
            # continue
            # assert inp == None
            # # when a source produces like an observer.on_next loop, the function has
            # # an entry but never exits. Then only an arrow goes out of the func:
            # while frm[-1] != n:
            #     frm.pop()
            # frm.pop()
            # w = None if output == 'null' else output
            # if not frm:
            #     break
            # if w:
            #     s = t = w
            #     w = trim(w, distance=(n - frm[-1]))
            # else:
            #     w = 'null'
            # # add the arrow back to the calling function, with the response
            # r_add(viz.rsp(n, frm[-1], what=href(w, t, nr, 'resp') or ''))
            # # add(viz.deactivate(n))

    fn = '%s/%s/call_flow.%s' % (d_dest, fn, viz.ext)
    r = viz.wrap(r)  # e.g. @startuml, and concat to string
    write_file(fn, r)
    return fn

    # loc = S.d_root + '/build/autodocs/'
    # m = {
    #     'fn': fn.split(dirname(S.fn_doc), 1)[1].rsplit('.', 1)[0],
    #     'loc': len(ILS.d_doc.split(loc, 1)[1].split('/')) * '../',
    # }
    # if viz == Plant:
    #     # v = '[![](.%(fn)s.svg)](%(loc)scall_sequence.html?src=%(fn)s)' % m
    #     v = '[![](.%(fn)s.svg)](?src=%(fn)s&sequence_details=true)' % m
    #     v = T.closed_admon('Call Sequence', v, 'note')
    # elif viz == Mermaid:
    #     v = '{!%(fn)s.plantuml!}' % m
    # add_doc('\n%s\n' % v)
