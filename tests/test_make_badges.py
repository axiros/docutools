"""Tests for the `make_badges` plugin."""
import pytest

import lcdoc.call_flow_logging as cfl
from lcdoc.auto_docs import mod_doc

# from lcdoc.py_test.auto_docs import gen_mod_doc, wrap_funcs_for_call_flow_docs
from devapp.tools import project, exists, read_file, write_file
import shutil, json, os
from lcdoc.plugins.doc_lcdoc import make_badges

# just for reference, the unwrapped original:
# orig_gen_markdown = make_badges.gen_markdown
# first_test_was_run = []
import time

now = time.time


def test_document_make_badges(capsys):
    fn = mod_doc(make_badges, dest='auto')

    @cfl.document(trace=make_badges, dest=fn)
    def run_make_badges():
        return make_badges.main(argv=['pytest'])

    # run_make_badges()
    # run the use case:
    with pytest.raises(SystemExit):
        # call it w/o flags
        run_make_badges()
    captured = capsys.readouterr()
    # verify that the plugin actually worked and produced badges on stdout:
    assert 'pipeline.svg' in captured.out
    assert 'package.svg' in captured.out


def xest_run_make_badges_gen_call_flow(capsys, get_fn_uml=None):
    """
    Run the make_badges, generating a call graph
    
    Arguments:
        capsys: Pytest fixture to capture output.
    """
    first_test_was_run.append(1)  # see second
    # the directory we'll build the callflow for this test:
    d_flow = project.root()
    d_flow += '/build/autodocs/tests/'
    d_flow += 'test_make_badges__test_run_make_badges_gen_call_flow'
    # convenience:
    d = lambda fn: d_flow + '/' + fn

    if get_fn_uml:
        return d('call_seq.plantuml')

    # clear it, we'll check existance of files after the run:
    shutil.rmtree(d_flow, ignore_errors=True)

    # have all functions of this module wrapped into the flow logging mechanics:
    wrap_funcs_for_call_flow_docs(make_badges)

    # run the use case:
    with pytest.raises(SystemExit):
        # call it w/o flags
        make_badges.main(argv=['pytest'])
    captured = capsys.readouterr()

    # verify that the plugin actually worked and produced badges on stdout:
    assert 'pipeline.svg' in captured.out
    assert 'package.svg' in captured.out

    # verify the call_flow files had been written as expected:

    # the module source code, will be displayed in the viewer:
    assert exists(d('lcdoc.plugins.make_badges.module.py'))

    # first function invocation, logged with input/response args:
    assert exists(d('1.json'))
    # the actual sequence diag - to be converted to svg in doc pre_process:
    # assert exists(d('call_seq.plantuml'))
    # functions with line numbers and their source (not necessarily in the logged module)
    assert len([f for f in os.listdir(d_flow) if f.endswith('.func.py')]) > 5

    """Important:
    We cannnot (yet) assert on the presence of the uml diagram, since this pytest
    here itself is wrapped as well - not in the call flow logger but within a test func
    autodoc, where the call flow is presented.

    And the call flow graph itself is created AFTER the pytest func is finished, i.e.
    not yet!

    => We let the second test ask us for the filename, via get_fn_uml

    """

    # verify spec of one file
    j = [json.loads(s) for s in read_file(d('1.json')).splitlines()]
    assert 'func' in j[0]
    assert 'mapped' in j[0]['input']
    assert 'line' in j[0]
    assert j[0]['name'] in 'main'

    # second line is repsonse. use case raised exit(0), which we captured as well:
    assert 'SystemExit' in j[1]

    # duration is 3rd line:
    assert float(j[2]) < 0.5

    # the module is still wrapped, we'll unwrap after this pytest:
    assert make_badges.gen_markdown != orig_gen_markdown