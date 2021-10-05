# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/chart/__init__.py,t=chart

Enables [Chart.js](https://www.chartjs.org/)

## Syntax

```javascript lp:chart addsrc="Example 1"
labels = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
];
data = {
  labels: labels,
  datasets: [{
    label: 'My First dataset',
    backgroundColor: 'rgb(255, 99, 132)',
    borderColor: 'rgb(255, 99, 132)',
    data: [0, 10, 5, 2, 20, 30, 45],
  }]
};

config = {
  type: 'line',
  data: data,
  options: {}
};

```

Using python:

```python lp:python|chart addsrc="Example 2"
import datetime

labels = [datetime.date(1900, m+1, 1).strftime('%B') for m in range(7)]

data = {
  'labels': labels,
  'datasets': [{
    'label': 'My First Python Dataset',
    'backgroundColor': '#8bd125',
    'borderColor': '#8bd125',
    'data': [0, 10, 5, 2, 20, 30, 45],
  }]
}

result = {
  'type': 'line',
  'data': data,
  'options': {}
}
```

!!! note "Restrictions in Python"

    Example 2 is a simply delivering the stringified `result` as `config` dict into javascript.
    Means, you have no dynamic possibilities, using javascript functions.
