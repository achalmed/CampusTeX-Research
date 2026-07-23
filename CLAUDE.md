# CLAUDE.md

Guía para Claude Code (claude.ai/code) al trabajar en este repositorio.

## Qué es este repositorio

El **framework canónico del estándar `Academic_Class`** (todo en **español** —
mantener el contenido y las ediciones en español). Cumple tres funciones:

1. **Define el estándar** de organización de cursos universitarios (estructura,
   nomenclatura, anatomía de sesión). El spec completo está en `README.md`.
2. **Aloja lo compartido** que sirve a **todos** los `Academic_Class-*` del
   workspace: `_PLANTILLAS/` (esqueletos para copiar) y `_BIBLIOTECA/` (bancos).
3. **Produce los entregables LaTeX** de cada curso: **diapositivas** de clase
   (Beamer, en `03_SESIONES/`) y **evaluaciones** (exámenes/prácticas, en
   `04_EVALUACIONES/`, vía el módulo `evaluaciones/` — ver `evaluaciones/README.md`
   y `docs/evaluaciones.md`).

**Los cursos reales NO viven aquí.** Viven en `~/Documents/Academic_Class-<Area>/`
(p. ej. `Academic_Class-Metodologia-investigacion`), donde cada `Academic_Class` es
un contenedor de `course_NN_<slug>/`. Por eso el tooling de `scripts/` recibe la
**ruta del curso** como argumento.

No hay suite de tests. Verificación = `./scripts/validate.sh <curso>` (estructura)
+ compilar a PDF y mirarlo.

## El estándar (resumen; detalle en README.md)

- Un `Academic_Class-<Area>/` contiene `course_NN_<slug>/` directamente.
- Cada curso tiene **12 carpetas 00–11** + `README.md`:
  `00_ADMINISTRACION 01_PLANIFICACION 02_CONTENIDO 03_SESIONES 04_EVALUACIONES
  05_ESTUDIANTES 06_RECURSOS 07_MULTIMEDIA 08_INVESTIGACION 09_PUBLICACION
  10_ARCHIVO 11_SEMESTRES`.
- Cada sesión (`03_SESIONES/SNN_<slug>/`) tiene la anatomía
  `01_Antes 02_Clase 03_Actividad 04_Evaluacion 05_Despues 06_Recursos 07_Notas`
  + `metadata.yml` + `README.md`. **El deck (`.tex`/`.qmd`) va en `02_Clase/`.**
- `11_SEMESTRES/<AAAA-ciclo>/` = cada dictado (estudiantes, calificaciones, evidencias).

## Arquitectura del repo

- `config/course.yml` — valores por defecto del docente (identidad, logo, tema,
  compilador). YAML **plano**; los scripts lo parsean con grep/sed (no anidar).
- `scripts/` — automatización. La lógica compartida está en `scripts/lib/common.sh`
  (colores, `config_get`, `slugify`, `latex_engine`, `compile_tex`, y los helpers
  `is_course`/`session_dir`/`list_sessions`/`list_courses` que reciben rutas). Los
  scripts de entrada solo orquestan. Nuevos parámetros → `config/course.yml`.
- `_PLANTILLAS/` — esqueletos para copiar: `Plantilla_Curso` (00–11),
  `Plantilla_Sesion` (anatomía + plantillas con `{{PLACEHOLDERS}}`),
  `Plantilla_Periodo`, y plantillas de documento (`Plantilla_Examen/Practica/Rubrica/Caso/Lectura`).
- `_BIBLIOTECA/` — bancos compartidos (`Banco_*`) + `Bibliografia/course.bib`.
- `evaluaciones/` — sistema LaTeX de evaluaciones: **una sola clase**
  `evaluacion.cls` (todo el diseño) + `plantillas/` (12 tipos) + `muestras/`.
  Motor **pdfLaTeX** (2 pasadas por los totales del `.aux`), independiente del de
  las diapositivas. Los cambios de diseño van **solo** en `evaluacion.cls`.
- `assets/branding/` — logo institucional canónico.
- `docs/` — documentación del tooling (incl. `docs/evaluaciones.md`).

> Nota histórica: antes existían `course/` (extraído a
> `Academic_Class-Metodologia-investigacion/course_03`), `templates/` (consolidado
> en `_PLANTILLAS/`) y `bibliography/` (consolidado en `_BIBLIOTECA/Bibliografia/`).

## Comandos

```bash
# Scaffolding (copian desde _PLANTILLAS/ hacia un curso/Academic_Class)
./scripts/new-course.sh  <ACADEMIC_CLASS_DIR> NN "Título"          # curso 00–11
./scripts/new-session.sh <COURSE_DIR> NN "Título" [--quarto]        # sesión SNN_slug
./scripts/new-period.sh  <COURSE_DIR> <AAAA-ciclo>                  # dictado en 11_SEMESTRES

# Validación y resumen
./scripts/validate.sh <COURSE_DIR | ACADEMIC_CLASS_DIR>            # invariantes 00–11 (exit!=0 si error)
./scripts/stats.sh    <COURSE_DIR>                                # resumen por sesión

# Compilación de diapositivas (decks en 02_Clase/)
./scripts/build-session.sh <COURSE_DIR> NN
./scripts/build-course.sh  <COURSE_DIR> [--solo-sesiones]

# Evaluaciones (exámenes/prácticas en 04_EVALUACIONES/)
./scripts/new-evaluacion.sh  <COURSE_DIR> <tipo|01-12> "Título" [--fecha AAAAMMDD]
./scripts/build-evaluacion.sh <ARCHIVO.tex> --modo examen|claves|soluciones|todos

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
- **Reversibilidad**: los árboles `Academic_Class-*` **no** son repos Git; sus
  reorganizaciones dejan backup + `_ESTANDARIZACION/UNDO*.sh`. Este framework **sí**
  es Git (revertir con git).
- `*.sdr/` = metadatos de KOReader; ignorar.

## Pendiente

- Los decks del piloto `session_02`/`session_06` referencian imágenes no incluidas
  (rotura previa); se reconstruyen al usarlos, no se "arreglan" borrando contenido.
- Replicar el estándar a los otros 22 `Academic_Class-*` (usar `new-course.sh` +
  migración asistida como en el piloto).
