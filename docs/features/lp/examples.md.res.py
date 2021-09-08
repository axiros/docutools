{'2ffda9d45e11c3f8b26224068a478a93': [{'cmd': {'cmd': 'echo $0',
                                               'expect': 'bash'},
                                       'res': '$ echo $0           \n'
                                              '-bash               \n'
                                              '$'},
                                      {'cmd': {'cmd': 'export -f say_hello'},
                                       'res': '$ export -f say_hello'},
                                      {'cmd': {'cmd': '/bin/sh', 'expect': ''},
                                       'res': '$ /bin/sh           \n$'},
                                      {'cmd': {'cmd': 'echo $0',
                                               'expect': '/bin/sh'},
                                       'res': '$ echo $0           \n'
                                              '/bin/sh             \n'
                                              '$'},
                                      {'cmd': {'cmd': 'say_hello'},
                                       'res': '$ say_hello   \n'
                                              'Hello, from         \n'
                                              'TMUX=/tmp/tmux-1000/default,1113980,796 '
                                              'TMUX_PANE=%796 '
                                              'BASH_FUNC_say_hello%%=() { echo '
                                              '-e "Hello, '
                                              'from                  \n'
                                              '"$(env | grep -i tmux)""'},
                                      {'cmd': {'cmd': 'R="\\x1b["; '
                                                      'r="${R}1;31m"'},
                                       'res': '$ R="\\x1b["; r="${R}1;31m"'},
                                      {'cmd': {'cmd': 'echo -e "Means: We '
                                                      'have\n'
                                                      '- $r Cross block '
                                                      'sessions  ${R}0m\n'
                                                      '- $r Blocking '
                                                      'commands     ${R}0m\n'
                                                      '- and...${R}4m$r Full '
                                                      'Ansi\n'
                                                      '"'},
                                       'res': '$ echo -e "Means: We '
                                              'have               \n'
                                              '> - $r Cross block sessions  '
                                              '${R}0m     \n'
                                              '> - $r Blocking commands     '
                                              '${R}0m     \n'
                                              '> - and...${R}4m$r Full '
                                              'Ansi            \n'
                                              '> "                 \n'
                                              'Means: We have      \n'
                                              '- \x1b[1m\x1b[31m Cross block '
                                              'sessions  '
                                              '\x1b[0m\x1b[39m\x1b[49m               \n'
                                              '- \x1b[1m\x1b[31m Blocking '
                                              'commands     '
                                              '\x1b[0m\x1b[39m\x1b[49m               \n'
                                              '- and...\x1b[1;4m\x1b[31m Full '
                                              'Ansi\x1b[0m\x1b[39m\x1b[49m  \n'
                                              '\n'
                                              '\x1b[1;4m\x1b[31m$ '
                                              '\x1b[0m\x1b[39m\x1b[49m             \n'
                                              '\x1b[1;4m\x1b[31m'}],
 '39d75b9e7c5bf77cf0917cb01421b217': [{'cmd': {'cmd': 'echo "Hello World!"'},
                                       'res': '$ echo "Hello '
                                              'World!"                                 \n'
                                              'Hello World!'}],
 '4c1983f69f64940d425016f159689014': [],
 '7228e49bc88a91fb614305530ffaafa0': [{'cmd': {'cmd': 'say_hello () { \n'
                                                      '    echo -e "Hello, '
                                                      'from \\n"$(env | grep '
                                                      '-i tmux)""; \n'
                                                      '}'},
                                       'res': '$ say_hello () {    \n'
                                              '>     echo -e "Hello, from '
                                              '\\n"$(env | grep -i '
                                              'tmux)"";                          \n'
                                              '> }                 \n'
                                              '$ '}],
 'ed9d4f5a23d0c4cecb298af92221a6a2': [{'cmd': 'ls -lta /etc | grep hosts',
                                       'res': '$ ls -lta /etc | grep hosts\n'
                                              '-rw-r--r--. 1 root root       '
                                              '206 Sep  7 00:22 hosts'},
                                      {'cmd': 'echo "Hello World!"      ',
                                       'res': '$ echo "Hello World!"      \n'
                                              'Hello World!'}]}