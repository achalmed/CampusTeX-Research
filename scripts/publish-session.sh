#!/usr/bin/env bash
# ============================================================
# publish-session.sh — Publica y CONGELA una sesión en el MOOC del dictado
# ============================================================
# Uso:
#   ./scripts/publish-session.sh COURSE_DIR NN PERIODO [--refrescar]
#
# Crea (congelado) el módulo MOOC de la sesión SNN dentro del dictado:
#   COURSE/09_SEMESTRES/PERIODO/publicacion/SNN_slug/{slides,evaluation,practice,homework}
# Copia una INSTANTÁNEA de los PDF finales de la anatomía de la sesión:
#   02_Clase→slides · 04_Evaluacion→evaluation · 03_Actividad→practice · 05_Despues→homework
# y deja el módulo en SOLO LECTURA ("publicar = congelar"): el semestre se va
# congelando sesión a sesión. El sitio pub_* se enlaza por HARDLINK a este módulo
# (una sola copia, varios canales). --refrescar re-publica (descongela y rehace).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,18p' "${BASH_SOURCE[0]}"; exit 1; }
[[ $# -ge 3 ]] || usage
COURSE="$1"; NN="$2"; PERIODO="$3"; REFRESCAR=0
[[ "${4:-}" == "--refrescar" ]] && REFRESCAR=1
is_course "$COURSE" || die "No parece un curso: $COURSE"

SES="$(session_dir "$COURSE" "$NN")" || die "No existe la sesión $NN en $COURSE/03_SESIONES/"
SNAME="$(basename "$SES")"
PERDIR="$COURSE/09_SEMESTRES/$PERIODO"
[[ -d "$PERDIR" ]] || die "No existe el periodo $PERIODO. Créalo: ./scripts/new-period.sh \"$COURSE\" $PERIODO"
PUB="$PERDIR/publicacion"
[[ -d "$PUB" ]] || die "El periodo $PERIODO no tiene publicacion/ (estructura antigua). Refresca el periodo."
MOD="$PUB/$SNAME"

if [[ -e "$MOD" ]]; then
  [[ "$REFRESCAR" == 1 ]] || die "Ya publicado y congelado: $MOD
Para re-publicar (sobrescribe la versión congelada): añade --refrescar"
  chmod -R u+w "$MOD"; rm -rf "$MOD"
fi

# Crear el módulo desde la plantilla (o subcarpetas mínimas)
if [[ -d "$PUB/_plantilla_modulo" ]]; then
  cp -a "$PUB/_plantilla_modulo" "$MOD"
  rm -f "$MOD/README.md"                 # el README de la plantilla no aplica a un módulo real
else
  mkdir -p "$MOD"/{slides,evaluation,practice,homework}
fi

# Copiar (instantánea congelable) los PDF finales y materiales (odt/ods/docx/xlsx…) de cada parte de la sesión
copiar_pdfs() {  # $1 carpeta origen · $2 subcarpeta destino → imprime el conteo
  local src="$1" dst="$MOD/$2" n=0 f
  mkdir -p "$dst"
  if [[ -d "$src" ]]; then
    while IFS= read -r f; do cp "$f" "$dst/" && n=$((n+1)); done \
      < <(find "$src" -maxdepth 1 -type f \( -name '*.pdf' -o -name '*.odt' -o -name '*.ods' -o -name '*.odp' -o -name '*.docx' -o -name '*.xlsx' -o -name '*.pptx' -o -name '*.csv' -o -name '*.zip' \) 2>/dev/null)
  fi
  echo "$n"
}
s=$(copiar_pdfs "$SES/02_Clase"      slides)
e=$(copiar_pdfs "$SES/04_Evaluacion" evaluation)
p=$(copiar_pdfs "$SES/03_Actividad"  practice)
h=$(copiar_pdfs "$SES/05_Despues"    homework)

# Marcador de publicación
cat > "$MOD/_PUBLICADO.md" <<EOF
# Publicado — $SNAME  ($PERIODO)

- **Fecha:** $(date +%F)
- **Estado:** congelado (solo lectura). Para amendar: \`publish-session.sh … --refrescar\`.
- **Fuente:** \`03_SESIONES/$SNAME/\` — 02_Clase→slides ($s) · 04_Evaluacion→evaluation ($e) · 03_Actividad→practice ($p) · 05_Despues→homework ($h).
- El sitio \`pub_*\` se enlaza por **hardlink** a este módulo (una copia, varios canales).
EOF

# Congelar: solo lectura recursivo (el registro durable es el commit de git)
chmod -R a-w "$MOD"

ok "Publicado y congelado: $MOD"
echo "   slides=$s  evaluation=$e  practice=$p  homework=$h"
[[ $((s+e+p+h)) -eq 0 ]] && warn "No se encontraron PDF finales en la sesión; compila primero (build-session.sh) y re-publica con --refrescar."
echo "Enlaza al sitio (F5.2): ./scripts/publish-web.sh \"$COURSE\" $PERIODO --aplicar   (hardlinks segun dictado.yml)"
echo "Registra en git:  git add -A && git commit -m \"publica $SNAME ($PERIODO)\""
