# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/call_flow_logging.py,t=Callflow Logging

Function calling sequence as a plantuml sequence diagram


```python lp:python cfl eval=always addsrc

import json
def say_hello(n):
    print(n)
    return {'name': n}

def test_flow():
    json.dumps({'name': 'joe'})

show('call_flow', call=test_flow, trace=json)

```


 
