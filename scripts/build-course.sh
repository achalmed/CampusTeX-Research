#!/usr/bin/env bash
# ============================================================
# build-course.sh — Compila TODO el curso
# ============================================================
# Uso:
#   ./scripts/build-course.sh [--solo-sesiones]
#
# Compila:
#   1. Documentos administrativos: course/syllabus, course/topics,
#      course/policies (omitir con --solo-sesiones)
#   2. Todas las sesiones de course/sessions/ (vía build-session.sh)
#
# Continúa aunque una sesión falle y reporta el resumen al final.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

SOLO_SESIONES=0
[[ "${1:-}" == "--solo-sesiones" ]] && SOLO_SESIONES=1

declare -a fallos=()

# --- Documentos administrativos ------------------------------
if [[ "$SOLO_SESIONES" -eq 0 ]]; then
  for tex in "$ROOT_DIR/course/syllabus/syllabus.tex" \
             "$ROOT_DIR/course/topics/topics.tex" \
             "$ROOT_DIR/course/policies/lineamientos_cau_2026.tex"; do
    [[ -f "$tex" ]] || continue
    compile_tex "$tex" || fallos+=("$tex")
  done
fi

# --- Sesiones -------------------------------------------------
for dir in $(list_sessions); do
  num="$(basename "$dir" | sed -E 's/^session_([0-9]+).*/\1/')"
  "$ROOT_DIR/scripts/build-session.sh" "$num" || fallos+=("sesión $num")
done

echo
if [[ ${#fallos[@]} -eq 0 ]]; then
  ok "Curso completo compilado sin errores."
else
  error "Fallaron ${#fallos[@]} compilaciones:"
  printf '  - %s\n' "${fallos[@]}"
  exit 1
fi
