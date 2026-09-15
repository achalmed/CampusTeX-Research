#!/usr/bin/env bash
# ============================================================
# validate.sh — Valida cursos y dictados del estándar (§4, M5 2026-09-15)
# ============================================================
# Uso:
#   ./scripts/validate.sh CURSO|DICTADO   # ruta o slug (docencia/cursos/<slug>, docencia/dictados/<clave>)
#   ./scripts/validate.sh --todos         # todos los cursos y dictados de docencia/
#
# Curso (docencia/cursos/<slug>/):
#   - curso.yml con id (= carpeta) · titulo · estado · tipo ∈ {asignatura, herramienta, nivelacion, taller}; README.md.
#   - Carpetas de primer nivel SOLO de la lista cerrada: 01-diseno 02-contenido 03-sesiones 04-evaluaciones 05-recursos.
#   - Ninguna carpeta vacía ni .gitkeep en todo el curso; nombres de carpeta de primer nivel y de sesión en kebab-case.
#   - Sesión (03-sesiones/sNN-<slug>/): sesion.yml con id (= carpeta) · titulo · tipo ∈ {clase, laboratorio, taller,
#     evaluacion} · estado; guion.md; `artefacto` declarado, existente y coherente con el tipo
#     (clase: .tex/.qmd · laboratorio: .ipynb/.do/.py/.r/.rmd/.html · taller: .ods/.xlsx/.xlsm · evaluacion: .tex).
#     Con `revisar:` en sesion.yml la incoherencia es aviso, no error.
#   - Binarios > 5 MB: aviso (regla §7.6: datos en 02 analysis, pesados fuera del repo).
# Dictado (docencia/dictados/<clave>/):
#   - dictado.yml con id (= carpeta) · periodo · institucion · estado; `legado: true` exime de sesiones.
#   - sesiones[]: cada {curso, sesion, web} apunta a un curso y una sesión existentes.
# Código de salida != 0 si hay errores (los [!!] no hacen fallar).
# ============================================================

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

[[ $# -ge 1 ]] || { sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 1; }

errors=0
err() { error "$*"; errors=$((errors + 1)); }

COURSE_DIRS="01-diseno 02-contenido 03-sesiones 04-evaluaciones 05-recursos"
TIPOS_CURSO="asignatura herramienta nivelacion taller"
TIPOS_SESION="clase laboratorio taller evaluacion"
in_list() { local x="$1"; shift; for y in "$@"; do [[ "$x" == "$y" ]] && return 0; done; return 1; }

ext_ok() {  # ext_ok TIPO EXTENSION
  case "$1" in
    clase)       in_list "$2" tex qmd ;;
    laboratorio) in_list "$2" ipynb do py r rmd html ;;
    taller)      in_list "$2" ods xlsx xlsm ;;
    evaluacion)  in_list "$2" tex ;;
    *) return 1 ;;
  esac
}

