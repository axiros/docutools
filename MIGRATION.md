# Migration from make/poetry to just/uv

## Quick Start

1. **Install just and uv** (if not already installed):
   ```bash
   brew install just uv
   ```

2. **Initialize the environment**:
   ```bash
   just init
   ```

3. **Common commands**:
   ```bash
   just test           # Run tests
   just docs           # Build documentation  
   just docs-serve     # Serve docs locally
   just format         # Format code
   just build          # Build package
   just clean          # Clean build artifacts
   ```

## Command Mapping

| Old (make) | New (just) | Description |
|------------|------------|-------------|
| `source ./make -a && make tests` | `just test` | Run tests |
| `make docs` | `just docs` | Build documentation |
| `make docs-serve` | `just docs-serve` | Serve documentation |
| `make clean` | `just clean` | Clean build artifacts |
| `make release <version>` | `just release <version>` | Release new version |

## Key Changes

### Dependencies Management
- **Before**: Poetry managed dependencies
- **After**: uv manages dependencies (much faster)
- **Migration**: Dependencies moved from `[tool.poetry.dependencies]` to `[project.dependencies]` in pyproject.toml

### Build System  
- **Before**: Poetry build backend
- **After**: Hatchling build backend (modern, standards-compliant)

### System Dependencies
- **Before**: Installed via conda through `environ` file
- **After**: Installed via `brew install` in `just init`
- **Dependencies**: tmux, poetry, graphviz, imagemagick

### Task Runner
- **Before**: Bash functions in `make` script
- **After**: Just recipes in `justfile`
- **Benefits**:
  - Better syntax highlighting
  - Built-in help system (`just --list`)
  - Cross-platform compatibility
  - More readable recipe syntax

## Environment Setup

The old `environ` file approach is replaced by:

1. System dependencies via `just init` (uses brew)
2. Python dependencies via `uv sync`
3. Environment variables can be set in `.env` files (uv loads them automatically)

## Development Workflow

```bash
# One-time setup
just init

# Daily development
just test              # Run tests
just format           # Format code before committing
just docs-serve       # Preview documentation

# Release workflow  
just test             # Ensure tests pass
just build            # Build package
just release 2024.01.15  # Release with version
```

## Migration Status

✅ **Completed**:
- Basic task runner (just)
- Dependency management (uv)
- Build system (hatchling)
- Common development tasks
- System dependency installation

⏳ **Not Yet Migrated**:
- All advanced make functions (conda environment management, etc.)
- Git hooks and automation
- Advanced CI/CD integrations
- Coverage combination logic
- Changelog generation

These can be added incrementally as needed.
