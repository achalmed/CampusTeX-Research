#!/usr/bin/env bash
# ============================================================
# new-course.sh — Crea un curso nuevo en docencia/cursos/<slug>/ (§4.2, M5)
# ============================================================
# Uso:
#   ./scripts/new-course.sh SLUG "TÍTULO" [--tipo asignatura|herramienta|nivelacion|taller] [--area a,b] [--materia-web m]
#
# Ejemplo:
#   ./scripts/new-course.sh econometria-iii "Econometría III" --tipo asignatura --area estadistica,econometria --materia-web econometria
#
# Crea SOLO el registro (curso.yml) y el README.md generado. Las carpetas 01-diseno … 05-recursos
# se crean al primer uso (new-session.sh, new-evaluacion.sh, new-report.sh); una carpeta vacía es error del validador.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 2 ]] || usage
SLUG="$1"; TITLE="$2"; shift 2
TIPO="asignatura"; AREAS=""; MATERIA="null"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tipo) TIPO="$2"; shift 2 ;;
    --area) AREAS="$2"; shift 2 ;;
    --materia-web) MATERIA="$2"; shift 2 ;;
    *) usage ;;
  esac
done
is_kebab "$SLUG" || die "El slug debe ser kebab-case ASCII: $SLUG"
case "$TIPO" in asignatura|herramienta|nivelacion|taller) : ;; *) die "tipo no admitido: $TIPO" ;; esac
DEST="$CURSOS_DIR/$SLUG"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"
[[ -d "$CURSOS_DIR" ]] || die "No existe $CURSOS_DIR (¿submódulo docencia/ sin inicializar?)"

ETIQUETA="${SLUG//-/_}"
AREAS_YML="$(echo "$AREAS" | sed -E 's/[[:space:]]//g; s/,/, /g')"
mkdir -p "$DEST"
for f in curso.yml README.md; do
  sed -e "s|{{COURSE_SLUG}}|$SLUG|g" -e "s|{{TITLE}}|$TITLE|g" -e "s|{{COURSE_TYPE}}|$TIPO|g" \
      -e "s|{{AREAS}}|$AREAS_YML|g" -e "s|{{ETIQUETA}}|$ETIQUETA|g" -e "s|{{MATERIA_WEB}}|$MATERIA|g" -e "s|{{FECHA}}|$(date +%F)|g" \
      "$SCAFFOLDS_DIR/curso/$f" > "$DEST/$f"
done
ok "Curso creado: $DEST"
"$FW_DIR/scripts/validate.sh" "$DEST" >/dev/null && ok "validate.sh: sin errores"
echo "Siguiente: ./scripts/new-session.sh $SLUG 01 \"Título de la sesión\" [--tipo clase|laboratorio|taller|evaluacion]"
