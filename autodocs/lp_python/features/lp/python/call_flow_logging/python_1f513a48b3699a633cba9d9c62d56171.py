from lcdoc.mkdocs.lp.plugs import python
print  = python.printed
show = python.show
def run_lp_flow():

    
    import json
    def say_hello(n):
        print(n)
        return json.dumps({'name': n})
    
    def test_flow():
        say_hello('joe')
    
    show('call_flow', call=test_flow, trace=json)
    