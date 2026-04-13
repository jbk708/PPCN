#!/bin/bash
# author: Jonathan Kirkland (jkirkland@sbpdiscovery.org)
#
# Spawn a Jupyter server on a compute node using the project's uv-managed
# virtual environment (conda is unavailable on this cluster).
#
# Submit from the PPCN repo root:
#     sbatch scripts/bash/jupyter.sh
#
# After the job starts, read the token from the .err log and SSH-tunnel:
#     ssh -N -L 7788:<node>:7788 <user>@<login-host>

#SBATCH -J jupyter
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jkirkland@sbpdiscovery.org
#SBATCH --time=96:00:00
#SBATCH --partition=normal
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --output=/home/jkirkland/logs/%x-%A_%a.out
#SBATCH --error=/home/jkirkland/logs/%x-%A_%a.err

set -euo pipefail

# --- Project layout -----------------------------------------------------------
PROJECT_DIR="${HOME}/repos/PPCN"
cd "${PROJECT_DIR}"

# --- uv bootstrap -------------------------------------------------------------
# uv installs to ~/.local/bin by default. Make sure it is on PATH and install
# it on-the-fly if missing (idempotent, no-op when already present).
export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
    echo "[jupyter.sh] uv not found — installing to ${HOME}/.local/bin"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # shellcheck disable=SC1091
    source "${HOME}/.local/bin/env"
fi

echo "[jupyter.sh] using uv: $(command -v uv) ($(uv --version))"

# --- Sync the project env (dev extras include jupyter) ------------------------
# .python-version pins to 3.12 so uv pulls prebuilt manylinux wheels for
# native packages (pysam, cyvcf2) instead of building from source — the
# cluster is missing libbz2-dev so a source build of htslib would fail.
# --frozen honors uv.lock exactly; fail instead of silently re-resolving.
uv sync --extra dev --frozen
echo "[jupyter.sh] python: $(uv run --no-sync python --version)"

# --- Launch Jupyter -----------------------------------------------------------
NODE_HOST=$(hostname -s)
echo "[jupyter.sh] starting Jupyter on ${NODE_HOST}:7788"
echo "[jupyter.sh] to tunnel: ssh -N -L 7788:${NODE_HOST}:7788 ${USER}@<login-host>"

exec uv run --no-sync jupyter notebook \
    --no-browser \
    --port=7788 \
    --ip=0.0.0.0
