---
tipo: estado
estado: activo
actualizado: 2026-11-18
---
# estado.md — docencia (repo `Academic_Class_Framework`, remoto `CampusTeX-Research`)

Lo primero que se lee y lo último que se escribe en cada sesión (regla 10 de la guía raíz). Lo decidido vive en
`docs/decisiones.md`; lo pendiente, aquí, en §Por hacer, con fecha y dueño. El contenido docente lleva su propio
estado en `docencia/estado.md`; `registro/` es sensible y no se describe aquí.

## Hecho

| fecha | qué | dónde se ve |
|---|---|---|
| 2026-10-06 | ola 5, fase A (agente «docencia»): D1–D4, un commit por ítem | la bitácora de abajo; `meta/programa/06-olas/ola-05-reingenieria.md` §1 |

Bitácora de la ola 5 (etiqueta `antes-ola-05-2026-10-06` en este repo y en `docencia`):

- 2026-10-06 · D1 · `estado.md` aquí y en `docencia`; los pendientes de `docs/decisiones.md` pasan a §Por hacer y la sección sale de decisiones.md.
- 2026-10-06 · D2 · (en `docencia`) los scripts de los exámenes y `code_sesion_02.r` sin rutas absolutas: `NOTES_DIR` de `core/env` o la carpeta del script, con «Falta el dato» donde el origen ya no existe.
- 2026-10-06 · D3 · (en `docencia`) los dos `slides.tex` pdflatex/xelatex pasan a LuaLaTeX y compilan; `yaac-xelatex.cls` retirado. `README.md` y `CLAUDE.md` ya no dicen que haya decks que pidan XeLaTeX.
- 2026-10-06 · D4 · `simuladores/macro/modelos/nivel_12/_datos_bcrp.py` y `simuladores/CLAUDE.md` usan `DATAFW_DIR`, no `ANALYSIS_DIR` (el lector resuelve `datafw/data/raw/bcrp` y `metodos/series/lectores.py`); en `docencia`, los tres exámenes de econometría II. `grep` de los tres alias = 0 en el código de ambos repos (quedan en la prosa de §Futuro).
- 2026-11-18 · F10 · Estándar §10: `scripts/alineamiento.py` (matriz de alineamiento verificada, rúbricas, bancos de recuperación, política de IA, sesión activa, prueba antes y después) en `validate.sh`; aplicado a `econometria-i` (s01 a s03 con la ENAHO, réplica 6 de 6 al decimal del INEI); plantillas `cornell`, `ronda-de-pares` y `prueba-de-comprension`; en `seminario-de-investigacion`, la guía de tesis UNSCH y tres talleres.
- 2026-11-18 · F10c · El aula (`web/_aula`) muestra en la página del curso los resultados con su evidencia, la evaluación con su uso de IA, las rúbricas y el banco de cada sesión sin claves (commit local en `web`, sin empujar); `alineamiento.py mazo` exporta los bancos como mazo para Anki (TSV o CSV) y `publish-session.sh` lo publica en `practice/mazo.tsv`; hojas del estudiante de s01 y s02 de `econometria-i` (`practica-laboratorio.tex`, `--modo estudiante`); la tabla de evaluación del sílabo deja de flotar.
- 2026-11-18 · F10b · Las rúbricas de `econometria-i` cumplen `escritura/config/entrega/rubrica.schema.yml` (validadas con su `rubrica.py` en `alineamiento.py verificar`; el resultado de cada criterio, en `curso.yml` → `alineamiento.rubricas`; nota vigesimal derivada); la política de IA entra en la plantilla del sílabo (`01-diseno/politica-ia.tex`); `publish-session.sh --simular` y la versión del estudiante (`build.sh --modo estudiante`, entorno `paradocente`) con banco sin claves, hoja Cornell y `plantilla*.md`; dictado `2026-ii-unsch-econometria` en borrador (s01 a s03).

## En curso

nada en curso

## Por hacer

