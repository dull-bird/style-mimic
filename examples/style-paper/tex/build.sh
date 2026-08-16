#!/usr/bin/env bash
set -euo pipefail

TEX_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$TEX_DIR/.." && pwd)"
DATA_FILE="$ROOT_DIR/data/styles.json"
GENERATOR="$ROOT_DIR/scripts/generate_latex.py"

cd "$TEX_DIR"
if ! command -v xelatex >/dev/null 2>&1; then
  echo "xelatex is required to compile the Chinese edition" >&2
  exit 2
fi

python3 "$GENERATOR" --data "$DATA_FILE" --out "$TEX_DIR"
: > build.log
xelatex -interaction=nonstopmode -halt-on-error style-mimic-paper.tex 2>&1 | tee -a build.log
bibtex style-mimic-paper 2>&1 | tee -a build.log
xelatex -interaction=nonstopmode -halt-on-error style-mimic-paper.tex 2>&1 | tee -a build.log
xelatex -interaction=nonstopmode -halt-on-error style-mimic-paper.tex 2>&1 | tee -a build.log

test -s style-mimic-paper.pdf
echo "Built $TEX_DIR/style-mimic-paper.pdf"
