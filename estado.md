---
tipo: estado
estado: activo
actualizado: 2026-10-06
---
# estado.md — 10 Class (repo `Academic_Class_Framework`, remoto `CampusTeX-Research`)

Lo primero que se lee y lo último que se escribe en cada sesión (regla 10 de la guía raíz). Lo decidido vive en
`docs/decisiones.md`; lo pendiente, aquí, en §Por hacer, con fecha y dueño. El contenido docente lleva su propio
estado en `docencia/estado.md`; `registro/` es sensible y no se describe aquí.

## Hecho

| fecha | qué | dónde se ve |
|---|---|---|
| 2026-10-06 | ola 5, fase A (agente «docencia»): D1–D4, un commit por ítem | la bitácora de abajo; `meta/programa/06-olas/ola-05-reingenieria.md` §1 |

Bitácora de la ola 5 (etiqueta `antes-ola-05-2026-10-06` en este repo y en `docencia`):

- 2026-10-06 · D1 · `estado.md` aquí y en `docencia`; los pendientes de `docs/decisiones.md` pasan a §Por hacer y la sección sale de decisiones.md.

## En curso

nada en curso

## Por hacer

- 2026-10-04 · dueño: el autor · ¿El framework publicará versiones (etiquetas o releases que alguien consuma)? Si sí, vuelve `CHANGELOG.md` con SemVer.
- 2026-10-04 · dueño: el autor · `scripts/temario.py`, `enlazar.py` y `publicar-web.py` derivan `~/Documents` como carpeta padre del repo y `config/course.yml` (`compilador:`) escribe `$HOME/Documents/...`: pasar por `core/env.py`.
- 2026-10-04 · dueño: el autor · `scripts/lib/common.sh` (`INBOX_DIR`) y `scripts/doctor.sh` siguen tratando la bandeja `_inbox` de `docencia`, ya retirada.
- 2026-10-04 · dueño: campaña SIMULADORES · `simuladores/macro/modelos/`: tres pendientes sin fecha (aviso A13).
- 2026-10-04 · dueño: campaña SIMULADORES · revisar la excepción de `simuladores/CLAUDE.md` al cerrar `DIAGNOSTICO_SIMULADORES_2026-10`.
- 2026-10-04 · dueño: el autor · `scripts/new-evaluacion.sh` escribe las siglas `lab`, `eo` y `tar` (laboratorio, examen oral, tarea) donde `docs/estandar-evaluaciones.md` §2 fija `lb`, `or` y `ta`, y solo crea las doce plantillas de `templates/exam/`: alinear el script con la tabla.
- 2026-10-04 · dueño: el autor · `scaffolds/sesion/deck.tex` (el deck que crea `new-session.sh --tipo clase`) es un Beamer autocontenido con `\usetheme` de `config/course.yml` (`tema_beamer`), no `academic-beamer`: decidir si el scaffold pasa a la clase del framework.

## Futuro

- Fase B de la ola 5 (director): el submódulo `docencia` pasa a `contenido` y los alias `ANALYSIS_DIR`, `SCRIPTS_CALIBRE` y `SCRIPTS_FUENTES` salen de `core/env`; fase C: `10 Class` pasa a `docencia` (`meta/programa/06-olas/ola-05-reingenieria.md` §2 y §3).
