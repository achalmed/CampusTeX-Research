#!/usr/bin/env bash
# ============================================================
# build-course.sh — Compila un curso completo
# ============================================================
# Uso:
#   ./scripts/build-course.sh COURSE_DIR [--solo-sesiones]
#
# Compila:
#   1. Documentos administrativos (.tex) de 00_ADMINISTRACION/,
#      01_PLANIFICACION/ y 08_INVESTIGACION/ (omitir con --solo-sesiones).
#   2. El deck de cada sesión (vía build-session.sh).
#
# Continúa aunque algo falle y reporta el resumen al final.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }
COURSE="$1"
is_course "$COURSE" || die "No parece un curso: $COURSE"
SOLO_SESIONES=0
[[ "${2:-}" == "--solo-sesiones" ]] && SOLO_SESIONES=1

declare -a fallos=()

# --- Documentos administrativos ------------------------------
if [[ "$SOLO_SESIONES" -eq 0 ]]; then
  while IFS= read -r -d '' tex; do
    compile_tex "$tex" || fallos+=("$tex")
  done < <(find "$COURSE/00_ADMINISTRACION" "$COURSE/01_PLANIFICACION" "$COURSE/08_INVESTIGACION" \
             -name '*.tex' -not -path '*index_files*' -print0 2>/dev/null)
fi

# --- Sesiones -------------------------------------------------
for dir in $(list_sessions "$COURSE"); do
  num="$(basename "$dir" | sed -E 's/^S([0-9]+).*/\1/')"
  "$FW_DIR/scripts/build-session.sh" "$COURSE" "$num" || fallos+=("sesión $num")
done

echo
if [[ ${#fallos[@]} -eq 0 ]]; then ok "Curso compilado sin errores."
else error "Fallaron ${#fallos[@]} compilaciones:"; printf '  - %s\n' "${fallos[@]}"; exit 1; fi
