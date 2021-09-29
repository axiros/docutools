import lcdoc.call_flows.call_flow_logging as cfl
from lcdoc.tools import dirname as d
from lcdoc.tools import os, project, write_file

project.root({'docs_dir': d(d(__file__)) + '/docs'})
assert 'tests' in os.listdir(project.root())


def say_hello(name):
    print('hi ', name)
    return ['greeted', name]


def test_one():
    d = project.root() + '/build/autodocs/tests/'
    os.makedirs(d, exist_ok=True)
    d += '/testlog.md'
    write_file(d, '')

    @cfl.document(trace=say_hello, dest=d)
    def runit():
        res = say_hello('joe')

    runit()
