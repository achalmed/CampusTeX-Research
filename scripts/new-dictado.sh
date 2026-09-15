#!/usr/bin/env bash
# ============================================================
# new-dictado.sh — Crea un dictado en docencia/dictados/<clave>/ (§4.4, M5)
# ============================================================
# Uso:
#   ./scripts/new-dictado.sh AAAA-ciclo INSTITUCION MATERIA "TÍTULO" [--web-edicion EDICION]
#
# Ejemplo:
#   ./scripts/new-dictado.sh 2026-ii cau-unsch metodologia "Metodología de la Investigación — 2026-II"
#     → docencia/dictados/2026-ii-cau-unsch-metodologia/dictado.yml  (+ registro/2026-ii-cau-unsch-metodologia/)
#
# La clave <periodo>-<institucion>-<materia> es la misma en dictados/ (manifiesto + publicacion/, producto
# git-ignorado) y en registro/ (repo privado: estudiantes, calificaciones, evidencias). Sustituye a new-period.sh.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 4 ]] || usage
PERIODO="$(slugify "$1")"; INST="$(slugify "$2")"; MATERIA="$(slugify "$3")"; TITLE="$4"; shift 4
[[ "$PERIODO" =~ ^[0-9]{4}-(i|ii)$ ]] || die "periodo AAAA-i | AAAA-ii (minúsculas): $PERIODO"
EDICION="${PERIODO/-i/-1}"; EDICION="${EDICION/-1i/-2}-$INST"
[[ "${1:-}" == "--web-edicion" ]] && EDICION="$2"
CLAVE="${PERIODO}-${INST}-${MATERIA}"
DEST="$DICTADOS_DIR/$CLAVE"
[[ -e "$DEST" ]] && die "Ya existe: $DEST"
mkdir -p "$DEST"
sed -e "s|{{DICTADO}}|$CLAVE|g" -e "s|{{PERIODO}}|$PERIODO|g" -e "s|{{INSTITUCION}}|$INST|g" -e "s|{{TITLE}}|$TITLE|g" \
    -e "s|{{MATERIA_WEB}}|$MATERIA|g" -e "s|{{EDICION_WEB}}|$EDICION|g" "$SCAFFOLDS_DIR/dictado/dictado.yml" > "$DEST/dictado.yml"
ok "Dictado creado: $DEST/dictado.yml"
if [[ -d "$REGISTRO_DIR" ]]; then
  mkdir -p "$REGISTRO_DIR/$CLAVE"
  [[ -f "$REGISTRO_DIR/$CLAVE/README.md" ]] || printf -- '---\ntipo: doc\ntitulo: "Registro del dictado %s"\nestado: activo\n---\n# Registro privado — %s\n\nEstudiantes, asistencia, calificaciones, evaluaciones aplicadas y evidencias de este dictado. Nunca con remote público.\n' "$CLAVE" "$CLAVE" > "$REGISTRO_DIR/$CLAVE/README.md"
  ok "Registro privado: $REGISTRO_DIR/$CLAVE/"
fi
echo "Siguiente: declara cursos[] y sesiones[] en dictado.yml; publica con ./scripts/publish-session.sh $CLAVE <curso> NN"
