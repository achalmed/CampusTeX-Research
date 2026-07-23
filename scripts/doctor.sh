#!/usr/bin/env bash
# ============================================================
# doctor.sh — Diagnostica el entorno de trabajo
# ============================================================
# Uso:
#   ./scripts/doctor.sh
#
# Comprueba que estén disponibles las herramientas que el
# framework necesita y reporta versión o ausencia de cada una.
# No modifica nada.
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

check() {
  local cmd="$1" desc="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "$desc ($cmd): $("$cmd" --version 2>/dev/null | head -1)"
  else
    warn "$desc ($cmd): NO instalado"
  fi
}

echo "Diagnóstico del entorno — Academic_Class Framework"
echo "=================================================="
check git      "Control de versiones"
check lualatex "Motor LaTeX del framework — LuaLaTeX (fontspec + microtype)"
check quarto   "Quarto (decks RevealJS)"
# Motores alternativos: informativos. El framework es LuaLaTeX-only (2026).
check xelatex  "Motor alternativo XeLaTeX (no soportado)"
check pdflatex "Motor alternativo pdfLaTeX (no soportado)"

COMPILADOR="$(eval echo "$(config_get compilador)")"
if [[ -x "$COMPILADOR" ]]; then
  ok "Compilador universal del workspace: $COMPILADOR"
else
  warn "Compilador universal no encontrado en: $COMPILADOR"
  echo "     build-session.sh usará los motores LaTeX directamente."
fi

[[ -f "$CONFIG_FILE" ]] && ok "Configuración: config/course.yml" \
                        || error "Falta config/course.yml"
