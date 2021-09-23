# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/flowchart/__init__.py,t=flowchart

Enables [flowchart.js](http://flowchart.js.org/)

## Syntax

```js lp:flowchart addsrc="Example 1"
st=>start: Improve your l10n process!
e=>end: Continue to have fun!:>https://youtu.be/YQryHo1iHb8[blank]
op1=>operation: Go to locize.com:>https://locize.com[blank]
sub1=>subroutine: Read the awesomeness
cond(align-next=no)=>condition: Interested to getting started?
io=>inputoutput: Register:>https://www.locize.app/register[blank]
sub2=>subroutine: Read about improving your localization workflow or another source:>https://medium.com/@adrai/8-signs-you-should-improve-your-localization-process-3dc075d53998[blank]
op2=>operation: Login:>https://www.locize.app/login[blank]
cond2=>condition: valid password?
cond3=>condition: reset password?
op3=>operation: send email
sub3=>subroutine: Create a demo project
sub4=>subroutine: Start your real project
io2=>inputoutput: Subscribe

st->op1->sub1->cond
cond(yes)->io->op2->cond2
cond2(no)->cond3
cond3(no,bottom)->op2
cond3(yes)->op3
op3(right)->op2
cond2(yes)->sub3
sub3->sub4->io2->e
cond(no)->sub2(right)->op1

st@>op1({"stroke":"Red"})@>sub1({"stroke":"Yellow"})@>cond({"stroke":"Red"})@>io({"stroke":"Red"})@>op2({"stroke":"Red"})@>cond2({"stroke":"Red"})@>sub3({"stroke":"Red"})@>sub4({"stroke":"Red"})@>io2({"stroke":"Red"})@>e({"stroke":"Red","stroke-width":6,"arrow-end":"classic-wide-long"})

```

### With Mode Piping

We create a python session where we set opts:

```python lp:python session=myflowchart addsrc="Define options once in python..."
opts = {
  'x': 0,
  'y': 0,
  'line-width': 3,
  'line-length': 50,
  'text-margin': 10,
  'font-size': 14,
  'font-color': 'black',
  'line-color': 'black',
  'element-color': 'black',
  'fill': 'white',
  'yes-text': 'yes',
  'no-text': 'no',
  'arrow-end': 'block',
  'scale': 1,
  # style symbol types
  'symbols': {
    'start': {
      'font-color': 'red',
      'element-color': 'green',
      'fill': 'yellow'
    },
    'end':{
      'class': 'end-element'
    }
  },
  # even flowstate support ;-)
  'flowstate' : {
    'past' : { 'fill' : '#CCCCCC', 'font-size' : 12},
    'current' : {'fill' : 'yellow', 'font-color' : 'red', 'font-weight' : 'bold'},
    'future' : { 'fill' : '#FFFF99'},
    'request' : { 'fill' : 'blue'},
    'invalid': {'fill' : '#444444'},
    'approved' : { 'fill' : '#58C4A3', 'font-size' : 12, 'yes-text' : 'APPROVED', 'no-text' : 'n/a' },
    'rejected' : { 'fill' : '#C45879', 'font-size' : 12, 'yes-text' : 'n/a', 'no-text' : 'REJECTED' }
  }
}
print('A ton of options defined within session: %(session_name)s' % ctx)
```


We use the experimental 'mode piping' feature, forwarding the conventional "result" into the next plugin, flowchart:

```python lp:python|flowchart session=myflowchart addsrc="..then re-use later with piping"
code = '''
st=>start: Start|past:>http://www.google.com[blank]
e=>end: Ende|future:>http://www.google.com
op1=>operation: My Operation|past
op2=>operation: Stuff|current
sub1=>subroutine: My Subroutine|invalid
cond=>condition: Yes 
or No?|approved:>http://www.google.com
c2=>condition: Good idea|rejected
io=>inputoutput: catch something...|future

st->op1(right)->cond
cond(yes, right)->c2
cond(no)->sub1(left)->op1
c2(yes)->io->e
c2(no)->op2->e
'''

result = dict(opts=opts, code=code)
```
