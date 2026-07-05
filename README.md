# CampusTeX-Research

Framework para diseñar, impartir y mantener cursos universitarios completos,
donde **cada sesión de clase es una unidad didáctica autosuficiente**:
diapositivas, plan de clase, guion del docente, prácticas, evaluaciones,
tareas, recursos y retrospectiva, todo en una sola carpeta con estructura
uniforme.

Contiene el curso **"Inteligencia Artificial, Sistemas de Citación y
Elaboración de Monografías"** (CAU — Universidad Nacional de San Cristóbal
de Huamanga, 2026-I), impartido por Edison Achalma, y sirve de plantilla
para cursos futuros.

## Inicio rápido

```bash
# Diagnóstico del entorno (LaTeX, Quarto, compilador)
./scripts/doctor.sh

# Ver el estado del curso
./scripts/stats.sh

# Crear una sesión nueva
./scripts/new-session.sh 07 "Marco Teórico"

# Compilar una sesión / todo el curso
./scripts/build-session.sh 02
./scripts/build-course.sh

# Validar la estructura
./scripts/validate.sh
```

## Estructura

```
config/course.yml     ← configuración central (curso, docente, logo, estilo)
templates/            ← plantillas de sesión y documentos (quiz, rúbrica…)
scripts/              ← automatización (crear, compilar, validar, limpiar)
docs/                 ← documentación del framework
assets/branding/      ← logo institucional canónico
bibliography/         ← BibTeX compartido del curso
course/
├── syllabus/         ← syllabus oficial (md + tex + pdf)
├── calendar/         ← calendario del semestre
├── evaluation/       ← sistema de evaluación global
├── policies/         ← lineamientos de trabajo
├── topics/           ← banco de temas de investigación
└── sessions/
    ├── session_01_la_monografia/
    ├── session_02_estructura/
    ├── session_03_busqueda_de_informacion/
    ├── session_04_redaccion/          ← única sesión en Quarto (excepción)
    ├── session_05_apa/                ← 7 decks independientes
    └── session_06_inteligencia_artificial/
```

Cada sesión sigue la misma anatomía (ver `templates/session/README.md`):
`metadata.yml` (ficha técnica) · `slides/` · `teaching/` (plan de clase,
guion, retrospectiva) · `practice/` · `evaluation/` · `homework/` ·
`resources/` · `archive/`.

## Formatos

- **LaTeX Beamer** es el formato estándar de las diapositivas (motor
  autodetectado: pdflatex/xelatex/lualatex).
- **Sesión 4 es la excepción**: fuente Quarto RevealJS (`index.qmd`); se
  mantiene en Quarto deliberadamente y `build-session.sh` la renderiza con
  `quarto render`.

## Documentación

| Documento | Contenido |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Diseño del framework y decisiones |
| [docs/workflow.md](docs/workflow.md) | Flujo semestral completo |
| [docs/session-creation.md](docs/session-creation.md) | Cómo crear y preparar una sesión |
| [docs/teaching-guide.md](docs/teaching-guide.md) | Manual de uso para docentes |
| [docs/developer-guide.md](docs/developer-guide.md) | Manual técnico |
| [docs/automation.md](docs/automation.md) | Referencia de scripts |
| [docs/templates.md](docs/templates.md) | Referencia de plantillas |
