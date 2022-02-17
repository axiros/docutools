# Development Installation

When you want to use docutools within your project, in order to generate documentation for it:

- Add `docutools = "^<version>"` as a development dependency, e.g. within a
  :srcref:fn=pyproject.toml file.
- Set required :srcref:fn=environ,t=environment variables
- Adapt your `mkdocs.yml` file for the plugins you want to use. We do not interfere with any custom
  css or js

## Using `docutools` Task Runner

A task runner automates common developer jobs. You may want to use the same task runner within your project than we do.

docutools' task runner is based on shell functions and currently supports only [conda][cond] for
virtual environment related tasks.

!!! hint "Alternatives"
   
    - A pure python alternative would be e.g. [duty](https://github.com/pawamoy/duty).
    - Or use a plain Makefile.


### Usage

- The task runner is a collection of shell functions for common developer duties, within a sourceable file: :srcref:fn=make
- The file is generic and can be taken from the [docutools repo](https://github.com/axiros/docutools/blob/master/make).
- The file is parametrized through a set of variables, within this file :srcref:fn=environ
- Additionally, make sources a typcially git-ignored file, `environ.personal` - for personal
  settings you don't want to keep within your repo.

!!! tip "environ file"

    I source the `environ` file on `cd` (if not yet sourced) within a shell function in my .zshrc. It

The environ file sources make and activates the virtual (conda) environment.

Then all functions are available:

```bash lp fmt=xt_flat
( source environ && make )
```

!!! tip

    You might add your own functions directly within `make` or provide them via `environ.personal` if
    you want to stay update-able with our version of `make`.


You can run the functions now, via `make <function name>`.


### Hooks

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


