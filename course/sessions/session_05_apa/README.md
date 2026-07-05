# Sesión 05: Normas APA 7ma edición

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
./scripts/build-session.sh 05
```

## Nota: sesión con múltiples decks

`slides/` contiene **7 presentaciones independientes**: `slides.tex` (visión
general) más un deck por subtema en `01 introduccion/` … `06 referencias/`.
No son fragmentos `\input`: cada una compila por separado.
`build-session.sh 05` las compila todas.
