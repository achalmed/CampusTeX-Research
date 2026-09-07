# CLAUDE.md

Guía para Claude Code (claude.ai/code) al trabajar en este repositorio.

## Qué es este repositorio

El **framework canónico del estándar `Academic_Class`** (todo en **español** —
mantener el contenido y las ediciones en español). Cumple tres funciones:

1. **Define el estándar** de organización de cursos universitarios (estructura,
   nomenclatura, anatomía de sesión). El spec completo está en `README.md`.
2. **Aloja lo compartido** que sirve a **todos** los `Academic_Class-*` del
   workspace: `scaffolds/` (esqueletos de carpetas) y `templates/` (documentos
   vacíos) para copiar, y `libraries/` + `bibliography/` (bancos y `.bib`).
3. **Produce los entregables LaTeX** de cada curso: **diapositivas** de clase
   (Beamer, en `03_SESIONES/`) y **evaluaciones** (exámenes/prácticas, en
   `04_EVALUACIONES/`, vía la clase `academic-exam` + `templates/exam/` — ver
   `docs/00-arquitectura.md`).

**Los cursos reales NO viven en el núcleo del framework.** Viven en las 23 áreas
`areas/Academic_Class-<Area>/` (p. ej. `areas/Academic_Class-Metodologia-investigacion`),
que desde 2026-09-06 son **submódulos git** de este repositorio (`.gitmodules`; cada
área conserva su propio repo e historial; las que aún no tienen remote usan la URL
relativa `../Academic_Class-<Area>.git`). Cada `Academic_Class` es un contenedor de
`course_NN_<slug>/`. El tooling de `scripts/` sigue recibiendo la **ruta del curso**
como argumento. Flujo: commit dentro del área → `git add areas/<area>` + commit aquí
(mueve el puntero). Clon nuevo: `git clone --recurse-submodules`.

No hay suite de tests. Verificación = `./scripts/validate.sh <curso>` (estructura)
+ compilar a PDF y mirarlo.

## El estándar (resumen; detalle en README.md)

- Un `Academic_Class-<Area>/` contiene `course_NN_<slug>/` directamente.
- Cada curso tiene **10 carpetas 00–09** + `README.md`:
  `00_ADMINISTRACION 01_PLANIFICACION 02_CONTENIDO 03_SESIONES 04_EVALUACIONES
  05_ESTUDIANTES 06_RECURSOS 07_MULTIMEDIA 08_INVESTIGACION 09_SEMESTRES`.
- Cada sesión (`03_SESIONES/SNN_<slug>/`) tiene la anatomía
  `01_Antes 02_Clase 03_Actividad 04_Evaluacion 05_Despues 06_Recursos 07_Notas`
  + `metadata.yml` + `README.md`. **El deck (`.tex`/`.qmd`) va en `02_Clase/`.**
- `09_SEMESTRES/<AAAA-ciclo>/` = cada dictado: registro privado (estudiantes,
  calificaciones, evidencias) **+ publicación** (MOOC por sesión, se congela poco a
  poco). Fusiona las antiguas `09_PUBLICACION`/`10_ARCHIVO`/`11_SEMESTRES`.

## Arquitectura del repo

- `config/course.yml` — valores por defecto del docente (identidad, logo, tema,
  compilador). YAML **plano**; los scripts lo parsean con grep/sed (no anidar).
- `scripts/` — automatización. La lógica compartida está en `scripts/lib/common.sh`
  (colores, `config_get`, `slugify`, `latex_engine`, `compile_tex`, y los helpers
  `is_course`/`session_dir`/`list_sessions`/`list_courses` que reciben rutas). Los
  scripts de entrada solo orquestan. Nuevos parámetros → `config/course.yml`.
**Plataforma editorial (rediseño 2026-07-23, ver `docs/00-arquitectura.md` — fuente de verdad arquitectónica). Motor LuaLaTeX exclusivo (migración 2026). Capas, cada una con responsabilidad única:**

- `styles/` — **identidad visual única** (`academic.sty` carga colores, fuentes
  fontspec Libertinus+Inconsolata, math, iconos, cajas, código, tablas, idioma).
  La cargan por igual las clases de documento **y** el tema Beamer → un examen y
  una diapositiva comparten diseño al carácter. **El color se cambia en un solo
  sitio, `config/palette.tex`; las tipografías, en `styles/academic-fonts.sty`.**
- `classes/` — clases delgadas que encapsulan el diseño: `academic-base` (núcleo
  `article`), `academic-exam` (evaluaciones, 3 modos, hereda base), `academic-report`
  (sílabo/calendario/nota-docente/rúbrica, hereda base), `academic-beamer` (beamer + tema).
