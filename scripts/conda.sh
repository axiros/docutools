function make_conda_root_env { # creates the root conda env if not present yet
    # main conda bin is in path
    local p="$(conda_root)"
    test -e "$p" && {
        nfo "Already present: $p"
        return 0
    }
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    chmod +x miniconda.sh
    ./miniconda.sh -b -p $p 2>/dev/null
    conda_act
    ls -a $HOME
}
function make_conda_py_env { # creates the venv for the project and poetry installs
    # main conda bin is in path
    local n="${PROJECT}_py${pyver}"
    local p="$(conda_root)/envs/$n"
    test -e "$p" && {
        nfo "Already present: $p"
        return 0
    }
    conda_act
    set -x
    conda create -q -n "${n}" python="${pyver}" ripgrep tmux fd-find poetry graphviz
    conda activate "$n"
    poetry install
    conda info
    ls -a "$(conda_root)/envs/"
}
