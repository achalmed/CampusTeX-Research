#!/usr/bin/env bash
# ============================================================
# clean.sh — Elimina archivos auxiliares de LaTeX
# ============================================================
# Uso:
#   ./scripts/clean.sh [--pdf]
#
# Elimina en todo el repositorio los auxiliares de compilación
# (.aux, .log, .nav, .snm, .toc, .out, .vrb, etc.).
# Con --pdf elimina también los PDF generados junto a un .tex
# o .qmd del mismo nombre (los PDF entregables sin fuente al
# lado nunca se tocan).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

AUX_EXTS=(aux log nav snm toc out vrb fls fdb_latexmk synctex.gz
          bbl blg bcf run.xml lof lot idx ilg ind)

count=0
for ext in "${AUX_EXTS[@]}"; do
  while IFS= read -r f; do
    rm -f "$f"; count=$((count + 1))
  done < <(find "$ROOT_DIR" -name ".git" -prune -o -type f -name "*.${ext}" -print)
done
ok "Eliminados $count archivos auxiliares."

if [[ "${1:-}" == "--pdf" ]]; then
  count=0
  while IFS= read -r pdf; do
    base="${pdf%.pdf}"
    if [[ -f "$base.tex" || -f "$base.qmd" ]]; then
      rm -f "$pdf"; count=$((count + 1))
    fi
  done < <(find "$ROOT_DIR" -name ".git" -prune -o -type f -name "*.pdf" -print)
  ok "Eliminados $count PDF regenerables."
fi
