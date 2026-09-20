#!/usr/bin/env bash
# ============================================================
# doctor.sh — Diagnostica el entorno y la salud del contenido docente (M5)
# ============================================================
# Uso:
#   ./scripts/doctor.sh
#
# (1) Herramientas (git, lualatex, quarto, compilador universal, config).
# (2) docencia/: submódulo presente; validate.sh --todos; temario-generar.sh verificar; enlazar.py verificar;
#     _inbox/ (temporal con plazo, D10); binarios > 5 MB fuera de publicacion/; registro/ sin remote público.
# (3) Normativa de archivos: core/archivos.py validar "10 Class".
# No modifica nada. Código de salida 1 si hay errores.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

rc_total=0
check() {
  local cmd="$1" desc="$2"
  if command -v "$cmd" >/dev/null 2>&1; then ok "$desc ($cmd): $("$cmd" --version 2>/dev/null | head -1)"
  else warn "$desc ($cmd): NO instalado"; fi
}

echo "Diagnóstico del entorno — Academic_Class Framework"
echo "=================================================="
check git      "Control de versiones"
check lualatex "Motor LaTeX del framework — LuaLaTeX"
check quarto   "Quarto (decks RevealJS)"
COMPILADOR="$(eval echo "$(config_get compilador)")"
[[ -x "$COMPILADOR" ]] && ok "Compilador universal del workspace: $COMPILADOR" || warn "Compilador universal no encontrado en: $COMPILADOR"
[[ -f "$CONFIG_FILE" ]] && ok "Configuración: config/course.yml" || { error "Falta config/course.yml"; rc_total=1; }

echo
echo "Contenido docente — docencia/ (§4)"
if [[ -d "$CURSOS_DIR" ]]; then
  ok "docencia/: $(list_courses | wc -l) cursos · $(list_dictados | wc -l) dictados"
  if out="$("$FW_DIR/scripts/validate.sh" --todos 2>&1)"; then ok "validate.sh --todos: sin errores"
  else error "validate.sh --todos: $(echo "$out" | grep -c '\[ERROR\]') error(es) — ejecuta ./scripts/validate.sh --todos"; rc_total=1; fi
  if out="$("$FW_DIR/scripts/temario-generar.sh" verificar --quiet 2>&1)"; then ok "temario-generar.sh verificar: README al día"
  else error "temario-generar.sh verificar: README desfasados (generar --que readme --aplicar)"; rc_total=1; fi
  if out="$(python3 "$FW_DIR/scripts/enlazar.py" verificar 2>&1 | tail -1)"; then ok "enlazar.py verificar: $out"
  else error "enlazar.py verificar: $out"; rc_total=1; fi
  n_inbox="$(find "$INBOX_DIR" -type f ! -name README.md 2>/dev/null | wc -l)"
  # (DOC4/D10, 2026-09-20): _inbox/ y registro/_legado/ son temporales con plazo acordado; hasta esa fecha no se avisa (ruido crónico que ya no informa).
  PLAZO_TEMPORALES="2026-10-31"
  if [[ "$n_inbox" -eq 0 ]]; then ok "_inbox/: vacío"
  elif [[ "$(date +%F)" < "$PLAZO_TEMPORALES" ]]; then ok "_inbox/: $n_inbox archivos por clasificar — temporal con plazo $PLAZO_TEMPORALES (D10); nada se cita desde ahí"
  else warn "_inbox/: $n_inbox archivos por clasificar y el plazo $PLAZO_TEMPORALES ya venció (§7.11: nada se cita desde ahí)"; fi
  n_big="$(find "$CURSOS_DIR" -type f -size +5M -not -path '*/publicacion/*' 2>/dev/null | wc -l)"
  [[ "$n_big" -eq 0 ]] && ok "Binarios > 5 MB en cursos/: ninguno" || warn "Binarios > 5 MB en cursos/: $n_big (§7.6: datos a 02 analysis; pesados fuera del repo o LFS)"
else
  error "No existe $CURSOS_DIR (submódulo docencia/ sin inicializar: git submodule update --init)"; rc_total=1
fi
if [[ -d "$REGISTRO_DIR/.git" ]]; then
  if [[ -n "$(git -C "$REGISTRO_DIR" remote 2>/dev/null)" ]]; then
    error "registro/ tiene remote ($(git -C "$REGISTRO_DIR" remote -v | head -1)): datos de estudiantes, nunca a un remote público"; rc_total=1
  else ok "registro/: repo privado sin remote"; fi
else
  warn "registro/: no es un repo git (datos de estudiantes sin control de versiones)"
fi

# --- Normativa de archivos (meta/NORMATIVA_ARCHIVOS.md §11)
CORE_ENV="$FW_DIR/../core/env.sh"
if [[ -f "$CORE_ENV" ]]; then
  # shellcheck source=/dev/null
  source "$CORE_ENV"
  echo
  echo "Normativa de archivos — core/archivos.py validar \"10 Class\""
  rc=0
  python3 "$DOCS_ROOT/core/archivos.py" validar "$DOCS_ROOT/10 Class" --max 5 || rc=$?
  case $rc in
    0) ok "Normativa de archivos: sano" ;;
    1) warn "Normativa de archivos: avisos (ver arriba)" ;;
    *) error "Normativa de archivos: fallos (ver arriba)"; rc_total=1 ;;
  esac
else
  warn "core/env.sh no encontrado: no se valida la normativa de archivos"
fi
exit "$rc_total"
