# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **framework for preparing and maintaining complete university courses** (in **Spanish** — keep all content and edits in Spanish), currently containing the course *"Inteligencia Artificial, Sistemas de Citación y Elaboración de Monografías"* (CAU / Universidad Nacional de San Cristóbal de Huamanga, 2026-I, taught by Edison Achalma). Each class session is a self-contained didactic unit under `course/sessions/`. It is one of the `CampusTeX-*` sub-repos inside the `~/Documents` workspace (see the parent `~/Documents/CLAUDE.md`).

There is no test suite. Verification = `./scripts/validate.sh` (structure) + compiling to PDF and looking at it. Generated PDFs **are committed** as deliverables.

## Architecture

- `config/course.yml` — single source of truth for course identity (name, teacher, institution, logo, Beamer theme). Scripts parse it as **flat YAML** with grep/sed — do not nest the `[script]`-marked keys.
- `scripts/` — automation. Shared logic lives in `scripts/lib/common.sh` (config parsing, `session_dir`, `slugify`, `latex_engine`, `compile_tex`); entry scripts only orchestrate. New tunables go in `config/course.yml`, never hardcoded.
- `templates/session/` — scaffold consumed by `new-session.sh` (placeholders `{{TITLE}}`, `{{TEACHER}}`, … rendered with sed; if you add one, update `render_template()` in `new-session.sh`). `templates/documents/` — quiz/rubric/practice/case/reading templates copied by hand.
- `course/` — real content: `syllabus/`, `calendar/`, `evaluation/`, `policies/`, `topics/`, and `sessions/session_NN_slug/`.
- Full design rationale in `docs/architecture.md`; script reference in `docs/automation.md`.

Every session has the same anatomy: `metadata.yml` (ficha técnica; validated fields: numero, titulo, duracion_minutos, formato_slides, estado), `README.md`, `slides/`, `teaching/` (lesson_plan, teacher_notes, retrospective), `practice/`, `evaluation/`, `homework/`, `resources/`, `archive/`.

## Common commands

```bash
./scripts/new-session.sh 07 "Marco Teórico" [--quarto]  # scaffold a session
./scripts/build-session.sh 02                           # compile one session
./scripts/build-course.sh [--solo-sesiones]             # compile everything
./scripts/validate.sh                                   # structure invariants (exit != 0 on error)
./scripts/clean.sh [--pdf]                              # remove LaTeX aux files
./scripts/doctor.sh                                     # environment check
./scripts/stats.sh                                      # per-session overview
bash -n scripts/*.sh scripts/lib/*.sh                   # syntax-check scripts
```

`build-session.sh` prefers the workspace universal compiler (`~/Documents/scripts_for_latex/script_compilar_latex/main.sh`, auto-detects engine); fallback runs the engine detected by `latex_engine()` (magic comment `%!TEX`, `yaac-*` class, `fontspec`) twice.

## Formats and known quirks

- **LaTeX Beamer is the standard** slide format (aspectratio 169, Madrid theme, Spanish babel, tikz/tcolorbox, cau-logo watermark). Every deck is **self-contained**: own preamble + local copy of `cau-logo.png`. Don't move images out of a deck's directory, and don't introduce a shared preamble into historical decks.
- **`session_04_redaccion` is the one Quarto exception** (kept deliberately): source is `slides/index.qmd`; `index.html`, `index.tex`, `index.pdf`, `index_files/` are generated — edit only the `.qmd`. `build-session.sh 04` runs `quarto render`.
- **`session_05_apa`** contains 7 independent decks (master `slides.tex` + one per subfolder `01 introduccion/`…`06 referencias/`); they are separate documents, not `\input` fragments. `build-session.sh 05` compiles all.
- **Pre-existing build failures** (not regressions): `session_02` and `session_06` slides.tex reference images that were never committed (and session 6 uses emoji incompatible with pdflatex); their committed PDFs are the deliverables — don't "fix" by deleting content.
- Engine map: `course/syllabus/syllabus.tex` → lualatex (vendored `yaac-luatex.cls` + bundled fonts) · session 1 → xelatex · `course/topics/`, `course/policies/` → xe/lualatex (fontspec) · rest → pdflatex.
- Historical inner folders keep spaces in names (`05 citas/`, `logo unsch sigla vertical/`) to preserve LaTeX relative paths — always quote paths in shell.
- `*.sdr/` folders are KOReader reading metadata — ignore.
- Session folders follow `session_NN_slug` (two digits, ASCII slug); this pattern is API for the scripts. Rename only with `git mv`, keeping the pattern. All migrations use `git mv` to preserve history.
