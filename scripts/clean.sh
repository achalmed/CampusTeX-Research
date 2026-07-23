#!/usr/bin/env bash
# ============================================================
# clean.sh — Elimina archivos auxiliares de LaTeX
# ============================================================
# Uso:
#   ./scripts/clean.sh [--pdf] [DIR]
#
# Elimina bajo DIR (por defecto la raíz del framework) los
# auxiliares de compilación (.aux, .log, .nav, .toc, …).
# Con --pdf elimina también los PDF que tengan un .tex/.qmd del
# mismo nombre al lado (los entregables sin fuente no se tocan).
#
# Para limpiar un curso: ./scripts/clean.sh --pdf /ruta/al/course_NN
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

PDF=0; DIR="$FW_DIR"
for a in "$@"; do
  case "$a" in
    --pdf) PDF=1 ;;
    *) DIR="$a" ;;
  esac
done
[[ -d "$DIR" ]] || die "No existe: $DIR"

AUX_EXTS=(aux log nav snm toc out vrb fls fdb_latexmk synctex.gz
          bbl blg bcf run.xml lof lot idx ilg ind)

count=0
for ext in "${AUX_EXTS[@]}"; do
  while IFS= read -r f; do
    rm -f "$f"; count=$((count + 1))
  done < <(find "$DIR" -name ".git" -prune -o -type f -name "*.${ext}" -print)
done
ok "Eliminados $count archivos auxiliares en ${DIR}."

if [[ "$PDF" -eq 1 ]]; then
  count=0
  while IFS= read -r pdf; do
    base="${pdf%.pdf}"
    if [[ -f "$base.tex" || -f "$base.qmd" ]]; then
      rm -f "$pdf"; count=$((count + 1))
    fi
  done < <(find "$DIR" -name ".git" -prune -o -type f -name "*.pdf" -print)
  ok "Eliminados $count PDF regenerables."
fi
