#!/usr/bin/env bash
# generate-stubs.sh — Generate Python type stubs for sublimelsp/LSP.
#
# Usage:
#   ./generate-stubs.sh [LSP_REF]
#
#   LSP_REF  Tag, branch, or commit to check out (default: main)
#
# Output: LSP/ directory at the repo root containing .pyi files structured
#         to match the import namespace (from LSP.plugin import ...,
#         from LSP.protocol import ...).
#
# Requirements: git, uv

PYTHON_VERSION=3.8

set -euo pipefail

LSP_REPO="https://github.com/sublimelsp/LSP"
LSP_REF="${1:-main}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/.."
WORK_DIR="$(mktemp -d)"
LSP_SRC="$WORK_DIR/LSP"
STUB_TMP="$WORK_DIR/out"

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
cleanup() {
    rm -rf "$WORK_DIR"
}
trap cleanup EXIT

log() { echo "[generate-stubs] $*"; }

# ---------------------------------------------------------------------------
# Check for uv
# ---------------------------------------------------------------------------
if ! command -v uv &>/dev/null; then
    echo "Error: uv not found in PATH (https://docs.astral.sh/uv/getting-started/installation/)" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Clone LSP
# ---------------------------------------------------------------------------
log "Cloning $LSP_REPO @ $LSP_REF ..."
# --branch works for tags and branches but not bare commit SHAs, so fall back
# to a full clone + checkout when needed.
if ! git clone --quiet --depth=1 --branch "$LSP_REF" "$LSP_REPO" "$LSP_SRC" 2>/dev/null; then
    log "'$LSP_REF' is not a branch/tag; doing full clone + checkout ..."
    git clone --quiet "$LSP_REPO" "$LSP_SRC"
    git -C "$LSP_SRC" checkout --quiet "$LSP_REF"
fi

LSP_COMMIT=$(git -C "$LSP_SRC" rev-parse HEAD)
LSP_TAG=$(git -C "$LSP_SRC" describe --tags --always 2>/dev/null || echo "$LSP_COMMIT")
log "Checked out: $LSP_TAG ($LSP_COMMIT)"

# ---------------------------------------------------------------------------
# Generate stubs
# ---------------------------------------------------------------------------
cp -rf "$LSP_SRC/stubs"/* "$LSP_SRC"

log "Generating stubs..."
mkdir -p "$STUB_TMP"
uvx --python="${PYTHON_VERSION}" --from=mypy stubgen \
    --parse-only \
    --include-docstrings \
    "$LSP_SRC" \
    -o "$STUB_TMP"

# remove unneeded files
rm -rf "$STUB_TMP/tests" "$STUB_TMP/tests_"*

# ---------------------------------------------------------------------------
# Assemble output under LSP/ to match the import namespace
# ---------------------------------------------------------------------------
LSP_OUT="$PROJECT_DIR/stubs/LSP"
log "Writing stubs to $LSP_OUT/ ..."
rm -rf "$LSP_OUT"

mkdir -p "$LSP_OUT"
[[ -d $STUB_TMP ]] && mv -Tf "$STUB_TMP" "$LSP_OUT/"

# Fix Incomplete placeholder types, class attribute types, and normalize to LF.
# Uses Python's AST module to infer types from source without executing code.
log "Post-processing stubs..."
LSP_OUT="$LSP_OUT" LSP_SRC="$LSP_SRC" uv run python "${SCRIPT_DIR}/fix-stubs.py"

# Format stubs with ruff
uvx --from ruff ruff format "${LSP_OUT}"

# Marker file so consumers can tell which LSP version the stubs came from
cat >"$LSP_OUT/.version" <<EOF
ref: $LSP_REF
tag: $LSP_TAG
commit: $LSP_COMMIT
EOF

log "Done."
log "Stubs: $LSP_OUT/"
log "LSP:   $LSP_TAG"
