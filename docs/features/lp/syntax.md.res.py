{'089b6ce02251129dcab4728e456ca358': [{'cmd': {'cmd': 'env | grep LP_'},
                                       'res': '$ env | grep '
                                              'LP_                                      \n'
                                              '\x1b[1m\x1b[31mLP_\x1b[0m\x1b[39m\x1b[49mDOCU_FILE=/home/gk/repos/docutools/docs/features/lp/syntax.md                \n'
                                              '\x1b[1m\x1b[31mLP_\x1b[0m\x1b[39m\x1b[49mDOCU=/home/gk/repos/docutools/docs/features/lp'},
                                      {'cmd': {'cmd': 'env | grep TMUX'},
                                       'res': '$ env | grep '
                                              'TMUX                                     \n'
                                              '\x1b[1m\x1b[31mTMUX\x1b[0m\x1b[39m\x1b[49m=/tmp/tmux-1000/default,1113980,831 \n'
                                              '\x1b[1m\x1b[31mTMUX\x1b[0m\x1b[39m\x1b[49m_PANE=%831'}],
 '39b508d3aff3b942c186e1d4cf4df126': [{'cmd': 'env | grep LP_ # any env var '
                                              'starting with lp_ or LP_ is put '
                                              'into the session',
                                       'res': '$ env | grep LP_ # any env var '
                                              'starting with lp_ or LP_ is put '
                                              'into the session\n'
                                              'LP_DOCU_FILE=/home/gk/repos/docutools/docs/features/lp/syntax.md\n'
                                              'LP_DOCU=/home/gk/repos/docutools/docs/features/lp'}],
 '3cbd77fb09a03c298f3abb985e46adf0': [{'cmd': 'ls /notexisting || true # would '
                                              'except here without the `|| '
                                              'true`',
                                       'res': '$ ls /notexisting || true # '
                                              'would except here without the '
                                              '`|| true`\n'
                                              'ls: cannot access '
                                              "'/notexisting': No such file or "
                                              'directory'},
                                      {'cmd': 'ls /etc |grep hosts',
                                       'res': '$ ls /etc |grep hosts\nhosts'}],
 '709f98923e717df626280de087159a58': [{'cmd': 'echo "Hello ${User:-World}"',
                                       'res': '$ echo "Hello ${User:-World}"\n'
                                              'Hello World'}],
 'd9ae642b4aef5e2c541bb930216ee356': [{'cmd': 'echo "hello world"',
                                       'res': '$ echo "hello world"\n'
                                              'hello world'}],
 'ef141587432d3b777a84d336a0c7a980': [{'cmd': {'cmd': 'foo () { echo bar; }'},
                                       'res': '$ foo () { echo bar; }'},
                                      {'cmd': {'cmd': 'cat << EOF > test.pyc\n'
                                                      'foo$(foo)baz\n'
                                                      'second_line\n'
                                                      'EOF'},
                                       'res': '$ cat << EOF > '
                                              'test.pyc                 \n'
                                              '> foo$(foo)baz      \n'
                                              '> second_line       \n'
                                              '> EOF               \n'
                                              '$ '},
                                      {'cmd': {'cmd': 'cat test.pyc | sed -z '
                                                      '"s/\\n/X/g" | grep '
                                                      "'foobarbazXsecond_line'"},
                                       'res': '$ cat test.pyc | sed -z '
                                              '"s/\\n/X/g" | grep '
                                              "'foobarbazXsecond_line'         \n"
                                              '\x1b[1m\x1b[31mfoobarbazXsecond_line\x1b[0m\x1b[39m\x1b[49mX'}]}