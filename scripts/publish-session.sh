#!/usr/bin/env bash
# ============================================================
# publish-session.sh — Publica una sesión en el módulo MOOC de un dictado (M5, §4.4)
# ============================================================
# Uso:
#   ./scripts/publish-session.sh DICTADO CURSO NN [--refrescar]
#
# DICTADO: clave o ruta (docencia/dictados/<clave>). CURSO: slug o ruta. NN: sesión sNN-*.
# La sesión debe figurar en dictado.yml → sesiones[] {curso, sesion, web}; el módulo es
#   docencia/dictados/<clave>/publicacion/<web>/{slides,evaluation,practice,homework}
# (PRODUCTO git-ignorado; la web lo enlaza por hardlink con publish-web.sh). Contenido:
#   slides ← *.pdf de la raíz de la sesión · practice ← practica*/plantilla*/portada*/taller* y demás
#   documentos de oficina · evaluation ← evaluacion*/quiz*/rubrica*/examen* · homework ← tarea*/homework*.
# Congelar = etiquetar: se crea el tag `dictado/<clave>/<sesion>` en el repo docencia/ sobre el commit
# actual de las fuentes (no se copia nada versionado). --refrescar re-publica y mueve el tag.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,17p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
DICT="$(dictado_dir "$1")" || die "No es un dictado (falta dictado.yml): $1"
COURSE="$(course_dir "$2")" || die "No es un curso: $2"
NN="$3"; REFRESCAR=0; [[ "${4:-}" == "--refrescar" ]] && REFRESCAR=1
SES="$(session_dir "$COURSE" "$NN")" || die "No existe la sesión $NN en $COURSE/03-sesiones/"
SNAME="$(basename "$SES")"; CSLUG="$(basename "$COURSE")"; CLAVE="$(basename "$DICT")"

WEB="$(python3 - "$DICT/dictado.yml" "$CSLUG" "$SNAME" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1])) or {}
for s in d.get("sesiones") or []:
    if s.get("curso") == sys.argv[2] and s.get("sesion") == sys.argv[3]:
        print(s.get("web") or ""); break
PY
)"
[[ -n "$WEB" ]] || die "La sesión $CSLUG/$SNAME no está en $DICT/dictado.yml → sesiones[] (declárala con su 'web')"
MOD="$DICT/publicacion/$WEB"
if [[ -e "$MOD" ]]; then
  [[ "$REFRESCAR" == 1 ]] || die "Ya publicado: $MOD (añade --refrescar para re-publicar)"
  rm -rf "$MOD"
fi
mkdir -p "$MOD"     # las subcarpetas se crean solo si reciben archivos (ninguna carpeta vacía en docencia/, §4.2)

OFICINA='\( -name "*.pdf" -o -name "*.odt" -o -name "*.ods" -o -name "*.odp" -o -name "*.docx" -o -name "*.xlsx" -o -name "*.pptx" -o -name "*.csv" -o -name "*.zip" \)'
s=0; e=0; p=0; h=0
while IFS= read -r f; do
  b="$(basename "$f")"; bl="${b,,}"
  case "$bl" in
    *.pdf)                                     mkdir -p "$MOD/slides";     cp "$f" "$MOD/slides/"     && s=$((s+1)) ;;
    evaluacion*|quiz*|rubrica*|examen*)        mkdir -p "$MOD/evaluation"; cp "$f" "$MOD/evaluation/" && e=$((e+1)) ;;
    tarea*|homework*)                          mkdir -p "$MOD/homework";   cp "$f" "$MOD/homework/"   && h=$((h+1)) ;;
    *)                                         mkdir -p "$MOD/practice";   cp "$f" "$MOD/practice/"   && p=$((p+1)) ;;
  esac
done < <(eval find "\"$SES\"" -maxdepth 1 -type f "$OFICINA" 2>/dev/null | sort)

cat > "$MOD/_PUBLICADO.md" <<EOT
---
tipo: doc
titulo: "Publicado — $CSLUG/$SNAME ($CLAVE)"
estado: hecho
---
<!-- GENERADO por 10 Class/scripts/publish-session.sh; producto no versionado (publicacion/ está en .gitignore) -->
# Publicado — $CSLUG/$SNAME  ($CLAVE → $WEB)

- **Fecha:** $(date +%F)
- **Fuente:** \`cursos/$CSLUG/03-sesiones/$SNAME/\` (artefacto: $(session_artifact "$SES")); tag \`dictado/$CLAVE/$SNAME\`.
- slides=$s · evaluation=$e · practice=$p · homework=$h
- La web se enlaza por **hardlink** a este módulo: \`./scripts/publish-web.sh $CLAVE --aplicar\`.
EOT

TAG="dictado/$CLAVE/$SNAME"
if git -C "$DOCENCIA_DIR" rev-parse -q --verify "refs/tags/$TAG" >/dev/null 2>&1 && [[ "$REFRESCAR" == 0 ]]; then
  info "Tag existente: $TAG (no se mueve sin --refrescar)"
else
  git -C "$DOCENCIA_DIR" tag -f -a "$TAG" -m "Sesión $SNAME de $CSLUG publicada en $CLAVE ($(date +%F))" >/dev/null && ok "Tag: $TAG"
fi
ok "Publicado: $MOD   (slides=$s evaluation=$e practice=$p homework=$h)"
[[ $((s+e+p+h)) -eq 0 ]] && warn "Sin PDF ni materiales en la raíz de la sesión; compila primero (build-session.sh) y re-publica con --refrescar."
echo "Enlaza al sitio: ./scripts/publish-web.sh $CLAVE --aplicar"
