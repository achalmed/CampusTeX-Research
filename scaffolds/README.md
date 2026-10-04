---
tipo: readme
titulo: "scaffolds — esqueletos mínimos de curso, sesión y dictado"
estado: activo
---
# scaffolds/ — esqueletos mínimos de curso, sesión y dictado

Ya no hay árboles de carpetas que copiar: un curso, una sesión o un dictado nacen con **solo su registro** y el
artefacto del tipo; las carpetas se crean al primer uso (una carpeta vacía es error del validador: `docs/estandar-docencia.md` §2).

## Estructura

| Carpeta | Archivos | Lo usa |
|---|---|---|
| `curso/` | `curso.yml`, `README.md` | `new-course.sh SLUG "Título" [--tipo …]` |
| `sesion/` | `sesion.yml`, `guion.md`, `deck.tex` (Beamer autocontenido: `beamer` + `tema_beamer` de `config/course.yml`, no `academic-beamer`), `deck.qmd` (reveal.js) | `new-session.sh CURSO NN "Título" [--tipo …]` |
| `dictado/` | `dictado.yml` | `new-dictado.sh AAAA-ciclo INSTITUCION MATERIA "Título"` |

Los `{{PLACEHOLDERS}}` se rellenan desde `config/course.yml` y los argumentos del script.
