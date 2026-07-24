# 02_Clase — El deck de diapositivas (lo esencial de la sesión)

> El corazón de la sesión: las **diapositivas** que se proyectan en clase. `validate.sh`
> **exige** que exista aquí un deck (`.tex` o `.qmd`).

## Qué va aquí

- **`diapositivas.tex`** (Beamer, clase `academic-beamer`) — el deck por defecto; o
  **`slides.qmd`** (Quarto RevealJS) si la sesión se creó con `--quarto`.
- **`cau-logo.png`** — copia **local** del logo (el deck es **autocontenido**: al mover
  la sesión, su logo viaja con ella).
- Recursos que el deck incluye (imágenes propias de estas diapositivas).

## Cómo se crea y compila

```bash
./scripts/new-presentation.sh <COURSE_DIR> NN "Título" --tipo clase   # → 02_Clase/diapositivas.tex
./scripts/build-session.sh    <COURSE_DIR> NN                          # compila el deck (LuaLaTeX)
```

Tipos de presentación disponibles (`--tipo`): `clase`, `conferencia`, `seminario`,
`ponencia`, `workshop`, `defensa-tesis`, `institucional`, `masterclass`.

## Qué NO va aquí

- El examen/práctica de la sesión → `04_EVALUACIONES/` del curso (no la sesión).
- El plan de clase → [`01_Antes/`](../01_Antes/README.md).

## Ejemplo — cabecera de `diapositivas.tex`

```latex
\documentclass{academic-beamer}
\title{Introducción a APA}
\author{Edison Achalma B.Sc. Econ.}
\institute{Universidad Nacional de San Cristóbal de Huamanga}
\date{Semestre 2026-I}
\begin{document}
\maketitle
% … frames …
\end{document}
```

> Nota: el esqueleto trae `slides.tex` **y** `slides.qmd` como marcador; `new-session.sh`
> borra el que no corresponda al formato elegido y `new-presentation.sh` crea el
> `diapositivas.tex` definitivo.
