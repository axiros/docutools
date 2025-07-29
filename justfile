# docutools - Development Task Runner
# Modern replacement for the make script using just

# Default recipe to display help
default:
    @just --list

# Initialize development environment using brew. Tested on OSX
init:
    @command -v brew >/dev/null || (echo "❌ Error: Homebrew is required but not installed." && echo "Install it from: https://brew.sh" && exit 1)
    @echo "Installing system dependencies..."
    brew install tmux graphviz imagemagick
    @echo "Setting up uv and installing dependencies..."
    uv sync
    @echo "Development environment ready!"

# Install/sync dependencies
install:
    uv sync

# Run all tests
test *ARGS:
    uv run pytest {{ARGS}} tests -c config/pytest.ini

# Run tests with coverage
test-cov:
    uv run coverage run --rcfile=config/coverage.pytest.ini -m pytest tests -c config/pytest.ini
    uv run coverage combine
    uv run coverage report --precision=2

# Format code with ruff
format:
    uv run ruff format src tests
    uv run ruff check --fix src tests

# Run type checking
typecheck:
    uv run mypy src

# Lint code
lint:
    uv run ruff check src tests

# Run all quality checks (format, lint, typecheck)
check: format lint typecheck

# Build documentation
docs:
    rm -f docs/autodocs
    uv run coverage run --rcfile=config/coverage.lp.ini $(uv run which mkdocs) build

# Serve documentation locally
docs-serve PORT="2222":
    @echo "Serving docs on http://127.0.0.1:{{PORT}}"
    @pkill -f "mkdocs serve.*{{PORT}}" || true
    uv run mkdocs serve -a "127.0.0.1:{{PORT}}"

# Check documentation links
docs-checklinks:
    uv run linkchecker --help | cat >/dev/null || (echo "Install linkchecker: pip install git+https://github.com/linkchecker/linkchecker.git" && exit 1)
    uv run linkchecker site --ignore-url '(.*).json'

# Clean build artifacts and caches
clean:
    rm -f .coverage*
    rm -rf .mypy_cache .pytest_cache build dist pip-wheel-metadata site public __pycache__
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    just clean-lp

# Clean LP (Literal Programming) caches
clean-lp:
    @echo "Cleaning LP caches..."
    find . -name "*.lp.py" -delete

# Build the package
build:
    uv build

# Run tests and lp doc tests:
doctest:
    just test
    just docs

# Calcs a version, adds to pyproject, git tags, calls publish <version>
new-version VERSION="": 
    #!/usr/bin/env bash
    set -euo pipefail
    
    VERSION_ARG="{{VERSION}}"
    if [ -z "$VERSION_ARG" ]; then
        # Use calendar versioning by default
        VERSION_ARG=$(date "+%Y.%m.%d")
        echo "Using calendar version: $VERSION_ARG"
    fi
    
    echo "Releasing version $VERSION_ARG"
    sed -i '' "s/^version = .*/version = \"$VERSION_ARG\"/" pyproject.toml
    git commit -am "chore: Prepare release {{VERSION}}" || true
    git tag "{{VERSION}}"
    git push --tags



publish: 
    just clean
    just build
    uv publish --token "$(pass pypitoken)"

# Development shortcuts
alias t := test
alias d := docs  
alias ds := docs-serve
alias clc := clean-lp
