# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/chartist/__init__.py,t=chartist

Creates [chartist.js](https://gionkunz.github.io/chartist-js/) graphs.


You may use declarative python (use keyword `python` as param before "lp"):

!!! success "Python Format"
    ```python lp mode=chartist addsrc eval=always
    import string

    labels = [i for i in string.ascii_letters[:4]]
    data = {
      'labels': labels,
      'series': [
        [ 2, 4, 2, 5]
      ]
    }
    #options = {'width': 600, 'height': 200}
    type = 'Line'

    ```

!!! success "Javascript Format"
    ```javascript lp mode=chartist addsrc aspect=4:5 eval=always
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

`lp:lightbox`



