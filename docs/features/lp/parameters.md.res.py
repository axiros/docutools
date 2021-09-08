{'0357c577d4a24699bbc84beb7d905955': [{'cmd': {'cmd': 'date'},
                                       'res': '$ date        \n'
                                              'Wed Sep  8 02:26:03 AM CEST '
                                              '2021'},
                                      {'cmd': {'cmd': 'tmux list-sessions | '
                                                      'grep docutest'},
                                       'res': '$ tmux list-sessions | grep '
                                              'docutest                  \n'
                                              '\x1b[1m\x1b[31mdocutest\x1b[0m\x1b[39m\x1b[49m: '
                                              '1 windows (created Wed Sep  8 '
                                              '02:26:03 2021)'}],
 '07297dea871a6e803f87d078112d9e75': [{'cmd': {'asserts': 'foobar',
                                               'cmd': 'ls foo*',
                                               'post': 'rm foobar',
                                               'pre': 'touch foobar|true'},
                                       'res': '$ ls foo*     \nfoobar'},
                                      {'cmd': 'ls foobar # lp: '
                                              'asserts="cannot"',
                                       'res': '$ ls foobar # lp: '
                                              'asserts="cannot"      \n'
                                              "ls: cannot access 'foobar': No "
                                              'such file or '
                                              'directory                           \n'
                                              '$ '}],
 '1281ac7836479f3618566a84866f0d6f': [{'cmd': 'touch /tmp/silent_test',
                                       'res': '$ touch /tmp/silent_test\n'}],
 '23824502d4f4dcd4457627823e8a6dee': [{'cmd': '', 'res': 'hosts'}],
 '409aaddd87713903b1ac8c38de36cbea': [{'cmd': {'cmd': "echo -e '$ foo'"},
                                       'res': "$ echo -e '$ "
                                              "foo'                                     \n"
                                              '$ foo'}],
 '4c1983f69f64940d425016f159689014': [],
 '553887ee29d6eb15270219a6c2ccdf16': [{'cmd': {'cmd': 'tmux list-sessions | '
                                                      'grep docutest'},
                                       'res': '$ tmux list-sessions | grep '
                                              'docutest                  \n'
                                              '\x1b[1m\x1b[31mdocutest\x1b[0m\x1b[39m\x1b[49m: '
                                              '1 windows (created Wed Sep  8 '
                                              '02:26:03 2021)'}],
 '5774d194a14bba07ab798bcbb223182e': [{'cmd': {'cmd': 'while true; do date; '
                                                      'sleep 0.05; done',
                                               'expect': False},
                                       'res': '$ while true; do date; sleep '
                                              '0.05; done \n'
                                              'Wed Sep  8 02:26:02 AM CEST '
                                              '2021        \n'
                                              'Wed Sep  8 02:26:02 AM CEST '
                                              '2021        \n'
                                              'Wed Sep  8 02:26:02 AM CEST '
                                              '2021'}],
 '610785c419013ab8a25dea3f986ccd6f': [{'cmd': 'ls  . | grep hosts',
                                       'res': '$ ls  . | grep hosts\nhosts'}],
 '71d6fd282044a55f4c3c98c3fbf3e234': [{'cmd': 'rm /tmp/silent_test || true',
                                       'res': '$ rm /tmp/silent_test || true\n'
                                              'rm: cannot remove '
                                              "'/tmp/silent_test': No such "
                                              'file or directory'}],
 '7279305bfcdd75b2e329369cd96f0dc2': [{'cmd': 'ls /',
                                       'res': '$ ls /\n'
                                              'bin\n'
                                              'boot\n'
                                              'dev\n'
                                              'etc\n'
                                              'home\n'
                                              'lib\n'
                                              'lib64\n'
                                              'lost+found\n'
                                              'media\n'
                                              'mnt\n'
                                              'opt\n'
                                              'proc\n'
                                              'root\n'
                                              'run\n'
                                              'sbin\n'
                                              'srv\n'
                                              'swap\n'
                                              'sys\n'
                                              'tmp\n'
                                              'usr\n'
                                              'var'},
                                      {'cmd': '# statement specific assertion:',
                                       'res': '$ # statement specific '
                                              'assertion:\n'},
                                      {'cmd': 'echo hi',
                                       'res': '$ echo hi\nhi'}],
 '9e663c7f148d2aace1e5e9e509e9570b': [{'cmd': 'echo Hello',
                                       'res': '$ echo Hello\nHello'}],
 '9e663c7f148d2aace1e5e9e509e9570b_': [{'cmd': 'echo Hello',
                                        'res': '$ echo Hello\nHello'}],
 '9e663c7f148d2aace1e5e9e509e9570b__': [{'cmd': 'echo Hello',
                                         'res': '$ echo Hello\nHello'}],
 'b1d4e7026cc3e8d867bb09be4c8d1c41': [{'cmd': 'ls -lta /tmp/silent_test',
                                       'res': '$ ls -lta /tmp/silent_test\n'
                                              '-rw-r--r--. 1 gk gk 0 Sep  8 '
                                              '02:26 /tmp/silent_test'}],
 'b2c9d8bcf68cf09a19e11f9bdea6d16c': [{'cmd': 'tmux list-sessions | grep test '
                                              '|| true',
                                       'res': '$ tmux list-sessions | grep '
                                              'test || true\n'
                                              'docutest: 1 windows (created '
                                              'Wed Sep  8 02:22:18 2021)\n'
                                              'dt_test: 1 windows (created Wed '
                                              'Sep  8 02:26:01 2021)\n'
                                              'test: 1 windows (created Wed '
                                              'Sep  8 02:26:01 2021)\n'
                                              'test1: 1 windows (created Tue '
                                              'Sep  7 10:57:20 2021)'}],
 'cce25dfe7ada542aa3f90a760a24b6fa': [{'cmd': {'cmd': 'ls -lt /usr/bin | head '
                                                      '-n 12'},
                                       'res': '$ ls -lt /usr/bin | head -n '
                                              '12                        \n'
                                              'total 507944        \n'
                                              '-rwxr-xr-x. 1 root root         '
                                              '42868 Aug 25 00:06 '
                                              'xdg-mime                     \n'
                                              '-rwxr-xr-x. 1 root root         '
                                              '25822 Aug 24 17:58 '
                                              'xdg-open                     \n'
                                              'lrwxrwxrwx. 1 root '
                                              'root            20 Aug 19 13:59 '
                                              'st -> /etc/alternatives/st   \n'
                                              '-rwxr-xr-x. 1 root '
                                              'root           322 Aug 10 11:01 '
                                              'skypeforlinux                \n'
                                              'lrwxrwxrwx. 1 root '
                                              'root            46 Aug 10 06:13 '
                                              'microsoft-edge-beta -> '
                                              '/opt/microsoft/msedge-beta/microsoft-edge-beta                                        \n'
                                              'lrwxrwxrwx. 1 root '
                                              'root            32 Aug  8 01:01 '
                                              'microsoft-edge -> '
                                              '/etc/alternatives/microsoft-edge                   \n'
                                              '-rwxr-xr-x. 1 root root         '
                                              '74344 Aug  6 17:56 '
                                              'bootctl                      \n'
                                              '-rwxr-xr-x. 1 root root         '
                                              '98968 Aug  6 17:56 '
                                              'busctl                       \n'
                                              '-rwxr-xr-x. 1 root root         '
                                              '57616 Aug  6 17:56 '
                                              'coredumpctl                  \n'
                                              '-rwxr-xr-x. 1 root root        '
                                              '144568 Aug  6 17:56 '
                                              'homectl                      \n'
                                              '-rwxr-xr-x. 1 root root         '
                                              '32744 Aug  6 17:56 '
                                              'hostnamectl'}],
 'dbd8547fccabcdfd0d81c250e97660a2': [{'cmd': {'cmd': 'tmux list-sessions | '
                                                      'grep kill_test'},
                                       'res': '$ tmux list-sessions | grep '
                                              'kill_test                 \n'
                                              '\x1b[1m\x1b[31mkill_test\x1b[0m\x1b[39m\x1b[49m: '
                                              '1 windows (created Wed Sep  8 '
                                              '02:26:02 2021)'},
                                      {'cmd': {'cmd': 'ls . | grep hosts'},
                                       'res': '$ ls . | grep hosts'}],
 'eaee39da022873ad5a434580e723d1f2': [{'cmd': {'asserts': 'foobar',
                                               'cmd': 'ls foo*',
                                               'pre': 'touch foobar|true'},
                                       'res': '$ ls foo*     \nfoobar'}]}