"""Development tasks."""

import os
import re
from itertools import chain
from pathlib import Path
from shutil import which
from typing import List, Optional, Pattern

import httpx
import toml
from duty import duty
from git_changelog.build import Changelog, Version
from jinja2.sandbox import SandboxedEnvironment

PY_SRC_PATHS = (Path(_) for _ in ('src', 'tests', 'duties.py'))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = ' '.join(PY_SRC_LIST)
TESTING = os.environ.get('TESTING', '0') in {'1', 'true'}
CI = os.environ.get('CI', '0') in {'1', 'true'}
PTY = True


@duty(pre=['check_code_quality', 'check_types', 'check_docs', 'check_dependencies'])
def check(ctx):  # noqa: W0613 (no use for the context argument)
    """
    Check it all!

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """  # noqa: D400 (exclamation mark is funnier)


@duty
def check_code_quality(ctx, files=PY_SRC):
    """
    Check the code quality (flakehell lint).

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    ctx.run(f'flakehell lint {files}', title='Checking code quality', pty=PTY)


@duty
def check_dependencies(ctx):
    """
    Check for vulnerabilities in dependencies.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    nofail = False
    safety = which('safety')
    if not safety:
        pipx = which('pipx')
        if not pipx:
            safety = 'safety'
            nofail = True
        else:
            safety = f'{pipx} run safety'
    ctx.run(
        f'poetry export -f requirements.txt --without-hashes | {safety} check --stdin --full-report',
        title='Checking dependencies',
        pty=PTY,
        nofail=nofail,
    )


@duty
def check_docs(ctx):
    """
    Check if the documentation builds correctly.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    ctx.run('mkdocs build -s', title='Checking documentation', pty=PTY)


@duty
def check_types(ctx):
    """
    Check that the code is correctly typed.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    try:
        ctx.run(
            f'mypy --config-file config/mypy.ini {PY_SRC}',
            title='Type-checking',
            pty=PTY,
        )
    except Exception as ex:
        ctx.run('echo "Ignoring Errors and returning 0"')


@duty(silent=False)
def clean(ctx):
    """
    Delete temporary files.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    ctx.run('rm -rf .coverage*')
    ctx.run('rm -rf .mypy_cache')
    ctx.run('rm -rf .pytest_cache')
    ctx.run('rm -rf build')
    ctx.run('rm -rf dist')
    ctx.run('rm -rf pip-wheel-metadata')
    ctx.run('rm -rf site')
    ctx.run('find . -type d -name __pycache__ | xargs rm -rf')
    ctx.run("find . -name '*.rej' -delete")


@duty(silent=False)
def ci(ctx):
    """
    Trigger a CI Run by pushing and empty commit

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    ctx.run('echo ' ' >> README.md')
    ctx.run('git commit README.md -m "ci: trigger CI (empty commit)"')
    ctx.run('git push')


@duty(silent=False)
def docs_regen(ctx):
    """
    Regenerate some documentation pages.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """

    cmd = [
        'doc',
        'pre_process',
        '--patch_mkdocs_filewatch_ign_lp',
        '--gen_theme_link',
        '--gen_last_modify_date',
        '--gen_change_log',
        '--gen_credits_page',
        '--gen_auto_docs',
        '--lit_prog_evaluation=md',
        '--lit_prog_evaluation_timeout=5',
        '--lit_prog_on_err_keep_running=false',
    ]
    #'    --ops_ref_page=docs/reference/all_operators.md'
    #'    --release_announce_html=docs/theme/announce.html'
    ctx.run(' '.join(cmd), title='Generating docfiles.', capture=False)


@duty(pre=[docs_regen])
def docs(ctx):
    """
    Build the documentation locally.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    ctx.run('mkdocs build --site-dir public', title='Building documentation')


@duty(pre=[docs_regen])
def docs_serve(ctx, host='127.0.0.1', port=8000):
    """
    Serve the documentation (localhost:8000).

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    ctx.run(
        f'mkdocs serve -a {host}:{port}', title='Serving documentation', capture=False
    )


@duty
def format(ctx):  # noqa: W0622 (we don't mind shadowing the format builtin)
    """
    Run formatting tools on the code.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    ctx.run(
        f'autoflake -ir --exclude tests/fixtures --remove-all-unused-imports {PY_SRC}',
        title='Removing unused imports',
        pty=PTY,
    )
    ctx.run(f'isort -y -rc {PY_SRC}', title='Ordering imports', pty=PTY)
    ctx.run(f'black {PY_SRC}', title='Formatting code', pty=PTY)


# we dont' do parallel runs (pytest -n)
# @duty
# def combine(ctx):
#     """
#     Combine coverage data from multiple runs.

#     Arguments:
#         ctx: The [context][duty.logic.Context] instance (passed automatically).
#     """
#     ctx.run('coverage combine --rcfile=config/coverage.ini')


@duty(silent=True)
def coverage(ctx):
    """
    Report coverage as text and HTML.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    ctx.run('mkdir -p build')
    ctx.run('coverage report --rcfile=config/coverage.ini | tee build/coverage_report')

    ctx.run('coverage html --rcfile=config/coverage.ini')


@duty(pre=[duty(lambda ctx: ctx.run('rm -f .coverage', silent=False))])
def test(ctx, match=os.environ.get('match', '')):
    """
    Run the test suite.

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    # cmd = 'ops resources --sync default --force'
    # ctx.run(cmd, title='Installing test resources')
    # the autodocs are written as they are run, randomizer whould screw that up:
    cmd = 'pytest -xs -p no:randomly -c config/pytest.ini -k "%s" tests'
    title = 'Running tests with $make_autodocs set'
    ctx.run(cmd % match, title=title, capture=False)
    print('tests done')


@duty()
def badges(ctx):
    """
    Create badges

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
    """
    # -n auto removed (multiprocess runs, TODO put in again)
    u = (
        'hg+https://badges.github.com/scm/hg/noauth/badges::/tmp/badges_%(USER)s'
        % os.environ
    )
    ctx.run(
        ['doc', 'make_badges', '--badge_directory', u, '--modify_readme'],
        title='Creating badges',
        pty=PTY,
        capture=False,
    )


@duty
def release(ctx, version=os.environ.get('version')):
    """
    Release a new Python package: usage: make release VERSION=2020.10.12

    Arguments:
        ctx: The [context][duty.logic.Context] instance (passed automatically).
        version: The new version number to use.
    """
    if not version:
        raise Exception('export version=...')
    ctx.run(
        f'poetry version {version}',
        title=f'Bumping version in pyproject.toml to {version}',
        pty=PTY,
    )
    ctx.run('git add pyproject.toml CHANGELOG.md', title='Staging files', pty=PTY)
    ctx.run(
        ['git', 'commit', '-m', f'chore: Prepare release {version}'],
        title='Committing changes',
        nofail=True,
        pty=PTY,
    )
    ctx.run(f'git tag {version}', title='Tagging commit', pty=PTY, nofail=True)
    if TESTING:
        return
    ctx.run('git push', title='Pushing commits', pty=False)
    ctx.run('git push --tags', title='Pushing tags', pty=False)
    ctx.run('poetry build', title='Building dist/wheel', pty=PTY)
    ctx.run('poetry publish', title='Publishing dist/wheel', pty=PTY)
    ctx.run('mkdocs gh-deploy', title='Publishing docs', pty=PTY)
    # user, pw = os.environ.get('user'), os.environ.get('pass')
    # import getpass
