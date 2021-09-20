# Terminal Color Support 


Normal fenced code blocks can 'only' highlight per language - but cannot "understand" terminal output and
 their [color escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code).  

Therefore during the mkdocs build we include [xtermjs](https://xtermjs.org/) and a helper script into your [assets](https://squidfunk.github.io/mkdocs-material/customization/#adding-assets), which renders the escape codes correctly within HTML.  

This is far more efficient than using [svg](https://yarnpkg.com/package/ansi-to-svg) or png formats.

??? note "Demo Script"
    ```bash lp mode=make_file fn=/tmp/colordemo.sh chmod=770 fmt=mk_console
    echo -e '<attribute background foreground>'
    echo -e "\nSpecifying the background color"
    for bg in 40 41 42 43 44 45 46 47
    do
      for att in 0 1 2 5 7 4
      do
        for fg in 30 31 32 33 34 35 36 37
        do
          # -n option is not valid here.  Instead, \c is used.
          echo -e "\x1b[${att};${bg};${fg}m<${att} ${bg} ${fg}> \x1b[0m\c"
        done
        echo -e " "
      done
      echo -e " "
    done

    echo -e '\nNot specifying the background color'
    for att in 0 1 2 5 7 4
    do
      for fg in 30 31 32 33 34 35 36 37
      do
        echo -e "\x1b[${att};${fg}m<${att} NA ${fg}> \x1b[0m\c"
      done
      echo -e " "
    done

    echo -e "\nTesting 256 colors"

    i=0
    while [ $i -lt 16 ]
    do
      j=0
      while [ $j -lt 16 ]
      do
        n=$(( i * 16 + j))
        ns=$(printf "%03d" $n)
        echo -e "\x1b[48;5;${n}m ${ns} \x1b[0m\c"
        j=$(( j + 1 ))
      done
      i=$(( i + 1))
      echo -e " "
    done

    echo -e "   *   *   *   *"
    i=0
    while [ $i -lt 16 ]
    do
      j=0
      while [ $j -lt 16 ]
      do
        n=$(( i * 16 + j))
        ns=$(printf "%03d" $n)
        echo -e "\x1b[4;38;5;${n}m ${ns} \x1b[0m\c"
        j=$(( j + 1 ))
      done
      i=$(( i + 1))
      echo -e " "
    done

    echo -e "Bye!"
    ```

```bash lp fmt=xt_flat

bash -c /tmp/colordemo.sh
```
