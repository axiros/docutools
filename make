# vim: ft=bash
about='
Development Shortcuts

Purpose: Makefile like automation of standard developer tasks.

KEEP THIS FILE GENERIC - INDEPENDENT of PROJECT.

Modifying Present Functionality:
- Use hooks to customize for your own project.
- Hook mechanics: See https://github.com/axiros/docutools/ documentation.

Modifying Parameters, Adding Functionality:
- Add project specific kvs to an environ file, which you source (automatically?) when entering this directory.
- Add a (git ignored) environ.personal for your personal settings. It will be sourced below as well, when present.


'

me="${BASH_SOURCE[0]:-${(%):-%x}}" # bash and zsh/ksh compliant
builtin cd "$(dirname "$me")"
here="$(pwd)"
test -e "environ.personal" && source "./environ.personal" # overwrites, git ignored

set -a
M="\x1b[1;32m"
O="\x1b[0m"
T1="\x1b[48;5;255;38;5;0m"
T2="\x1b[48;5;124;38;5;255m"
XDG_RUNTIME_DIR=/run/user/$UID # for systemd --user mode
TERMINAL="${TERMINAL:-st}"
VERSION_MAKE="1"
mkdocs_path="${mkdocs_path:-$PROJECT}"
mkdocs_port="${mkdocs_port:-8000}"
d_cover_html="${d_cover_html:-build/coverage/overall}"
fn_changelog="${fn_changelog:-docs/about/changelog.md.lp.py}"
set +a

skip_func_after_hook="42"

nfo() { test -z "$2" && echo -e "${M}$*$O" >&2 || h1 "$@"; }
h1()  { local a="$1" && shift && echo -e "$T1 $a $T2 $* $O" >&2; }
sh()  {
    hook pre "$@"
    if [[ "$?" != "$skip_func_after_hook" ]]; then call "$@"; fi
    hook post "$@"
}

hook () {
    local fn="scripts/$2_$1.sh"
    test -e "$fn" || return 0
    shift
    shift
    unset hookfunc
    source "$fn" "$@"
    test -n "$hookfunc" || return
    call "$hookfunc" "$@"
}

call () {
    nfo "$@"
    "$@" || {
        ret="$?"
        if [[ "$ret" == "$skip_func_after_hook" ]]; then return "$skip_func_after_hook"; fi
        nfo "ERR" $1
        test -n "$lc_exit_err" && exit 1
        return 1
    }
}

as_subproc () {
    # call the func within a subproc, so that we have global exit after fail of first sh called func
    ( lc_exit_err=true; sh "$@" ) || { nfo "ERR" $1; return 1; }
    return 0
}


help() {
    funcs()   { local a="func" && grep "${a}tion" ./make | grep " {" | sed -e "s/${a}tion/- /g" | sed -e 's/{//g' | sort; }
    aliases() { local a="## Function" && grep -A 30 "$a Aliases:" ./make | grep -B 30 'make()' | grep -v 'make()'; }
    local doc="
    # Repo Maintenance Functions

    ## Usage: ./make <function> [args]

    ## Functions:

    $(funcs)

    $(aliases)

    "
    doc="$(echo "$doc" | sed -e 's/^    //g')"
    echo -e "$doc\n"
}


activate_venv() {
    # must be set in environ:
    local conda_env="$(conda_root)/envs/${PROJECT}_py${pyver}"
    test -e "$conda_env" || { nfo "No $conda_env"; return 1; }
    test -z "$CONDA_SHLVL" && conda_src
    test "$CONDA_PREFIX" = "${conda_env:-x}" && return 0
    while [ -n "$CONDA_PREFIX" ]; do conda deactivate; done
    nfo 'Adding conda root env $PATH'
    export PATH="$(conda_root)/bin:$PATH"
    nfo Activating "$conda_env"
    conda activate "$conda_env"
}

set_version() {
    if [ "${versioning:-}" = "calver" ]; then
            version="$(date "+%Y.%m.%d")"
            return 0
    fi
    nfo "Say ./make release <version>"
    return 1
}

conda_root () { echo "$HOME/miniconda3"; }

conda_src () {
    source "$(conda_root)/etc/profile.d/conda.sh";
    conda config --set always_yes yes # --set changeps1 no
    conda config --add channels conda-forge
}


# ----------------------------------------------------------------------------------------- Make Functions:
function self-update {
    source scripts/self_update
    run_self_update "$@"
}

