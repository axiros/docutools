root_tools="tree fd-find ripgrep poetry"

function make_conda_root_env { # creates the root conda env if not present yet
    type micromamba && return
    echo -e "\x1b[1mInstalling micromamba.\x1b[0m"
    echo "Please confirm all question unless you know what you are doing."
    "${SHELL}" <(curl -L micro.mamba.pm/install.sh)
    call . "$HOME/.$(basename $SHELL)rc"
    call micromamba activate
    call eval micromamba install --yes $root_tools ${conda_root_tools:-}
    call micromamba info
    nfo "Next, run \x1b[1mmake ci-conda-py-env\x1b[0m"
}

function make_conda_py_env { # creates the venv for the project and poetry installs
    # main conda bin is in path
    local n="${PROJECT}_py${pyver}"
    local p="$(conda_root)/envs/$n"
    call micromamba activate
    test -e "$p" || {
        echo "Installing $p (with tools: $conda_project_tools)"
        call eval micromamba create --yes -q -n "${n}" python="${pyver}" ${conda_project_tools:-} $*
    }
    call activate_venv || return 1
    call poetry install
    call ls -a "$(conda_root)/envs/"
    call micromamba list
}
