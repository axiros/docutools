# LP Examples

`lp:page addsrc`

```bash lp asserts=Hello fmt=xt_flat session=foo
echo "Hello World!"
```

<hr/>

```bash lp asserts=Hello fmt=xt_flat
ls -lta /etc | grep hosts # lp: asserts=hosts
echo "Hello World!"       # lp: asserts="[World and Hello] or Foo" 
```

<hr/>

Defining a function for later use:

```bash lp new_session=test
say_hello () { 
    echo -e "Hello, from \n"$(env | grep -i tmux)""; 
}
```

<hr/>

Heredoc, incl. the  previously defined function:

```bash lp session=test asserts=TMUX
echo $0 # lp: expect=bash
export -f say_hello
/bin/bash # lp: expect=
echo $0 # lp: expect=bash
say_hello
R="\x1b["; r="${R}1;31m"
echo -e "Means: We do have
> - $r Cross block sessions  ${R}0m
> - $r Blocking commands/subshells     ${R}0m
> - and...${R}4m$r Full Ansi
> "
```

You can `tmux att -t` test to inspect what is going on.

