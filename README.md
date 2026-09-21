---
tipo: readme
estado: activo
---
# 10 Class/ — el framework de docencia: estándar de contenido y plataforma editorial LuaLaTeX

Repo `Academic_Class_Framework` (remoto `achalmed/CampusTeX-Research`). El contenido docente no vive
aquí: vive en el submódulo `docencia/` (repo `Academic_Class`) y lo privado en `registro/`.

## Qué es

Este repositorio es dueño de **dos cosas** para la docencia de Edison Achalma B.Sc. Econ.:

1. **El estándar** de organización del contenido docente —curso, sesión, dictado, registro,
   nomenclatura—, escrito una sola vez en [`docs/estandar-docencia.md`](docs/estandar-docencia.md) y
   en [`docs/estandar-evaluaciones.md`](docs/estandar-evaluaciones.md), exigido por
   `scripts/validate.sh` y vigilado por `scripts/doctor.sh`. Lo cumplen hoy **52 cursos**,
   **67 sesiones tipadas** y **708 fichas de evaluación** en `docencia/`.
2. **La plataforma editorial LaTeX** con identidad visual única que produce todo el material
   docente: diapositivas, exámenes, sílabos, calendarios, notas de docente y rúbricas. Motor
   **LuaLaTeX exclusivo**; arquitectura en [`docs/arquitectura.md`](docs/arquitectura.md).

Principio rector: **el documento depende del framework, nunca al revés.** El diseño vive una sola vez
en `styles/` + `classes/`; cada documento solo *elige* su clase y *rellena* contenido. El color se
cambia en `sistema-editorial/temas/docencia.yml`, de donde se genera `config/palette.tex`, y re-tinta
exámenes, diapositivas y sílabos a la vez.

**Qué no es**: no es una colección de plantillas sueltas, no es un gestor de notas de estudio (eso es
`01 notes/40-cursos-y-formacion/` con el learning-skill) y no cubre tesis, monografías, ensayos ni
artículos (eso es `03 writing`, repo `Academic_Writing_Framework`).

## Uso

```bash
cd ~/Documents/10\ Class          # CURSO y DICTADO aceptan slug o ruta

# 1) Registros (solo el registro y el artefacto del tipo; sin árboles de carpetas)
./scripts/new-course.sh  econometria-i "Econometría I" --tipo asignatura --materia-web econometria
./scripts/new-session.sh econometria-i 07 "Series temporales" --tipo clase   # sesion.yml + guion.md + deck.tex
./scripts/new-dictado.sh 2026-ii unsch econometria "Econometría I · 2026-II" # dictado.yml + registro/<clave>/

# 2) Documentos LaTeX (plantillas de templates/, identidad única, LuaLaTeX)
./scripts/new-presentation.sh econometria-i 07 "Series temporales"           # deck academic-beamer
./scripts/new-evaluacion.sh   econometria-i examen-desarrollo "Parcial"      # → 04-evaluaciones/
./scripts/new-report.sh       econometria-i silabo "Sílabo 2026-II"          # → 01-diseno/

# 3) Compilar, validar, publicar
./scripts/build-session.sh econometria-i 07
./scripts/build.sh ARCHIVO.tex [--modo examen|claves|soluciones|todos]
./scripts/validate.sh --todos && ./scripts/doctor.sh
./scripts/temario-generar.sh generar --que readme --aplicar                  # vistas desde curso.yml
./scripts/publish-session.sh 2026-ii-unsch-econometria econometria-i 07      # tag + publicacion/
./scripts/publish-web.sh     2026-ii-unsch-econometria --aplicar             # hardlinks a 04 index/cursos
```

Cada script está descrito en [`scripts/README.md`](scripts/README.md).

## Estructura

| Carpeta | Qué es | Dueño / generador |
|---|---|---|
| `styles/` | identidad visual única (`academic.sty` + colores, fuentes, math, iconos, bloques, código, tablas) | este repo |
| `classes/` | clases delgadas: `academic-base` · `academic-exam` · `academic-report` · `academic-beamer` | este repo |
| `themes/` | tema Beamer propio `academic` (minúsculas desde M7); consume `styles/` | este repo |
| `config/` | `course.yml` (identidad del docente, YAML plano) · `palette.tex` **GENERADO** | `sistema-editorial/generador.py` |
| `templates/` | documentos vacíos, sin diseño: `exam/` (12 tipos) · `presentation/` (8) · `report/` (4) | este repo |
| `scaffolds/` | registros mínimos de curso, sesión y dictado (no árboles de carpetas) | este repo |
| `scripts/` | automatización: crear, compilar, validar, generar vistas, publicar | este repo |
| `assets/` | `branding/cau-logo.png`, el logo canónico | este repo |
| `bibliography/` | `course.bib` heredado; la bibliografía viva se cita por `calibre_id` (F5.4) | Calibre |
| `docs/` | documentación permanente e `historial/` | autor; `docs/README.md` lo genera `core/docs.py` |
| `simuladores/` | el laboratorio computacional (motor + `macro/` + `estadistica/`) | `simuladores/CLAUDE.md` |
| `docencia/` | **submódulo** (repo `Academic_Class`): `cursos/`, `dictados/`, `migracion/` | `docencia/README.md` |
| `registro/` | repo privado hermano, git-ignorado: estudiantes, calificaciones, evidencias | `registro/CLAUDE.md` |

## Documentación

| Documento | Para qué leerlo |
|---|---|
| [`docs/estandar-docencia.md`](docs/estandar-docencia.md) | **la fuente única** del estándar: curso, sesión, dictado, registro, nomenclatura |
| [`docs/estandar-evaluaciones.md`](docs/estandar-evaluaciones.md) | evaluaciones: 16 tipos, siglas, subcarpetas, expediente, `code/`, ficha |
| [`docs/arquitectura.md`](docs/arquitectura.md) | la plataforma editorial: capas, decisiones, flujo de un documento |
| [`docs/como-se-mantiene.md`](docs/como-se-mantiene.md) | ciclo de vida documental: quién actualiza qué cuando cambia el estándar |
| [`docs/README.md`](docs/README.md) | índice completo, generado desde el frontmatter de `docs/` |
| [`CHANGELOG.md`](CHANGELOG.md) | qué cambió y cuándo (R1–R13, M0–M8, F5.x, Fase 6) |
| [`CLAUDE.md`](CLAUDE.md) | reglas para el asistente y detalles que cuesta redescubrir |

## Límite honesto

- **No hay suite de tests.** La verificación es `validate.sh` + compilar y mirar el PDF + `doctor.sh`;
  lo que el validador no exige, no está garantizado.
- **Un solo motor, a propósito.** LuaLaTeX; no se soporta pdfLaTeX ni XeLaTeX, y un documento heredado
  que los pida se reconstruye, no se parchea.
- **El framework no versiona datos de estudiantes**: eso es `registro/`, ignorado desde aquí y sin
  remoto. Tampoco versiona los productos de publicación ni las fuentes PDF de los expedientes.
- **El legado sin clasificar se resolvió el 2026-09-20**: `docencia/_inbox/` (410 archivos) salió del repo al archivo del vault
  (`06 archives/2026-09-20-docencia-inbox/`) y `registro/_legado/` (306 MB, trabajos de estudiantes) se conserva como archivo
  cerrado del registro privado, no como temporal.
- **5 decks Beamer heredados no compilan** (falta la copia local de `cau-logo.png`, o piden XeLaTeX):
  es pendiente del docente y se reconstruyen al usarlos.
- **El color no se decide aquí**: `config/palette.tex` es un espejo generado por `sistema-editorial`;
  editarlo a mano se pierde en la siguiente generación.
