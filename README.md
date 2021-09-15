#  docutools

<!-- id: 58ce0e4068dce84983a2caa8a1e87f12 -->
[![docs pages][docs pages_img]][docs pages] [![gh-ci][gh-ci_img]][gh-ci] [![pkg][pkg_img]][pkg] [![code_style][code_style_img]][code_style] 

[docs pages]: https://AXGKl.github.io/docutools
[docs pages_img]: https://AXGKl.github.io/docutools/img/badge_docs.svg
[gh-ci]: https://github.com/AXGKl/docutools/actions/workflows/ci.yml
[gh-ci_img]: https://github.com/AXGKl/docutools/actions/workflows/ci.yml/badge.svg
[pkg]: https://pypi.org/project/docutools/2021.9.14/
[pkg_img]: https://AXGKl.github.io/docutools/img/badge_pypi.svg
[code_style]: https://pypi.org/project/axblack/
[code_style_img]: https://AXGKl.github.io/docutools/img/badge_axblack.svg

<!-- id: 58ce0e4068dce84983a2caa8a1e87f12 -->


## [Documentation](https://axgkl.github.io/docutools/) building tools

This repo is providing a set of plugins for [mkdocs material](https://squidfunk.github.io/mkdocs-material/) compatible documentation.

It is meant to be used as a development dependency for projects.

Most notable feature: **[Literate Programming](./features/lp/)**.

> Most plugins should work in other mkdocs variants as well. No guarantees though.

Note: Some features are not yet documented.


Last modified: Wed, 15 Sep 2021 23h GMT
 
<!-- id: 959627b395c41fd3fc2896412d4d1e10 -->
<div class="ct-chart ct-square" id="chartist-959627b395c41fd3fc2896412d4d1e10"></div>


<script>
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
new Chartist.Line('#chartist-959627b395c41fd3fc2896412d4d1e10', data); //, options);
</script>


<!-- id: 959627b395c41fd3fc2896412d4d1e10 -->


 
<!-- id: f5a5f31cfa02f57fa182e7437b9a9245 -->
<div class="ct-chart ct-square" id="chartist-f5a5f31cfa02f57fa182e7437b9a9245"></div>


<script>

var data = {'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], 'series': [[5, 2, 4, 2, 10]]};
var options = {'width': 3000, 'height': 200};
new Chartist.Line('#chartist-f5a5f31cfa02f57fa182e7437b9a9245', data, options);
</script>


<!-- id: f5a5f31cfa02f57fa182e7437b9a9245 -->