validate_session() {
  local course="$1" s="$2" name sname sy tipo id art ext
  name="$(basename "$course")"; sname="$(basename "$s")"; sy="$s/sesion.yml"
  [[ "$sname" =~ ^s[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$ ]] || err "$name/$sname: nombre de sesión fuera de sNN-<kebab>"
  [[ -f "$sy" ]] || { err "$name/$sname: falta sesion.yml"; return; }
  for k in id titulo tipo estado; do
    [[ -n "$(yaml_get "$sy" "$k")" ]] || err "$name/$sname: sesion.yml sin '$k'"
  done
  id="$(yaml_get "$sy" id)"; [[ -z "$id" || "$id" == "$sname" ]] || err "$name/$sname: id '$id' ≠ carpeta"
  tipo="$(yaml_get "$sy" tipo)"; in_list "$tipo" $TIPOS_SESION || err "$name/$sname: tipo '$tipo' no admitido ($TIPOS_SESION)"
  [[ -f "$s/guion.md" ]] || err "$name/$sname: falta guion.md"
  art="$(session_artifact "$s")"
  if [[ -z "$art" ]]; then err "$name/$sname: sesion.yml sin 'artefacto'"
  elif [[ ! -f "$s/$art" ]]; then err "$name/$sname: artefacto no existe: $art"
  else
    ext="${art##*.}"; ext="${ext,,}"
    if ! ext_ok "$tipo" "$ext"; then
      if [[ -n "$(yaml_get "$sy" revisar)" ]]; then warn "$name/$sname: artefacto .$ext no coincide con tipo '$tipo' (marcado revisar)"
      else err "$name/$sname: artefacto .$ext no coincide con tipo '$tipo'"; fi
    fi
  fi
}

validate_course() {
  local course="$1" name cy tipo id d
  name="$(basename "$course")"; cy="$course/curso.yml"
  info "Curso: $name"
  is_kebab "$name" || err "$name: nombre de curso fuera de kebab-case"
  [[ -f "$cy" ]] || { err "$name: falta curso.yml"; return; }
  [[ -f "$course/README.md" ]] || err "$name: falta README.md"
  for k in id titulo estado tipo; do
    [[ -n "$(yaml_get "$cy" "$k")" ]] || err "$name: curso.yml sin '$k'"
  done
  id="$(yaml_get "$cy" id)"; [[ -z "$id" || "$id" == "$name" ]] || err "$name: id '$id' ≠ carpeta"
  tipo="$(yaml_get "$cy" tipo)"; in_list "$tipo" $TIPOS_CURSO || err "$name: tipo '$tipo' no admitido ($TIPOS_CURSO)"
  while IFS= read -r d; do
    in_list "$(basename "$d")" $COURSE_DIRS || err "$name: carpeta fuera de la lista cerrada: $(basename "$d")/"
  done < <(find "$course" -mindepth 1 -maxdepth 1 -type d)
  while IFS= read -r d; do err "$name: carpeta vacía: ${d#"$course"/}/"; done < <(find "$course" -type d -empty)
  while IFS= read -r d; do err "$name: .gitkeep prohibido: ${d#"$course"/}"; done < <(find "$course" -name .gitkeep)
  while IFS= read -r d; do warn "$name: binario > 5 MB (§7.6): ${d#"$course"/} ($(du -h "$d" | cut -f1))"; done \
    < <(find "$course" -type f -size +5M -not -path '*/publicacion/*')
  while IFS= read -r s; do [[ -n "$s" ]] && validate_session "$course" "$s"; done < <(list_sessions "$course")
  while IFS= read -r d; do
    [[ "$(basename "$d")" =~ ^s[0-9]{2}- ]] || err "$name: en 03-sesiones/ solo caben sesiones sNN-<slug>: $(basename "$d")/"
  done < <(find "$course/03-sesiones" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)
}

validate_dictado() {
  local d="$1" name dy
  name="$(basename "$d")"; dy="$d/dictado.yml"
  info "Dictado: $name"
  is_kebab "$name" || err "$name: clave de dictado fuera de kebab-case"
  for k in id periodo institucion estado; do
    [[ -n "$(yaml_get "$dy" "$k")" ]] || err "$name: dictado.yml sin '$k'"
  done
  [[ "$(yaml_get "$dy" id)" == "$name" ]] || err "$name: id ≠ carpeta"
  [[ "$(yaml_get "$dy" legado)" == "true" ]] && { info "$name: dictado legado (sin fuentes en el framework)"; return; }
  while IFS=';' read -r orden curso sesion web; do
    [[ -n "$curso" ]] || continue
    if ! course_dir "$curso" >/dev/null 2>&1; then err "$name: sesión $orden → curso inexistente '$curso'"; continue; fi
    [[ -d "$(course_dir "$curso")/03-sesiones/$sesion" ]] || err "$name: sesión $orden → '$curso/03-sesiones/$sesion' no existe"
    [[ -n "$web" ]] || err "$name: sesión $orden sin 'web'"
  done < <(python3 - "$dy" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1])) or {}
for s in d.get("sesiones") or []:
    print(f"{s.get('orden','')};{s.get('curso','')};{s.get('sesion','')};{s.get('web','')}")
PY
)
}

if [[ "$1" == "--todos" ]]; then
  while IFS= read -r c; do [[ -n "$c" ]] && validate_course "$c"; done < <(list_courses)
  while IFS= read -r d; do [[ -n "$d" ]] && validate_dictado "$d"; done < <(list_dictados)
elif c="$(course_dir "$1" 2>/dev/null)"; then validate_course "$c"
elif d="$(dictado_dir "$1" 2>/dev/null)"; then validate_dictado "$d"
else die "No es un curso (curso.yml) ni un dictado (dictado.yml): $1"
fi

echo
if [[ "$errors" -eq 0 ]]; then ok "Estructura válida. Sin errores."
else error "Validación con $errors error(es)."; exit 1; fi
