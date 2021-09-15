#  docutools

```yaml lp mode=make_badges write_readme eval=always
docs # lp: value=pagecount
gh-action # lp: action=ci
pypi
axblack

```


## [Documentation](https://axgkl.github.io/docutools/) building tools

This repo is providing a set of plugins for [mkdocs material](https://squidfunk.github.io/mkdocs-material/) compatible documentation.

It is meant to be used as a development dependency for projects.

Most notable feature: **[Literate Programming](./features/lp/)**.

> Most plugins should work in other mkdocs variants as well. No guarantees though.

Note: Some features are not yet documented.


Last modified: :ctime:
 
```javascript lp mode=chartist eval=always
var data = {
  // A labels array that can contain any sort of values
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  // Our series array that contains series objects or in this case series data arrays
  series: [
    [5, 2, 4, 2, 10]
  ]
};

// As options we currently only set a static size of 300x200 px. We can also omit this and use aspect ratio containers
// as you saw in the previous example
var optionsx = {
  width: 3000,
  height: 200
};

// Create a new line chart object where as first parameter we pass in a selector
// that is resolving to our chart container element. The Second parameter
// is the actual data object. As a third parameter we pass in our custom options.
new Chartist.Line('_id_', data); //, options);

```


 
```python lp mode=chartist eval=always
data = {
  'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  'series': [
    [5, 2, 4, 2, 10]
  ]
}

options = {
  'width': 3000,
  'height': 200
}

typ = 'Line'

```

