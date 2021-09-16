# Chartist

Creates [chartist.js](https://gionkunz.github.io/chartist-js/) graphs.


You may use declarative python (use keyword `python` as param before "lp"):

```python lp mode=chartist addsrc
data = {
  'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  'series': [
    [5, 2, 4, 2, 5]
  ]
}
#options = {'width': 600, 'height': 200}
type = 'Line'

```

You can also use javascript:

```javascript lp mode=chartist addsrc aspect=4:5
var data = {
  // A labels array that can contain any sort of values
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  // Our series array that contains series objects or in this case series data arrays
  series: [
    [5, 2, 4, 2, 5]
  ]
};

// "_id_" will be replaced with unique dynamic one:
new Chartist.Line('_id_', data, options={width: 400, height: 200});

```


