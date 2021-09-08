{'2a92bc680d958a454e1e75f05e6b7503': {'formatted': '\n'
                                                   '=== "Code"\n'
                                                   '    ```python\n'
                                                   '    def '
                                                   'configure_tmux_base_index_1(session_name):\n'
                                                   '        """\n'
                                                   '        Seems everybody '
                                                   'really using it has 1 (on '
                                                   'normal keyboards 0 is far '
                                                   'away)\n'
                                                   '        and its a hard to '
                                                   'detect or change, '
                                                   'especially when the messed '
                                                   'with it outside of\n'
                                                   '        our control. \n'
                                                   '    \n'
                                                   '        On clean systems '
                                                   'it will be just missing '
                                                   'or: the user / runner does '
                                                   'not care.\n'
                                                   '    \n'
                                                   '        => Lets create it '
                                                   '- when it is NOT present, '
                                                   'so that we can have '
                                                   'automatic CI/CD.\n'
                                                   '        While for a normal '
                                                   'user (who is using it) we '
                                                   'fail if not configured '
                                                   'correctly.\n'
                                                   '        """\n'
                                                   '        fn = '
                                                   "env.get('HOME', '') + "
                                                   "'/.tmux.conf'\n"
                                                   '        if exists(fn):\n'
                                                   '            return\n'
                                                   '    \n'
                                                   '        '
                                                   "lp.app.warning('!!! "
                                                   'Writing %s to set base '
                                                   "index to 1 !!' % fn)\n"
                                                   '        r = [\n'
                                                   "            'set-option -g "
                                                   "base-index 1',\n"
                                                   '            '
                                                   "'set-window-option -g "
                                                   "pane-base-index 1',\n"
                                                   "            '',\n"
                                                   '        ]\n'
                                                   '        write_file(fn, '
                                                   "'\\n'.join(r))\n"
                                                   "        lp.sprun('tmux "
                                                   'source-file "%s"\' % fn)\n'
                                                   '        wait(0.5)\n'
                                                   '        '
                                                   'tmux_kill_session(session_name)\n'
                                                   '        wait(0.5)\n'
                                                   '        '
                                                   'tmux_start(session_name)\n'
                                                   '        wait(0.5)\n'
                                                   '    \n'
                                                   '    \n'
                                                   '    ```\n'
                                                   '=== '
                                                   '"[:fontawesome-brands-git-alt:](https://github.com/AXGKl/docutools/blob/master/src/lcdoc/lp_session.py#L60)"\n'
                                                   '    '
                                                   'https://github.com/AXGKl/docutools/blob/master/src/lcdoc/lp_session.py#L60\n',
                                      'res': 'def '
                                             'configure_tmux_base_index_1(session_name):\n'
                                             '    """\n'
                                             '    Seems everybody really using '
                                             'it has 1 (on normal keyboards 0 '
                                             'is far away)\n'
                                             '    and its a hard to detect or '
                                             'change, especially when the '
                                             'messed with it outside of\n'
                                             '    our control. \n'
                                             '\n'
                                             '    On clean systems it will be '
                                             'just missing or: the user / '
                                             'runner does not care.\n'
                                             '\n'
                                             '    => Lets create it - when it '
                                             'is NOT present, so that we can '
                                             'have automatic CI/CD.\n'
                                             '    While for a normal user (who '
                                             'is using it) we fail if not '
                                             'configured correctly.\n'
                                             '    """\n'
                                             "    fn = env.get('HOME', '') + "
                                             "'/.tmux.conf'\n"
                                             '    if exists(fn):\n'
                                             '        return\n'
                                             '\n'
                                             "    lp.app.warning('!!! Writing "
                                             "%s to set base index to 1 !!' % "
                                             'fn)\n'
                                             '    r = [\n'
                                             "        'set-option -g "
                                             "base-index 1',\n"
                                             "        'set-window-option -g "
                                             "pane-base-index 1',\n"
                                             "        '',\n"
                                             '    ]\n'
                                             '    write_file(fn, '
                                             "'\\n'.join(r))\n"
                                             "    lp.sprun('tmux source-file "
                                             '"%s"\' % fn)\n'
                                             '    wait(0.5)\n'
                                             '    '
                                             'tmux_kill_session(session_name)\n'
                                             '    wait(0.5)\n'
                                             '    tmux_start(session_name)\n'
                                             '    wait(0.5)\n'
                                             '\n'}}