function ci-conda-root-env { # creates the root conda env if not present yet
    source scripts/conda.sh && make_conda_root_env "$@"
}

function ci-conda-py-env { # creates the venv for the project and poetry installs
    source scripts/conda.sh && make_conda_py_env "$@"
}

function ci {                # Trigger a CI Run by pushing and empty commit
    msg="ci: trigger CI (empty commit)"
    if [[ "$1" == "-a" ]]; then
        git commit -a -m "$msg"
    else
        echo ' ' >> README.md
        sh git commit README.md -m "$msg"
    fi
    sh git push
}

function clean {
    rm -f .coverage*
    for i in .mypy_cache .pytest_cache build dist pip-wheel-metadata site public
    do
        sh rm -rf "$i"
    done
}

function clean-lp-caches {
    find . -print |grep '\.lp.py'
    echo 'ok to delete all cached lp eval results? (ctrl-c otherwise)'
    read -n ok
    find . -print |grep '\.lp.py' | xargs rm -f
}

# :docs:cover_function
function combine_coverage {
    sh coverage combine
    sh coverage report --precision=2 | tee .code_coverage # comitted, want to see changes
    /bin/rm -rf "$d_cover_html"
    sh coverage html --directory="$d_cover_html" \
        --show-contexts \
        --precision=2 \
        --title="Overall Coverage"
}
# :docs:cover_function

function docs {
    #export lp_eval="${lp_eval:-always}"
    rm -f docs/autodocs # errors if present but not filled, seen as file at startup, then dir -> mkdocs err
    # executes a lot of code in lp blocks -> goes into coverage:
    sh coverage run --rcfile=config/coverage.lp.ini $CONDA_PREFIX/bin/mkdocs build "$@"
    combine_coverage # so that at mkdocs gh-deploy the docu build can copy the files
}

function docs-checklinks {
    type linkchecker || { echo "pip3 install git+https://github.com/linkchecker/linkchecker.git"; return 1; }
    # we ignore the x.json links of callflow svgs - they are rewritten in lc.js browser sided:
    linkchecker site --ignore-url '(.*).json' "$@"
}

function docs-serve {
    export lp_eval="${lp_eval:-on_page_change}"
    echo $lp_eval
    ps ax| grep mkdocs | grep serve | grep $mkdocs_port | xargs | cut -d ' ' -f1 | xargs kill 2>/dev/null
    sh mkdocs serve -a "127.0.0.1:${mkdocs_port}" "$@"
}

function tests {
    test -z "$1" && {
        rm -f .coverage.pytest*
        $CONDA_PREFIX/bin/pytest -vvxs tests -p no:randomly -c config/pytest.ini tests
        return $?
    }
    test -n "$1" && sh pytest "$@"
}

function release {

    test -z "$2" || { echo "say make release <version>"; return 1; }
    version="${1:-}"
    test -z "$version" && { set_version || return 1; }
    nfo "New Version = $version"
    sh poetry version "$version"
    sh tests
    #sh cover # cov reports created on ci
    # create a new changelog, this is committed, since on CI --depth=1:
    sh rm -f "$fn_changelog"
    lp_eval=changelog docs
    sh docs
    sh poetry build
    sh git commit -am "chore: Prepare release $version"
    sh git tag "$version"
    sh poetry publish
    sh git push --tags
}


## Function Aliases:

d()   {  make docs               "$@"  ; }
ds()  {  make docs-serve         "$@"  ; }
clc() {  make clean-lp-caches    "$@"  ; }
rel() {  make release            "$@"  ; }
t()   {  make tests              "$@"  ; }
sm()  { source ./make;   } # after changes

make() {
    test -z "$1" && {
        help
        return
    }
    local f="$1"
    type $f >/dev/null 2>/dev/null || {
        help
        return
    }
    shift
    as_subproc $f "$@"
}

test -n "$sourcing_make" && return 0
arg="${1:-xx}"
if [[ "$arg" == "-e" ]] || [[ "$arg" == "-ea" ]] ; then
    shift
    sourcing_make=true
    nfo "Sourcing ./environ"
    set -a; source ./environ; set +a
    unset sourcing_make
fi
if [[ "$arg" == "-a" ]] || [[ "$arg" == "-ea" ]]; then activate_venv; fi
[[ -d "$here/bin" ]] && [[ "$PATH" != *"$here/bin:"* ]] && PATH="$here/bin:$PATH" || true # add bin folder if present to PATH