- `themes/` — tema Beamer propio `beamer{,color,font,inner,outer}themeAcademic` (minimalista; consume `styles/`).
- `templates/` — documentos vacíos, **sin diseño** (`presentation/`, `exam/` 12 tipos, `report/`); solo `\documentclass{academic-*}` + contenido.
- `scaffolds/` — esqueletos de **carpetas** (no compilables): `course` (00–09), `session` (01_Antes…07_Notas), `period` (dictado: registro privado + publicación MOOC).
- `libraries/` — bancos compartidos (`Banco_*`); `bibliography/` — `.bib`.
- `assets/branding/` — logo canónico. `examples/` — ejemplos compilados. `config/` — `course.yml` (datos) + `palette.tex` (color); las tipografías viven en `styles/academic-fonts.sty`.
- `docs/` — documentación técnica (`00-arquitectura.md` es la canónica).

> Nota histórica: se retiraron `evaluaciones/` (→ `academic-exam` + `templates/exam/`),
> `_PLANTILLAS/` (→ `templates/` + `scaffolds/`) y `_BIBLIOTECA/` (→ `libraries/` +
> `bibliography/`) en el cutover del rediseño; el motor pasó de pdfLaTeX a XeLaTeX
> y, en la migración de 2026, a **LuaLaTeX** (único motor soportado).

## Comandos

```bash
# Scaffolds de carpetas (copian desde scaffolds/ hacia un curso/Academic_Class)
./scripts/new-course.sh  <ACADEMIC_CLASS_DIR> NN "Título"          # curso 00–09
./scripts/new-session.sh <COURSE_DIR> NN "Título" [--quarto]        # sesión SNN_slug
./scripts/new-period.sh  <COURSE_DIR> <AAAA-ciclo>                  # dictado en 09_SEMESTRES

# Documentos LaTeX (copian desde templates/ y compilan con LuaLaTeX)
./scripts/new-presentation.sh <COURSE_DIR> NN "Título" [--tipo clase]   # diapositivas → SNN/02_Clase (academic-beamer)
./scripts/new-evaluacion.sh   <COURSE_DIR> <tipo|01-12> "Título"        # examen → 04_EVALUACIONES (academic-exam)
./scripts/new-report.sh       <COURSE_DIR> <silabo|calendario|nota-docente|rubrica> "Título"  # academic-report
./scripts/build.sh <ARCHIVO.tex> [--modo examen|claves|soluciones|todos]  # compila cualquier .tex con LuaLaTeX

# Currículo único (F5.1): temario.yml es la fuente; README/esqueletos/web/skill/checklist se generan
./scripts/temario-generar.sh migrar   [--aplicar] [COURSE_DIR...]   # README + 02_CONTENIDO → temario.yml (solo cursos nuevos/heredados)
./scripts/temario-generar.sh generar  [--aplicar] [--que readme,esqueleto,web,skill,resumen] [COURSE_DIR...]
./scripts/temario-generar.sh verificar                              # exit!=0 si un README no coincide con su temario (lo corre el doctor)
python3 scripts/enlazar.py posts|simuladores|examenes [--aplicar]   # F5.3: posts→curso, modelos del laboratorio→tema, banco de exámenes→curso
python3 scripts/enlazar.py verificar                                # rutas de recursos/bancos y cursos de los posts (lo corre el doctor)

# Validación y resumen
./scripts/validate.sh <COURSE_DIR | ACADEMIC_CLASS_DIR>            # invariantes 00–09 (exit!=0 si error)
./scripts/stats.sh    <COURSE_DIR>                                # resumen por sesión

# Compilación de diapositivas (decks en 02_Clase/)
./scripts/build-session.sh <COURSE_DIR> NN
./scripts/build-course.sh  <COURSE_DIR> [--solo-sesiones]

# Publicación MOOC (publicar = congelar la sesión en el dictado) y web (F5.2)
./scripts/publish-session.sh <COURSE_DIR> NN <AAAA-ciclo> [--refrescar]  # → 09_SEMESTRES/<periodo>/publicacion/SNN/ (PDF + odt/ods/docx/xlsx…)
./scripts/publish-web.sh     <COURSE_DIR> <AAAA-ciclo> [--aplicar]       # dictado.yml → 04 index/cursos/<curso>/<edicion>/ por HARDLINK (simula sin --aplicar)

# Evaluaciones (exámenes/prácticas en 04_EVALUACIONES/)
./scripts/new-evaluacion.sh  <COURSE_DIR> <tipo|01-12> "Título" [--fecha AAAAMMDD]
./scripts/build.sh <ARCHIVO.tex> --modo examen|claves|soluciones|todos  # compila la evaluación

./scripts/clean.sh [--pdf] [DIR]                                  # DIR por defecto = framework
./scripts/doctor.sh                                              # chequeo de entorno

bash -n scripts/*.sh scripts/lib/*.sh                            # chequeo de sintaxis
```

