#!/bin/bash
# render.sh <pptx> <outprefix> [pages...]
set -e
WD="$(cd "$(dirname "$1")" && pwd)"
SRC="$1"; PRE="$2"; shift 2
"/c/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir "$WD" "$SRC" >/dev/null 2>&1
PDF="$WD/$(basename "${SRC%.*}").pdf"
PYTHONIOENCODING=utf-8 python - "$PDF" "$WD/$PRE" "$@" <<'PY'
import sys, fitz
pdf, pre = sys.argv[1], sys.argv[2]
pages = [int(p) for p in sys.argv[3:]]
d = fitz.open(pdf)
if not pages: pages = list(range(1, d.page_count+1))
for p in pages:
    pix = d[p-1].get_pixmap(dpi=100)
    out = f"{pre}-{p}.png"; pix.save(out); print(out)
PY
