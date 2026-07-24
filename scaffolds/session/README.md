# Sesión {{NUMBER}}: {{TITLE}}

**Curso:** {{COURSE}} ({{CYCLE}})
**Docente:** {{TEACHER}} — {{INSTITUTION}}

> Anatomía estándar de una sesión: `01_Antes` · `02_Clase` (el deck) · `03_Actividad`
> · `04_Evaluacion` · `05_Despues` · `06_Recursos` · `07_Notas`. Cada carpeta trae su
> propio `README.md`. Este esqueleto lo copia `new-session.sh` y rellena los
> `{{PLACEHOLDERS}}` con `config/course.yml`.

## Contenido de la sesión

| Carpeta / archivo | Propósito | Momento |
|---|---|---|
| `metadata.yml` | ficha técnica de la sesión (la leen `validate.sh`/`stats.sh`) | — |
| [`01_Antes/`](01_Antes/README.md) | plan de clase, preparación (`lesson_plan.md`) | antes |
| [`02_Clase/`](02_Clase/README.md) | **el deck** (`diapositivas.tex`/`.qmd`) + logo | durante |
| [`03_Actividad/`](03_Actividad/README.md) | actividad/práctica en clase | durante |
| [`04_Evaluacion/`](04_Evaluacion/README.md) | evaluación de salida breve de la sesión | durante/cierre |
| [`05_Despues/`](05_Despues/README.md) | tarea, cierre, refuerzo | después |
| [`06_Recursos/`](06_Recursos/README.md) | enlaces (`links.md`), datasets de la sesión | apoyo |
| [`07_Notas/`](07_Notas/README.md) | guion del docente, retrospectiva | apoyo |

## Nomenclatura de la carpeta de sesión

`S<NN>_<slug>` — `S01_introduccion`, `S06_referencias`. Dos dígitos; slug ASCII.

## Crear el deck y compilar

```bash
./scripts/new-presentation.sh <COURSE_DIR> {{NUMBER}} "{{TITLE}}" --tipo clase
./scripts/build-session.sh    <COURSE_DIR> {{NUMBER}}
```
