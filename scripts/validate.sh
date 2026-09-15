#!/usr/bin/env bash
# ============================================================
# validate.sh — Valida la estructura estándar 00–09
# ============================================================
# Uso:
#   ./scripts/validate.sh COURSE_DIR         # valida un curso
#   ./scripts/validate.sh ACADEMIC_CLASS_DIR # valida todos sus course_*
#
# Comprueba por curso:
#   - Las 10 carpetas 00–09 + README.md.
#   - Cada sesión (03_SESIONES/SNN_*): anatomía 01_Antes…07_Notas,
#     metadata.yml (núcleo id/titulo/estado, §7), README.md y deck en 02_Clase/.
#
# Código de salida != 0 si hay errores (los [!!] no hacen fallar).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 1; }
TARGET="$1"
[[ -d "$TARGET" ]] || die "No existe: $TARGET"

errors=0
err() { error "$*"; errors=$((errors + 1)); }

COURSE_DIRS=(00_ADMINISTRACION 01_PLANIFICACION 02_CONTENIDO 03_SESIONES \
  04_EVALUACIONES 05_ESTUDIANTES 06_RECURSOS 07_MULTIMEDIA 08_INVESTIGACION \
  09_SEMESTRES)
SESSION_DIRS=(01_Antes 02_Clase 03_Actividad 04_Evaluacion 05_Despues 06_Recursos 07_Notas)

validate_course() {
  local course="$1" name; name="$(basename "$course")"
  info "Curso: $name"
  for d in "${COURSE_DIRS[@]}"; do
    [[ -d "$course/$d" ]] || err "$name: falta la carpeta $d/"
  done
  [[ -f "$course/README.md" ]] || err "$name: falta README.md"

  for s in $(list_sessions "$course"); do
    local sname; sname="$(basename "$s")"
    [[ -f "$s/metadata.yml" ]] || err "$name/$sname: falta metadata.yml"
    for k in id titulo estado; do
      grep -qE "^${k}:" "$s/metadata.yml" 2>/dev/null || err "$name/$sname: metadata sin '$k'"
    done
    for d in "${SESSION_DIRS[@]}"; do
      [[ -d "$s/$d" ]] || err "$name/$sname: falta $d/"
    done
    local deck; deck="$(find "$s/02_Clase" \( -name '*.tex' -o -name '*.qmd' \) -not -path '*index_files*' 2>/dev/null | head -1)"
    [[ -n "$deck" ]] || warn "$name/$sname: 02_Clase/ sin deck .tex ni .qmd"
  done
}

if is_course "$TARGET"; then
  validate_course "$TARGET"
else
  mapfile -t courses < <(list_courses "$TARGET")
  [[ ${#courses[@]} -gt 0 ]] || die "No es un curso ni contiene course_*: $TARGET"
  for c in "${courses[@]}"; do validate_course "$c"; done
fi

echo
if [[ "$errors" -eq 0 ]]; then ok "Estructura válida. Sin errores."
else error "Validación con $errors error(es)."; exit 1; fi
