# Manual técnico para desarrolladores

## Stack

- **Bash** (scripts POSIX-ish con `set -euo pipefail`), sin dependencias
  más allá de coreutils + `iconv`.
- **LaTeX** (**lualatex**, motor único; migración 2026) — ver
  [architecture.md](architecture.md#compatibilidad).
- **Quarto** solo para la sesión 4.
- Configuración en **YAML plano** (`config/course.yml`), parseado con
  `grep`/`sed` — sin `yq` ni Python. Por eso: **no anidar** las claves
  marcadas `[script]`.

## Estructura del código

```
scripts/
├── lib/common.sh      ← TODO lo compartido: rutas, colores, config_get,
│                        session_dir, slugify, latex_engine, compile_tex
├── new-session.sh     ← scaffolding desde templates/session/
├── build-session.sh   ← compila una sesión (tex o qmd, autodetectado)
├── build-course.sh    ← admin docs + todas las sesiones
├── clean.sh           ← borra auxiliares LaTeX ([--pdf] también PDFs regenerables)
├── validate.sh        ← invariantes estructurales (CI-friendly, exit != 0)
├── doctor.sh          ← diagnóstico del entorno
└── stats.sh           ← resumen tabular del curso
```

Convención del workspace: la lógica compartida vive en `lib/`, los scripts
de entrada solo orquestan. Nuevos valores configurables van a
`config/course.yml`, nunca hardcodeados.

## Contratos importantes

- **`session_dir NN`** resuelve `course/sessions/session_NN_*`; la
  numeración de dos dígitos con guion bajo es API — no cambiar el patrón.
- **`compile_tex`** prefiere el compilador universal del workspace
  (clave `compilador:` en config, autodetecta motor y n.º de pasadas);
  fallback: motor de `latex_engine()` ejecutado 2 veces en el directorio
  del `.tex` (rutas relativas de imágenes dependen de esto).
- **`latex_engine`** (framework LuaLaTeX-only): honra un override explícito
  `%!TEX program = …` (para documentos legacy) y, en su defecto, usa
  **lualatex**. Se retiraron las heurísticas `yaac-*` y `fontspec → xelatex`.
- **Placeholders de plantillas**: `{{NUMBER}} {{TITLE}} {{SLUG}} {{DATE}}
  {{COURSE}} {{COURSE_SHORT}} {{CYCLE}} {{TEACHER}} {{EMAIL}}
  {{INSTITUTION}} {{UNIVERSITY}} {{THEME}} {{ASPECT}} {{DURATION}}
  {{MODALITY}} {{LEVEL}} {{FORMAT}}`. Si añades uno, actualiza el
  `render_template()` de `new-session.sh` y documenta en
  [templates.md](templates.md).

## Verificación

No hay suite de tests. El equivalente:

```bash
bash -n scripts/*.sh scripts/lib/*.sh   # sintaxis
./scripts/validate.sh                   # invariantes de estructura
./scripts/build-session.sh NN           # compilación real
```

Verifica cambios en plantillas creando una sesión desechable
(`new-session.sh 99 "Prueba"`), compilándola y borrándola.

## Reglas al modificar contenido migrado

- Los decks históricos son **autocontenidos**: no muevas imágenes fuera del
  directorio del `.tex` sin actualizar los `\includegraphics`.
- `session_04_redaccion/slides/` es un proyecto Quarto: `index.qmd` es la
  única fuente; `index.html`, `index.tex`, `index.pdf`, `index_files/` son
  generados.
- Carpetas internas con espacios (`05 citas/`, `logo unsch sigla vertical/`)
  se conservan por compatibilidad de rutas LaTeX: **citar siempre las rutas**
  en shell.
- `*.sdr/` (en `archive/` y junto a PDFs) es metadata de KOReader — ignorar.
- Migraciones siempre con `git mv`.
