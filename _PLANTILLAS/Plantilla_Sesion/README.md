# Sesión {{NUMBER}}: {{TITLE}}

**Curso:** {{COURSE}} ({{CYCLE}})
**Docente:** {{TEACHER}} — {{INSTITUTION}}

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
./scripts/build-session.sh {{NUMBER}}
```
