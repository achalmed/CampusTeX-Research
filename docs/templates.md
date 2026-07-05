# Referencia de plantillas

## `templates/session/` — scaffold de sesión

Consumidas automáticamente por `new-session.sh` (no copiar a mano):

| Plantilla | Se convierte en |
|---|---|
| `metadata.yml` | `session_NN_*/metadata.yml` |
| `README.md` | `session_NN_*/README.md` |
| `lesson_plan.md` | `teaching/lesson_plan.md` |
| `teacher_notes.md` | `teaching/teacher_notes.md` |
| `retrospective.md` | `teaching/retrospective.md` |
| `links.md` | `resources/links.md` |
| `slides.tex` | `slides/slides.tex` (Beamer, estilo de la casa) |
| `slides.qmd` | `slides/slides.qmd` (solo con `--quarto`) |

Los placeholders `{{...}}` se rellenan desde `config/course.yml`
(lista completa en [developer-guide.md](developer-guide.md#contratos-importantes)).

## `templates/documents/` — documentos didácticos

Se copian a mano a la sesión que los necesite y se completan:

| Plantilla | Uso | Destino sugerido |
|---|---|---|
| `quiz.md` | Evaluación de salida / entrada | `evaluation/` |
| `rubric.md` | Rúbrica con descriptores y escala vigesimal | `evaluation/` |
| `practice_guide.md` | Guía práctica / laboratorio paso a paso | `practice/` |
| `case_study.md` | Caso de estudio con dinámica grupal | `practice/` |
| `reading_guide.md` | Guía de lectura dirigida | `resources/` |

## Modelos reales (mejor que cualquier plantilla)

Para calibrar tono y nivel de detalle, mira los materiales ya escritos:

- **Guion de docente completo:** `session_01_la_monografia/teaching/teacher_notes.md`
  y `session_03_busqueda_de_informacion/teaching/teacher_notes.md`.
- **Plan de clase con módulos y tiempos:** `session_04_redaccion/teaching/lesson_plan.md`.
- **Guion por diapositiva:** `session_05_apa/teaching/guion_05_citas.md`.
- **Especificación de diseño de una presentación:** `session_06_inteligencia_artificial/teaching/design_spec.md`.

## Modificar o añadir plantillas

1. Edita/crea el archivo en `templates/`.
2. Si es de `session/` y usa un placeholder nuevo, añádelo al
   `render_template()` de `scripts/new-session.sh`.
3. Prueba con una sesión desechable: `./scripts/new-session.sh 99 "Prueba"`,
   revisa el resultado y bórrala.