`compile_tex` prefiere el compilador universal del workspace
(`~/Documents/scripts_for_latex/script_compilar_latex/main.sh`, autodetecta motor);
si no existe, usa el motor detectado por `latex_engine()` (comentario `%!TEX`, clase
`yaac-*`, `fontspec`) dos veces.

## Convenciones

- **Español** en todo. **Nombres de carpeta ASCII** (sin tildes) por portabilidad y
  scripts. **`.gitkeep`** en carpetas vacías.
- **Homogeneidad total**: al estandarizar se convierte todo al estándar (incluida la
  anatomía interna de sesiones); si un deck deja de compilar, se reconstruye.
- Los decks Beamer son **autocontenidos** (preámbulo propio + copia local del logo).
  Al mover un deck, mover su carpeta **completa** (los assets son hermanos del `.tex`).
- **Reversibilidad por git (todo)**: tanto este framework como los árboles
  `areas/Academic_Class-*` son repos Git (submódulos; se hace `git init` donde falte). La reversibilidad
  de cualquier reorganización es por git: commit del estado previo → migrar → commit.
  Ya no se usan backups + `_ESTANDARIZACION/UNDO*.sh`.
- `*.sdr/` = metadatos de KOReader; ignorar.

## Estado

- **Estándar replicado a las 23 áreas**: los **61/61** `course_*` de los
  `Academic_Class-*` cumplen el 00–09 (`00_ADMINISTRACION`…`09_SEMESTRES`). La
  réplica ya no está pendiente; para un curso nuevo, usar `new-course.sh`.
- Los decks del piloto `session_02`/`session_06` referencian imágenes no incluidas
  (rotura previa); se reconstruyen al usarlos, no se "arreglan" borrando contenido.

## El currículo: `temario.yml` (F5.1, 2026-09-06)

Cada `course_NN/` lleva un **`temario.yml`**: identidad del curso (`curso`, `titulo`,
`emoji`, `descripcion`, `area`, `rol: docente`, `nivel`, `semestre`, `prerrequisitos`,
`etiqueta`), enlaces (`web_slug` a `04 index/cursos/<slug>`, `dominio_fuat` al dominio
del learning-skill) y **`unidades[].temas[]`** (id, título, `archivo` en `02_CONTENIDO`,
`recursos[]` opcionales: apunte, simulador, libro por `calibre_id`, post, examen).
**Es la única fuente**: el `README.md` del curso, los esqueletos de `02_CONTENIDO`, la
sección «Contenidos / Sílabo» de la ficha web, `prompts/learning-skill/2 domains/_temarios/<dominio>.md`
y `05 tasks/temarios cursos (generado).md` se generan con `scripts/temario-generar.sh`.
Regla: **edita el temario, no las vistas**; el doctor avisa si un README se desfasó.
`migrar` solo se usa para un curso heredado sin temario (lee su README o sus carpetas).

## El dictado y la web: `dictado.yml` + hardlinks (F5.2, 2026-09-06)

Un dictado (`09_SEMESTRES/<periodo>/`) puede componerse de sesiones de **varios cursos** (Metodología
2026-I = monografías + seminario + APA). Su manifiesto `dictado.yml` lista `sesiones: [{orden, curso, sesion, web}]`
y el destino `web: {curso, edicion}`. Flujo: `publish-session.sh` congela cada sesión en `publicacion/SNN/`
→ `publish-web.sh` enlaza esos archivos **por hardlink** en `04 index/cursos/<curso>/<edicion>/<sesion>/`
(un solo inodo, dos canales; la web nunca tiene copias) y crea `index.qmd`/`_links.md` solo si faltan.
Regla D5: **el framework es la fuente**; lo que aparece en la web sale de un módulo publicado. El doctor
avisa si un dictado tiene copias o huérfanos en la web. Las fichas web sin curso ni ediciones llevan `draft: true`.

## Ecosistema de aprendizaje (contexto externo)

Las áreas contienen **solo docencia** (F5.0, 2026-09-06): los cursos que Edison toma y
sus **apuntes de estudio** viven en `01 notes/40-cursos-y-formacion/<curso>/`
(learning-skill, preset `apuntes_clase`) y enlazan al tema del curso docente en
`02_CONTENIDO`. El contrato entre piezas está en `~/Documents/prompts/ECOSISTEMA_APRENDIZAJE.md`;
si un cambio del estándar 00–09 afecta a los apuntes, pasa por su checklist de propagación.
