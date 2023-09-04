# vim: ft=sh
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

VERSION_MAKE="3" # micromamaba

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
mkdocs_path="${mkdocs_path:-$PROJECT}"
mkdocs_port="${mkdocs_port:-8000}"
d_cover_html="${d_cover_html:-build/coverage/overall}"
fn_changelog="${fn_changelog:-docs/about/changelog.md.lp.py}"
PROJECT="${PROJECT:-$(basename "$here")}"
set +a

skip_func_after_hook="42"


helper_funcs () {
    function nfo { test -z "$2" && echo -e "${M}$*$O" >&2 || h1 "$@"; }
    function h1  { local a="$1" && shift && echo -e "$T1 $a $T2 $* $O" >&2; }
    function sh  {
        hook pre "$@"
        if [[ "$?" != "$skip_func_after_hook" ]]; then call "$@"; fi
        hook post "$@"
    }
    function download {
        type wget 2>/dev/null 1>/dev/null && {
             wget -O "$2" "$1" 
             return $?
        }
        curl -L -o "$2" "$1"
    }

    function hook  {
        local fn="scripts/$2_$1.sh"
        test -e "$fn" || return 0
        shift
        shift
        unset hookfunc
        source "$fn" "$@"
        test -n "$hookfunc" || return
        call "$hookfunc" "$@"
    }

    function call  {
        nfo "$@"
        "$@" || {
            ret="$?"
            if [[ "$ret" == "$skip_func_after_hook" ]]; then return "$skip_func_after_hook"; fi
            nfo "ERR" $1
            test -n "$lc_exit_err" && exit 1
            return 1
        }
    }

    function as_subproc  {
        # call the func within a subproc, so that we have global exit after fail of first sh called func
        ( lc_exit_err=true; sh "$@" ) || { nfo "ERR" $1; return 1; }
        return 0
    }



    function conda_root  { echo "${conda_root:-$MAMBA_ROOT_PREFIX}"; }

    function activate_venv {
        # must be set in environ:
        local conda_env="$(conda_root)/envs/${PROJECT}_py${pyver}"
        test -e "$conda_env" || { nfo "No $conda_env"; echo -e "Run$M \nmake ci-conda-py-env$O"; return 1; }
        test -z "$CONDA_SHLVL" && { micromamba activate || return 1; }
        test "$CONDA_PREFIX" = "${conda_env:-x}" && return 0
        while [ -n "$CONDA_PREFIX" ]; do micromamba deactivate; done
        nfo 'Adding micromamba root env $PATH'
        export PATH="$(conda_root)/bin:$PATH"
        nfo Activating "$conda_env"
        micromamba activate "$conda_env"
    }

    function set_version {
        if [ "${versioning:-}" = "calver" ]; then
                version="$(date "+%Y.%m.%d")"
                return 0
        fi
        nfo "Say ./make release <version>"
        return 1
    }

    function ci-conda-root-env { ci-conda-base-env "$@"; } # backwards compat
    
    function make {
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

    ## Function Aliases:

    function d   {  make docs               "$@"  ; }
    function ds  {  make docs-serve         "$@"  ; }
    function clc {  make clean-lp-caches    "$@"  ; }
    function rel {  make release            "$@"  ; }
    function t   {  make tests              "$@"  ; }
    function sm  {  source ./make            "$@"  ; } # after changes
    # End

}

# ----------------------------------------------------------------------------------------- Make Functions:


function help {
    funcs()   { local a="func" && grep "^${a}tion" ./make | grep " {" | sed -e "s/${a}tion/- /g" | sed -e 's/{//g' | sort; }
    aliases() { local a="## Function" && grep -A 30 "$a Aliases:" "$here/make" | head -n 8 | tail -n 7 | sed -e 's/function/-/g' | sed -e 's/{//g' | cut -d '"' -f 1; }
    local doc="
    # Repo Ops and Maintenance Functions

    ## Usage: make <function> [args]
    
    ℹ️ Source the ./environ file before calling make

    ## Functions:

    $(funcs)

    ## Aliases
    $(aliases)

    "
    doc="$(echo "$doc" | sed -e 's/^    //g')"
    echo -e "$doc\n"
}

function self-update {

    url_make="https://raw.githubusercontent.com/axiros/docutools/master/make"
    h1 "Updating to: $url_make"
    

    function run_self_update {
        # Right now we only update make. in post_self_update one could do other stuff
        test -e make || return 1
        rm -f make.orig
        mv make make.orig
        curl -s "$url_make" > './make'
        diff make make.orig && { echo "Already up to date (ver $VERSION_MAKE)"; rm -f make.orig; return 0; }
        # updates
        rm -f scripts/self_update
        . make post_self_update && echo "Updated make (ver $VERSION_MAKE)"
    }
    run_self_update "$@"
}

function ci-conda-base-env { # creates the root conda env if not present yet
    source scripts/conda.sh && make_conda_root_env "$@"
}

function ci-conda-py-env {   # creates the venv for the project and poetry installs
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
    local tests=true
    test "${1:-}" = "notests" && { 
        nfo "Release w/o Tests!"
        tests=false
        shift
    }
    test -z "$2" || { echo "say make release <version>"; return 1; }
    version="${1:-}"
    test -z "$version" && { set_version || return 1; }
    nfo "New Version = $version"
    sh poetry version "$version"
    $tests && {
        sh tests
        #sh cover # cov reports created on ci
        # create a new changelog, this is committed, since on CI --depth=1:
        sh rm -f "$fn_changelog"
        lp_eval=changelog docs
        sh docs
    }
    sh poetry build
    sh git commit -am "chore: Prepare release $version" || true
    sh git tag "$version"
    sh poetry publish
    sh git push --tags
}

helper_funcs
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

