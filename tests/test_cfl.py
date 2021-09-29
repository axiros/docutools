import lcdoc.call_flows.call_flow_logging as cfl
from lcdoc.tools import dirname as d, os
from lcdoc.tools import project

project.root({'docs_dir': d(d(__file__)) + '/docs'})
assert 'tests' in os.listdir(project.root())


def say_hello(name):
    print('hi ', name)
    return ['greeted', name]


def test_one():
    @cfl.document(
        trace=say_hello, dest=project.root() + '/build/autodocs/call_flow_log.md'
    )
    def runit():
        res = say_hello('joe')

    runit()
