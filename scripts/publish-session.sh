#!/usr/bin/env bash
# ============================================================
# publish-session.sh — Publica una sesión en el módulo MOOC de un dictado (M5, §4.4; materiales del §10.7)
# ============================================================
# Uso:
#   ./scripts/publish-session.sh DICTADO CURSO NN [--simular] [--refrescar]
#
# DICTADO: clave o ruta (contenido/dictados/<clave>). CURSO: slug o ruta. NN: sesión sNN-*.
# La sesión debe figurar en dictado.yml → sesiones[] {curso, sesion, web}; el módulo es
#   docencia/dictados/<clave>/publicacion/<web>/{slides,evaluation,practice,homework}
# (PRODUCTO git-ignorado; la web lo enlaza por hardlink con publish-web.sh).
#
# Qué se publica, de la raíz de la sesión (primero por nombre, después por tipo):
#   evaluation ← evaluacion*/quiz*/rubrica*/examen* · homework ← tarea*/homework*/consigna*
#   practice   ← practica*/plantilla*/portada*/taller* (también plantilla*.md) · slides ← los demás *.pdf
#   practice   ← los demás documentos de oficina (.odt .ods .odp .docx .xlsx .pptx .csv .zip)
# Nunca: *-claves.pdf, *-soluciones.pdf, *-docente.pdf, ni el código o el .tex de la sesión. Si existe
# X-estudiante.pdf (build.sh --modo estudiante), se publica ese, con el nombre X.pdf, y no la versión del docente.
# Y además (estándar §10.7):
#   evaluation/recuperacion.md ← el banco de recuperación de la sesión, sin claves
#                                 (`alineamiento.py banco CURSO sNN --estudiante`), si hay recuperacion.yml
#   practice/mazo.tsv          ← el mismo banco como mazo para Anki, con la respuesta al reverso, para repasar fuera
#                                 de clase (`alineamiento.py mazo CURSO sNN`), si hay recuperacion.yml; el aula lo enlaza
#   practice/cornell.md        ← la hoja Cornell para la web (templates/report/cornell/), si el curso declara alineamiento
#
# --simular : dice qué publicaría y no escribe ni etiqueta nada (regla 3 del ecosistema: simular antes de aplicar).
# Congelar = etiquetar: se crea el tag `dictado/<clave>/<sesion>` en el repo docencia/ sobre el commit
# actual de las fuentes (no se copia nada versionado). --refrescar re-publica y mueve el tag.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

usage() { sed -n '2,30p' "${BASH_SOURCE[0]}"; exit 1; }
REFRESCAR=0; SIMULAR=0; POS=()
for a in "$@"; do
  case "$a" in
    --refrescar) REFRESCAR=1 ;;
    --simular)   SIMULAR=1 ;;
    -*)          usage ;;
    *)           POS+=("$a") ;;
  esac
done
[[ ${#POS[@]} -eq 3 ]] || usage
DICT="$(dictado_dir "${POS[0]}")" || die "No es un dictado (falta dictado.yml): ${POS[0]}"
COURSE="$(course_dir "${POS[1]}")" || die "No es un curso: ${POS[1]}"
NN="${POS[2]}"
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
ALINEADO="$(python3 -c 'import sys, yaml; print("1" if (yaml.safe_load(open(sys.argv[1])) or {}).get("alineamiento") else "")' "$COURSE/curso.yml")"
MOD="$DICT/publicacion/$WEB"
if [[ -e "$MOD" && "$REFRESCAR" == 0 && "$SIMULAR" == 0 ]]; then
  die "Ya publicado: $MOD (añade --refrescar para re-publicar)"
fi

# --- el plan: «subcarpeta<TAB>origen<TAB>nombre publicado» (los orígenes banco: y cornell: se generan o copian) ---
PLAN=()
while IFS= read -r f; do
  b="$(basename "$f")"; bl="${b,,}"
  case "$bl" in
    *-claves.pdf|*-soluciones.pdf|*-docente.pdf) continue ;;   # versiones del docente: nunca al estudiante
  esac
  nombre="$b"
  if [[ "$bl" == *-estudiante.pdf ]]; then
    nombre="${b%-estudiante.pdf}.pdf"; bl="${nombre,,}"
  elif [[ "$bl" == *.pdf && -f "${f%.pdf}-estudiante.pdf" ]]; then
    continue                                                  # hay versión del estudiante: va esa
  fi
  case "$bl" in
    evaluacion*|quiz*|rubrica*|examen*)          sub=evaluation ;;
    tarea*|homework*|consigna*)                  sub=homework ;;
    practica*|plantilla*|portada*|taller*)       sub=practice ;;
    *.pdf)                                       sub=slides ;;
    *)                                           sub=practice ;;
  esac
  PLAN+=("$sub"$'\t'"$f"$'\t'"$nombre")
