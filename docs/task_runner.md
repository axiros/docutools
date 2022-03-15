#  Task Runner

You may want to use the same task runner within your project than we do.

A task runner automates common developer jobs, like starting tests, preparing and running docu,
building, releasing (...).

docutools ships with its own taskrunner, which is described below.

!!! note

    If you do *not* intend to use docutools' taskrunner and to not plan to develop on docutools
    itself, you may safely skip this chapter.


## File Organization

The task runner's correct functioning is dependent on the presence of the following files and
directories:


```yaml
# Generic (project independent) set of functions for common dev tasks
# Parametrized by environ and environ.personal files:
- make
# holds basic project variables, e.g. project name.
# Must be sourced before any action. Sources make, activates venv when present
- environ 
# optional typically git-ignored file for personal / secret settings.
# sourced by make when present:
- environ.personal 
- mkdocs.yml # mkdocs material config (for make docs)
# Parametrizes tools like poetry or pyright. 
# Holds declared project dependencies:
- pyproject.toml 
- poetry.lock # Created by poetry install/update. Holds fixed dependencies.
- scripts/   # directory with helper scripts, used by make (e.g. conda related) and optional hooks
- config/   # directory with parametrization for coverage and pytest
- tests/   # directory for tests
- docs/   # directory for documentation
    - index.md
    - "..."
    - mdreplace.py # parametrizes the docutools markdown replace feature
```

The virtual environments created are by default outside of the project directory, by default under a
[miniconda base environment][mb] in users' `$HOME`.

[mb]: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html 


## Discussion

- The task runner is a collection of [shell functions][sf] for common developer duties, within a
  sourceable generic file: :srcref:fn=make and optional project specific hooks
- The file is generic and can be taken from the [docutools
  repo](https://github.com/axiros/docutools/blob/master/make).
- The file is parametrized through a set of variables, within this file: :srcref:fn=environ
- Additionally, make sources a (typically git-ignored) file, `environ.personal` when present - for
  personal settings (e.g. credentials) which you don't want to keep within your repo.
- docutools' task runner is based on [shell functions][sf] from within the `make` file and optional
  hooks
- For virtual environment related tasks it currently supports only [conda](./conda.md)
- The taskrunner uses [conda][cond] because we use quite a lot of tooling outside of python. See
  [here](./conda.md), regarding rationale.
- See the section about hooks below, regarding how to modify that, e.g. in favor of venvs

[sf]: [https://www.gnu.org/software/bash/manual/html_node/Shell-Functions.html]


### Alternatives   

- A pure python alternative would be e.g. [duty](https://github.com/pawamoy/duty).
- Or use a plain Makefile.



## Usage

Before using any function of `make`, the environ file must be sourced, so that the basic
project parameters are known.

!!! tip "Automatic activation on cd"

    For convenience we recommend to source the `environ` file on `cd`, within a shell function in
    your `.zshrc` or `.bashrc`. So you can simply `cd` into the dir and have all ready.

    ```bash
    # within your .bashrc / .zshrc:
    function cd {
        builtin cd "$@"
        test -f 'environ'  && source environ
    }
    ```


The environ file sources make and activates the virtual (conda) environment - if already created.

Then all functions are available:

```bash lp fmt=xt_flat
( source environ && make )
```

!!! tip

    You might add your own functions directly within `make` (not recommended) or (better) provide
    them via `environ.personal` if you want to stay update-able with our version of `make`.


You can run the functions now, via `make <function name>`.


## Hooks

You may provide project specific hooks for each function run but also for the commands within them -
when they are called via the `sh` function.

Conventional hook file name is `scripts/<func/cmdname>_<pre|post>.sh`, e.g.

- `scripts/poetry_pre.sh`
- `scripts/tests_post.sh`.

Here is an example hook file:

```bash
~/repos/mypackage/scripts master ⇡6 ❯ cat poetry_pre.sh                                                                                                                                        lc-python_py3.8
#!/usr/bin/env bash

publish_to_internal_artifactory() {
    poetry publish -r axup -u "$(pass show AX/artifactory_user)" -p "$(pass show AX/artifactory_password)" || return 1
    # this will cause the main command (poetry publish) to be skipped:
    return $skip_func_after_hook 
}

remove_symlinked_projects() {
    # another hook for a poetry action
}

if [[ "$1" == "publish" ]]; then hookfunc="publish_to_internal_artifactory"; fi
if [[ "$1" == "build" ]]; then hookfunc="remove_symlinked_projects"; fi
```

- From the example you can see that in a "pre-hook" you can replace the actual function, via a
  return code
- All variables are visible throughout all hooks, since the hooks are sourced, then `$hookfunc` is
  run, when set. I.e. you may set a variable in a pre hook and access it within the post hook.


[cond]: https://docs.conda.io/en/latest/miniconda.html