- 2026-10-20 · dueño: autor · Plataforma educativa, fase 5: escribir las lecciones que hoy son solo título (series de econometría I–II, MATLAB, Power BI y R 02–07 en los pubs; 0 palabras): sus temas ya existen en `curso.yml` (C1).
- 2026-10-20 · dueño: autor · Decidir si las lecciones de Python de numerus-scriptum se publican con salidas de código (`web/_pubs/numerus-scriptum/python/_metadata.yml`: `execute.enabled: false`; con `freeze` se ejecutarían una vez).
- 2026-10-20 · dueño: director · Fase 5, generador `curso.yml` → pub (`web/_aula`): llevar las notas de `python/02-contenido` a numerus-scriptum (y renombrarlas a la numeración nueva en el mismo paso, no antes); retirar los posts marcados «revisar» por duplicado en `contenido/migracion/mapa-lecciones.csv`.
- 2026-10-04 · dueño: el autor · ¿El framework publicará versiones (etiquetas o releases que alguien consuma)? Si sí, vuelve `CHANGELOG.md` con SemVer.
- 2026-10-04 · dueño: el autor · `scripts/lib/common.sh` (`INBOX_DIR`) y `scripts/doctor.sh` siguen tratando la bandeja `_inbox` de `docencia`, ya retirada.
- 2026-10-20 · dueño: director · los `archivo:` de los recursos `{tipo: simulador}` de ocho `curso.yml` (29 rutas) aún dicen `docencia/simuladores/…`: pasarlos a `simuladores/…` y regenerar los README (`temario-generar.sh`); mientras, `enlazar.py` los traduce (`RUTA_VIEJA_LAB`). Los dos pendientes de la campaña SIMULADORES pasaron a `simuladores/estado.md`.
- 2026-10-04 · dueño: el autor · `scripts/new-evaluacion.sh` escribe las siglas `lab`, `eo` y `tar` (laboratorio, examen oral, tarea) donde `docs/estandar-evaluaciones.md` §2 fija `lb`, `or` y `ta`, y solo crea las doce plantillas de `templates/exam/`: alinear el script con la tabla.
- 2026-10-04 · dueño: el autor · `scaffolds/sesion/deck.tex` (el deck que crea `new-session.sh --tipo clase`) es un Beamer autocontenido con `\usetheme` de `config/course.yml` (`tema_beamer`), no `academic-beamer`: decidir si el scaffold pasa a la clase del framework.
- 2026-11-18 · dueño: autor · Empujar `web` (el commit local de `_aula` con la página del curso del estándar §10; empujar dispara Netlify) y, cuando el dictado `2026-ii-unsch-econometria` se confirme, publicar sus sesiones (`publish-session.sh`, sin `--simular`) para que el aula enlace la hoja del laboratorio y el mazo de cada una.
- 2026-11-18 · dueño: autor · Decidir si se publican el banco y el mazo (con la respuesta al reverso) aunque la prueba escrita de la unidad (`ev-prueba`) y la prueba antes y después reusan esas preguntas (`docs/decisiones.md`, «el repaso fuera de clase es un mazo»): si no, separar en `recuperacion.yml` las preguntas reservadas a las pruebas.
- 2026-11-18 · dueño: autor · Dictar la unidad aplicada de `econometria-i` (s01 a s03), tomar la prueba antes y después (`alineamiento.py pre-post`) y anotar los resultados por pregunta en `registro/` (C10.6); con ellos, revisar las distancias del repaso (1, 2, 4, 8).
- 2026-11-18 · dueño: autor · Alinear el resto del temario de `econometria-i` (unidades 1 a 4) a medida que se escriban sus sesiones, y declarar `alineamiento` en `seminario-de-investigacion`.
- 2026-11-18 · dueño: autor · Taller de reescritura (`seminario-de-investigacion/05-recursos/talleres/reescritura/`): sustituir los párrafos construidos por párrafos reales anonimizados de tesis (la norma los pide reales).

## Futuro

- Fase B de la ola 5 (director): el submódulo `docencia` pasa a `contenido` y los alias `ANALYSIS_DIR`, `SCRIPTS_CALIBRE` y `SCRIPTS_FUENTES` salen de `core/env`; fase C: `docencia` pasa a `docencia` (`meta/programa/06-olas/ola-05-reingenieria.md` §2 y §3).