done < <(find "$SES" -maxdepth 1 -type f \( -iname "*.pdf" -o -iname "*.odt" -o -iname "*.ods" -o -iname "*.odp" \
          -o -iname "*.docx" -o -iname "*.xlsx" -o -iname "*.pptx" -o -iname "*.csv" -o -iname "*.zip" \
          -o -iname "plantilla*.md" \) 2>/dev/null | sort)
[[ -f "$SES/recuperacion.yml" ]] && PLAN+=("evaluation"$'\t'"banco:$SNAME"$'\t'"recuperacion.md")
[[ -f "$SES/recuperacion.yml" ]] && PLAN+=("practice"$'\t'"mazo:$SNAME"$'\t'"mazo.tsv")
[[ -n "$ALINEADO" && -f "$FW_DIR/templates/report/cornell/cornell.md" ]] \
  && PLAN+=("practice"$'\t'"cornell:$FW_DIR/templates/report/cornell/cornell.md"$'\t'"cornell.md")

if [[ "$SIMULAR" == 1 ]]; then
  info "Simulación: $CSLUG/$SNAME → $MOD$([[ -e "$MOD" ]] && echo ' (ya existe: se rehace solo con --refrescar)')"
  for item in "${PLAN[@]}"; do
    IFS=$'\t' read -r sub orig nombre <<<"$item"
    case "$orig" in
      banco:*)   desde="alineamiento.py banco $CSLUG $SNAME --estudiante (sin claves)" ;;
      mazo:*)    desde="alineamiento.py mazo $CSLUG ${SNAME:0:3} (mazo para Anki)" ;;
      cornell:*) desde="templates/report/cornell/cornell.md" ;;
      *)         desde="${orig#"$SES"/}" ;;
    esac
    echo "  publicaría $sub/$nombre  ← $desde"
  done
  [[ ${#PLAN[@]} -eq 0 ]] && warn "Nada que publicar: compila primero (build-session.sh, build.sh --modo estudiante)."
  echo "  y el tag dictado/$CLAVE/$SNAME en el repo del contenido. Sin --simular, lo hace."
  exit 0
fi

[[ -e "$MOD" ]] && rm -rf "$MOD"
mkdir -p "$MOD"     # las subcarpetas se crean solo si reciben archivos (ninguna carpeta vacía en docencia/, §4.2)
s=0; e=0; p=0; h=0
for item in "${PLAN[@]}"; do
  IFS=$'\t' read -r sub orig nombre <<<"$item"
  mkdir -p "$MOD/$sub"
  case "$orig" in
    banco:*)   python3 "$FW_DIR/scripts/alineamiento.py" banco "$COURSE" "$SNAME" --estudiante > "$MOD/$sub/$nombre" \
                 || die "No se pudo generar el banco de recuperación de $SNAME" ;;
    mazo:*)    python3 "$FW_DIR/scripts/alineamiento.py" mazo "$COURSE" "$SNAME" --salida "$MOD/$sub/$nombre" \
                 || die "No se pudo generar el mazo de repaso de $SNAME" ;;
    cornell:*) cp "${orig#cornell:}" "$MOD/$sub/$nombre" ;;
    *)         cp "$orig" "$MOD/$sub/$nombre" ;;
  esac
  case "$sub" in slides) s=$((s+1)) ;; evaluation) e=$((e+1)) ;; practice) p=$((p+1)) ;; homework) h=$((h+1)) ;; esac
done

cat > "$MOD/_PUBLICADO.md" <<EOT
---
tipo: doc
titulo: "Publicado — $CSLUG/$SNAME ($CLAVE)"
estado: hecho
---
<!-- GENERADO por docencia/scripts/publish-session.sh; producto no versionado (publicacion/ está en .gitignore) -->
# Publicado — $CSLUG/$SNAME  ($CLAVE → $WEB)

- **Fecha:** $(date +%F)
- **Fuente:** \`cursos/$CSLUG/03-sesiones/$SNAME/\` (artefacto: $(session_artifact "$SES")); tag \`dictado/$CLAVE/$SNAME\`.
- slides=$s · evaluation=$e · practice=$p · homework=$h (versión del estudiante: sin claves ni solucionarios)
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
