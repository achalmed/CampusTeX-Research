# Sesión 04: Redacción de proyectos de investigación

**Curso:** Inteligencia Artificial, Sistemas de Citación y Elaboración de Monografías (2026-I)
**Docente:** Edison Achalma — Centro de Actualización Universitaria (CAU)

## Contenido de esta carpeta

| Carpeta / archivo | Propósito |
|---|---|
| `metadata.yml` | Ficha técnica de la sesión (fuente única de datos) |
| `slides/` | Diapositivas (fuente + PDF compilado) |
| `teaching/lesson_plan.md` | Plan de clase: objetivos, tiempos, actividades |
| `teaching/teacher_notes.md` | Guion del docente diapositiva por diapositiva |
| `teaching/retrospective.md` | Qué funcionó, errores comunes, mejoras |
| `practice/` | Material práctico para el estudiante (plantillas, guías) |
| `evaluation/` | Quiz, rúbricas, listas de cotejo |
| `homework/` | Trabajo domiciliario |
| `resources/` | Lecturas, enlaces (`links.md`), datasets |
| `archive/` | Versiones antiguas y material descartado |

## Compilar

```bash
./scripts/build-session.sh 04
```

## Nota: sesión en Quarto (excepción del curso)

Esta es la única sesión cuya fuente es **Quarto RevealJS** (`slides/index.qmd`),
no LaTeX. Se mantiene así deliberadamente. **Edita solo `index.qmd`**;
`index.html`, `index.tex`, `index.pdf` e `index_files/` son generados.
`build-session.sh 04` detecta el `.qmd` y ejecuta `quarto render` automáticamente.
