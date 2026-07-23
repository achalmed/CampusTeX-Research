# Referencia de scripts

Todos se ejecutan desde cualquier directorio (resuelven la raíz del repo
por sí mismos) y llevan su documentación en la cabecera del archivo.

## `new-session.sh NUM "TÍTULO" [--quarto]`

Crea `course/sessions/session_NUM_slug/` con la estructura canónica
completa, plantillas rellenadas desde `config/course.yml` y copia local
del logo. Con `--quarto` genera `slides.qmd` (RevealJS) en lugar de
`slides.tex` (Beamer). Falla si el número ya existe.

## `build-session.sh NUM`

Compila las diapositivas de una sesión:

- `slides/*.qmd` → `quarto render` (sesión 4).
- `slides/**/*.tex` → compila **todos** los `.tex` (hasta 2 niveles;
  soporta sesiones multi-deck como la 5). Motor autodetectado; usa el
  compilador universal del workspace si está disponible.

## `build-course.sh [--solo-sesiones]`

Compila los documentos administrativos (syllabus, topics, lineamientos)
y luego todas las sesiones. Continúa ante fallos y resume al final.
`--solo-sesiones` omite los administrativos.

## `validate.sh`

Comprueba la estructura: config con claves mínimas; por sesión:
`metadata.yml` (con campos obligatorios), `README.md`, subcarpetas
canónicas y fuente de diapositivas. PDFs ausentes son solo aviso.
Exit ≠ 0 si hay errores → usable en CI o hook pre-commit.

## `clean.sh [--pdf]`

Borra auxiliares LaTeX en todo el repo (`.aux .log .nav .snm .toc .out
.vrb .fls .fdb_latexmk .synctex.gz .bbl .blg .bcf .run.xml ...`).
Con `--pdf` borra también los PDF que tengan `.tex`/`.qmd` fuente al lado
(nunca los PDF sin fuente, como `temario_completo.pdf`).

## `doctor.sh`

Diagnóstico: git, **lualatex** (motor del framework), quarto, iconv, compilador
universal y config; además informa de xelatex/pdflatex como motores alternativos
no soportados. Solo informa, no modifica nada.

## `stats.sh`

Tabla por sesión: número, título (de `metadata.yml`), formato, cantidad de
fuentes, PDFs compilados y archivos de práctica.

## Scripts previstos y decisiones

Del diseño original se **omitieron deliberadamente** (KISS):

- `new-course.sh` — crear un curso = copiar el repo + editar
  `config/course.yml` ([workflow.md](workflow.md#reutilizar-el-curso-en-otro-semestre--crear-un-curso-similar)).
- `new-unit.sh` — las unidades son un campo de `metadata.yml` (`unidad:`),
  no una carpeta; con 6–20 sesiones una jerarquía extra solo estorba.
- `watch.sh` — usa `quarto preview` (sesión 4) o el modo watch del
  compilador universal para LaTeX.
- `export-pdf.sh` / `export-html.sh` — cubiertos por `build-session.sh`
  (el formato de salida lo define la fuente: `.tex` → PDF, `.qmd` → lo que
  declare su YAML).
- `build-all.sh` — es `build-course.sh`.
