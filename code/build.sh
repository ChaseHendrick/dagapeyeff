#!/bin/sh
# Build the manuscript PDF from its LaTeX source.
#
#   sh code/build.sh   (from the paper folder, or give its path from anywhere)
#
# Regenerates numbers.tex, the tables and the figures from the frozen results, then runs pdflatex, bibtex
# and pdflatex twice in a scratch folder, so no .aux or .log files land in the repository. SOURCE_DATE_EPOCH
# is the date of the last commit that changed the source, not counting the PDF, so committing the PDF does
# not change the date the next build uses. Needs pdflatex, bibtex and pgfplots (TeX Live).
set -eu
HERE=$(cd "$(dirname "$0")/.." && pwd)
python3 "$HERE/code/make_numbers.py"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp "$HERE"/paper/*.tex "$HERE"/paper/refs.bib "$TMP"/
SOURCE_DATE_EPOCH=$(git -C "$HERE" log -1 --format=%ct -- paper ':(exclude)paper/*.pdf' 2>/dev/null || true)
[ -n "$SOURCE_DATE_EPOCH" ] || SOURCE_DATE_EPOCH=$(date +%s)
export SOURCE_DATE_EPOCH FORCE_SOURCE_DATE=1
cd "$TMP"
pdflatex -interaction=nonstopmode -halt-on-error dagapeyeff-exclusions.tex >/dev/null
bibtex dagapeyeff-exclusions >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error dagapeyeff-exclusions.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error dagapeyeff-exclusions.tex >/dev/null
if grep -E "Overfull|undefined" dagapeyeff-exclusions.log; then echo "layout or reference warnings above"; fi
cp dagapeyeff-exclusions.pdf "$HERE/paper/dagapeyeff-exclusions.pdf"
echo "built $HERE/paper/dagapeyeff-exclusions.pdf"
