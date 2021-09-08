{'0874ef6d8f99dc60d87870379d57c91d': [{'cmd': {'cmd': 'n=foo', 'timeout': 1},
                                       'res': '$ n=foo'},
                                      {'cmd': 'echo $n',
                                       'res': '$ echo $n     \nfoo'}],
 '089b6ce02251129dcab4728e456ca358': [{'cmd': {'cmd': 'env | grep LP_'},
                                       'res': '$ env | grep '
                                              'LP_                                      \n'
                                              '\x1b[1m\x1b[31mLP_\x1b[0m\x1b[39m\x1b[49mDOCU_FILE=/home/gk/repos/docutools/docs/features/lp/literate_programming.md  \n'
                                              '\x1b[1m\x1b[31mLP_\x1b[0m\x1b[39m\x1b[49mDOCU=/home/gk/repos/docutools/docs/features/lp'},
                                      {'cmd': {'cmd': 'env | grep TMUX'},
                                       'res': '$ env | grep '
                                              'TMUX                                     \n'
                                              '\x1b[1m\x1b[31mTMUX\x1b[0m\x1b[39m\x1b[49m=/tmp/tmux-1000/default,1113980,1005                                        \n'
                                              '\x1b[1m\x1b[31mTMUX\x1b[0m\x1b[39m\x1b[49m_PANE=%1005'}],
 '0964896250ff3d7abddbce782c5ab145': [{'cmd': 'env | grep LP_',
                                       'res': '$ env | grep LP_\n'
                                              'LP_DOCU_FILE=/home/gk/repos/docutools/docs/features/lp/literate_programming.md\n'
                                              'LP_DOCU=/home/gk/repos/docutools/docs/features/lp'}],
 '153865a47f92a67d742bdbae8bf93f73': [{'cmd': {'cmd': 'ls -lta /'},
                                       'res': '$ ls -lta /   \n'
                                              'total 20            \n'
                                              'drwxrwxrwt. 222 root root 4920 '
                                              'Sep  8 13:56 '
                                              '\x1b[30m\x1b[42mtmp\x1b[39m\x1b[49m                                 \n'
                                              'drwxr-xr-x.  53 root root 1480 '
                                              'Sep  8 09:40 '
                                              '\x1b[1m\x1b[34mrun\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'dr-xr-x---.   1 root root  348 '
                                              'Sep  7 11:04 '
                                              '\x1b[1m\x1b[34mroot\x1b[0m\x1b[39m\x1b[49m                                \n'
                                              'drwxr-xr-x.   1 root root 5190 '
                                              'Sep  7 00:21 '
                                              '\x1b[1m\x1b[34metc\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'drwxr-xr-x.  21 root root 4580 '
                                              'Sep  2 12:14 '
                                              '\x1b[1m\x1b[34mdev\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'drwxr-xr-x.   1 root root  194 '
                                              'Sep  1 19:33 '
                                              '\x1b[1m\x1b[34mvar\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'dr-xr-xr-x.  13 root root    0 '
                                              'Sep  1 19:33 '
                                              '\x1b[1m\x1b[34msys\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'dr-xr-xr-x. 483 root root    0 '
                                              'Sep  1 19:33 '
                                              '\x1b[1m\x1b[34mproc\x1b[0m\x1b[39m\x1b[49m                                \n'
                                              'drwxr-xr-x.   1 root root  132 '
                                              'Sep  1 12:57 '
                                              '\x1b[1m\x1b[34musr\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'dr-xr-xr-x.   1 root root  160 '
                                              'Aug 22 19:30 '
                                              '\x1b[1m\x1b[34m.\x1b[0m\x1b[39m\x1b[49m                                   \n'
                                              'dr-xr-xr-x.   1 root root  160 '
                                              'Aug 22 19:30 '
                                              '\x1b[1m\x1b[34m..\x1b[0m\x1b[39m\x1b[49m                                  \n'
                                              'drwxr-xr-x.   1 root root   56 '
                                              'Aug 17 12:58 '
                                              '\x1b[1m\x1b[34mopt\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'dr-xr-xr-x.   7 root root 4096 '
                                              'Aug 11 18:17 '
                                              '\x1b[1m\x1b[34mboot\x1b[0m\x1b[39m\x1b[49m                                \n'
                                              'drwxr-xr-x.   1 root root    0 '
                                              'Jun 19 11:02 '
                                              '\x1b[1m\x1b[34mswap\x1b[0m\x1b[39m\x1b[49m                                \n'
                                              'drwxr-xr-x.   1 root root    8 '
                                              'Jun 13 23:41 '
                                              '\x1b[1m\x1b[34mhome\x1b[0m\x1b[39m\x1b[49m                                \n'
                                              'drwxr-xr-x.   1 root root   14 '
                                              'Jun 13 15:53 '
                                              '\x1b[1m\x1b[34mmnt\x1b[0m\x1b[39m\x1b[49m                                 \n'
                                              'drwx------.   1 root root    0 '
                                              'Apr 23 12:53 '
                                              '\x1b[1m\x1b[34mlost+found\x1b[0m\x1b[39m\x1b[49m                          \n'
                                              'lrwxrwxrwx.   1 root root    7 '
                                              'Jan 26  2021 '
                                              '\x1b[1m\x1b[36mbin\x1b[0m\x1b[39m\x1b[49m '
                                              '-> '
                                              '\x1b[1m\x1b[34musr/bin\x1b[0m\x1b[39m\x1b[49m                      \n'
                                              'lrwxrwxrwx.   1 root root    7 '
                                              'Jan 26  2021 '
                                              '\x1b[1m\x1b[36mlib\x1b[0m\x1b[39m\x1b[49m '
                                              '-> '
                                              '\x1b[1m\x1b[34musr/lib\x1b[0m\x1b[39m\x1b[49m                      \n'
                                              'lrwxrwxrwx.   1 root root    9 '
                                              'Jan 26  2021 '
                                              '\x1b[1m\x1b[36mlib64\x1b[0m\x1b[39m\x1b[49m '
                                              '-> '
                                              '\x1b[1m\x1b[34musr/lib64\x1b[0m\x1b[39m\x1b[49m                  \n'
                                              'drwxr-xr-x.   1 root root    0 '
                                              'Jan 26  2021 '
                                              '\x1b[1m\x1b[34mmedia\x1b[0m\x1b[39m\x1b[49m                               \n'
                                              'lrwxrwxrwx.   1 root root    8 '
                                              'Jan 26  2021 '
                                              '\x1b[1m\x1b[36msbin\x1b[0m\x1b[39m\x1b[49m '
                                              '-> '
                                              '\x1b[1m\x1b[34musr/sbin\x1b[0m\x1b[39m\x1b[49m                    \n'
                                              'drwxr-xr-x.   1 root root    0 '
                                              'Jan 26  2021 '
                                              '\x1b[1m\x1b[34msrv\x1b[0m\x1b[39m\x1b[49m'}],
 '2e94e71dab36182e3927504dd28bc48e': [{'cmd': 'ls -lta --color=always /etc | '
                                              'head -n 15; echo -e "With '
                                              '\\x1b[1;38;5;124mAnsi Colors"',
                                       'res': '$ ls -lta --color=always /etc | '
                                              'head -n 15; echo -e "With '
                                              '\\x1b[1;38;5;124mAnsi Colors"\n'
                                              'total 1540\n'
                                              '-rw-r--r--. 1 root root       '
                                              '206 Sep  7 00:22 hosts\n'
                                              'drwxr-xr-x. 1 root root      '
                                              '5190 Sep  7 00:21 '
                                              '\x1b[0m\x1b[01;34m.\x1b[0m\n'
                                              '-rw-r--r--. 1 root root        '
                                              '97 Sep  7 00:17 doas.conf\n'
                                              '-rw-r--r--. 1 root root     '
                                              '73748 Sep  7 00:13 ld.so.cache\n'
                                              'drwxr-xr-x. 1 root root       '
                                              '626 Sep  7 00:13 '
                                              '\x1b[01;34mpam.d\x1b[0m\n'
                                              'drwxr-xr-x. 1 root root       '
                                              '480 Sep  4 10:36 '
                                              '\x1b[01;34msysconfig\x1b[0m\n'
                                              'drwxr-xr-x. 1 root root        '
                                              '60 Sep  1 19:33 '
                                              '\x1b[01;34mudev\x1b[0m\n'
                                              'drwxr-xr-x. 1 root root        '
                                              '24 Sep  1 12:57 '
                                              '\x1b[01;34mavrdude\x1b[0m\n'
                                              '-rw-r--r--. 1 root root       '
                                              '208 Sep  1 12:57 .updated\n'
                                              'drwxr-xr-x. 1 root root       '
                                              '132 Aug 22 19:34 '
                                              '\x1b[01;34mdnf\x1b[0m\n'
                                              'dr-xr-xr-x. 1 root root       '
                                              '160 Aug 22 19:30 '
                                              '\x1b[01;34m..\x1b[0m\n'
                                              '-rw-r--r--. 1 root root       '
                                              '706 Aug 22 19:13 '
                                              'timeshift.json\n'
                                              'drwxr-xr-x. 1 root root      '
                                              '1672 Aug 19 13:59 '
                                              '\x1b[01;34malternatives\x1b[0m\n'
                                              'drwxr-xr-x. 1 root root       '
                                              '674 Aug 17 13:08 '
                                              '\x1b[01;34mprofile.d\x1b[0m\n'
                                              'With \x1b[1;38;5;124mAnsi '
                                              'Colors'}],
 '2ffda9d45e11c3f8b26224068a478a93': [{'cmd': {'cmd': 'echo $0',
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
                                              'TMUX=/tmp/tmux-1000/default,1113980,1001 '
                                              'TMUX_PANE=%1001 '
                                              'BASH_FUNC_say_hello%%=() { echo '
                                              '-e "Hello, '
                                              'from                \n'
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
 '5b3a5d518bdcd02388bfc13978a6359e': [{'cmd': {'cmd': 'echo foo'},
                                       'res': '$ echo foo    \nfoo'},
                                      {'cmd': {'cmd': 'echo bar'},
                                       'res': '$ echo bar    \nbar'}],
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
 '8e80020c01376a9d42201274dc3c3e40': [{'cmd': {'cmd': 'name=Joe;echo $name'},
                                       'res': '$ name=Joe;echo '
                                              '$name                                 \n'
                                              'Joe'}],
 'cc5af469c146f34c56e1f981cfda710a': [{'cmd': {'cmd': 'echo "Hi $name"'},
                                       'res': '$ echo "Hi '
                                              '$name"                                     \n'
                                              'Hi Joe'}],
 'ed9d4f5a23d0c4cecb298af92221a6a2': [{'cmd': 'ls -lta /etc | grep hosts',
                                       'res': '$ ls -lta /etc | grep hosts\n'
                                              '-rw-r--r--. 1 root root       '
                                              '206 Sep  7 00:22 hosts'},
                                      {'cmd': 'echo "Hello World!"      ',
                                       'res': '$ echo "Hello World!"      \n'
                                              'Hello World!'}],
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