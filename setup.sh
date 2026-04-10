#!/usr/bin/env bash
set -euo pipefail

PYTHON_MIN="3.11"
R_MIN="4.0"

info()  { printf "\033[1;34m▸ %s\033[0m\n" "$1"; }
ok()    { printf "\033[1;32m✓ %s\033[0m\n" "$1"; }
warn()  { printf "\033[1;33m⚠ %s\033[0m\n" "$1"; }
fail()  { printf "\033[1;31m✗ %s\033[0m\n" "$1"; exit 1; }

check_python_version() {
    local py_ver
    py_ver=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$(printf '%s\n' "$PYTHON_MIN" "$py_ver" | sort -V | head -1)" != "$PYTHON_MIN" ]; then
        fail "Python >= $PYTHON_MIN required (found $py_ver)"
    fi
    ok "Python $py_ver"
}

# --- Preflight ---
info "Checking prerequisites"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

# --- Python environment ---
if command -v uv >/dev/null 2>&1; then
    ok "uv found ($(uv --version))"
    info "Installing Python environment via uv"
    # uv respects requires-python in pyproject.toml and will fetch a
    # compatible interpreter automatically if the system Python is too old.
    uv sync
    ok "Python packages installed"
else
    warn "uv not found — falling back to pip"
    check_python_version
    python3 -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    pip install -e ".[dev]" --quiet
    ok "Python packages installed (pip + venv)"
fi

# --- R packages ---
if command -v R >/dev/null 2>&1; then
    r_ver=$(R --version 2>/dev/null | head -1 | grep -oP '\d+\.\d+')
    if [ "$(printf '%s\n' "$R_MIN" "$r_ver" | sort -V | head -1)" != "$R_MIN" ]; then
        warn "R >= $R_MIN recommended (found $r_ver)"
    else
        ok "R $r_ver"
    fi
    info "Installing R packages"
    Rscript R/install_packages.R
    ok "R packages installed"
else
    warn "R not found — skipping R setup (dNdScv requires R)"
fi

# --- Summary ---
echo ""
ok "Environment ready"
if command -v uv >/dev/null 2>&1; then
    echo "  Run commands:  uv run <cmd>"
    echo "  Or activate:   source .venv/bin/activate"
else
    echo "  Activate:      source .venv/bin/activate"
fi
echo "  Lint:          uv run ruff check scripts/"
echo "  Test:          uv run pytest tests/"
echo ""
