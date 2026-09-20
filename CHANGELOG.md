---
tipo: changelog
estado: activo
---
# CHANGELOG — `Academic_Class_Framework` y `Academic_Class`

Línea de tiempo única de las decisiones fechadas del framework y de su contenido, hasta ahora
repartidas entre `CLAUDE.md`, `docs/arquitectura.md`, `docs/estandar-evaluaciones.md` y
`meta/reparaciones/`. Formato: fecha ISO · sello de fase · qué cambió. El detalle vive en
`docs/historial/` y en la bitácora de cada fase (`meta/reparaciones/<fase>/`, con `UNDO.sh`).

El repo no declara versión semántica: la referencia son la fecha y el sello de fase.

## 2026-09-20 — DOC4 · la documentación del framework

- `CLAUDE.md` reducido a ≤ 150 líneas y sin bitácora: el bloque «Estado» de R9–R13 pasa a
  `docs/historial/2026-09-17-cierre-r9-r13.md` con las cifras reales (52 cursos, 410 archivos en
  `_inbox`, ledger `docencia/migracion/estado-examenes.csv`).
- `docs/` renumerado a kebab-case: `arquitectura.md`, `estandar-docencia.md`,
  `estandar-evaluaciones.md`; `DIAGNOSTICO_AREAS_2026-09.md` y la migración a LuaLaTeX a
  `docs/historial/`. Índice `docs/README.md` generado por `core/docs.py`.
- El estándar se cuenta **una vez**: `README.md` y `docencia/README.md` pasan a ser punteros.
- README nuevos de `scripts/`, `classes/`, `config/`, `styles/`, `templates/`, `themes/`;
  `assets/README.md` corregido; `docs/como-se-mantiene.md`, `CHANGELOG.md`, `LICENSE` y
  `registro/CLAUDE.md` nuevos.
- **D10**: `docencia/_inbox/` (410 archivos) y `registro/_legado/` (306 MB) siguen como temporales
  con plazo **2026-10-31**; hasta esa fecha el doctor no avisa por ellos.

## 2026-09-20 — Fase 6 del sistema de diseño · el color sale del repo

- `config/palette.tex` pasa a ser un **archivo generado** desde `sistema-editorial/temas/docencia.yml`
  y espejado aquí (`generador.py generar --aplicar --espejo`; `verificar` avisa si diverge). Los once
  nombres `academic*` conservan valores y modelo: ningún examen cambia y los tres de muestra
  recompilan con texto y página idénticos.
- `\academicbn` (opción `bn` / `salida=bn`) se extiende a `academic-beamer` y `academic-report`,
  además de `academic-exam`.
- Llega `simuladores/` desde `02 analysis` con su historia: motor común y las disciplinas `macro/` y
  `estadistica/`; doctrina propia en `simuladores/CLAUDE.md`.

## 2026-09-17 — R12 y R13 · el banco de evaluaciones

- **R12**: decisión del autor — las evaluaciones de otras universidades se transforman **como
  propias**, cambiando solo el membrete y declarando el origen ajeno y toda clave reconstruida.
  50 expedientes ajenos transformados; total 222 transformados y 16 `manual`.
- **R13**: las evaluaciones catalogadas en Calibre salen de la biblioteca: 947 ítems → 707 expedientes
  pendientes en 33 cursos; aparecen `historia-economica` e `investigacion-operativa` y el repo pasa de
  50 a **52 cursos**. Ficha `<tallo>.md` versionada, fuentes `*_fuente*.pdf` fuera de git.
  Ledger final: 222 transformados · 698 pendientes · 25 `manual`.
- Respaldo `meta/reparaciones/R13_calibre-evaluaciones_2026-09-17/calibre-evaluaciones.tar`, 787 MiB,
  solo en disco. Detalle en `docs/historial/2026-09-17-cierre-r9-r13.md`.

## 2026-09-15 — R9–R11 · piloto y migración masiva de los exámenes propios

- 172 expedientes propios transformados al sistema `.tex` (`academic-exam` + solucionario + `code/`).
- Del piloto salen dos reglas del framework: `mathtools` antes de `unicode-math` (R9) y la directriz
  visual de los bloques —sin caja ni iconos en texto, con caja en Beamer— (R10).
- `docs/estandar-evaluaciones.md` consolida en un solo documento lo que estaba en tres sitios
  (prompt maestro, estándar de docencia §2 y `new-evaluacion.sh`).

## 2026-09-15 — M0–M8 · la reorganización de `areas/` (`DIAGNOSTICO_AREAS_2026-09`)

Diagnóstico y plan en `docs/historial/DIAGNOSTICO_AREAS_2026-09.md`; bitácoras `R1`–`R8` en
`meta/reparaciones/`; tag `reorg-2026-09-done`.

- **M0** congelar y medir: tag `pre-reorg-2026-09` en los 23 repos y en el framework; manifiesto de
  6 098 rutas.
- **M1** sacar lo que no es contenido docente: 20 datasets (201 MB) a `02 analysis`, los trabajos de
  estudiantes a `registro/_legado/`, el material de inglés a `01 notes`, 198 archivos a
  `docencia/_inbox/`.
- **M2** consolidar los 23 repos `Academic_Class-*` en el submódulo único `docencia/` con su historial
  (tags `<área>/pre-reorg-2026-09`); purga de blobs de estudiantes y > 50 MB; `.git` de 1,0 GB → 601 MB.
- **M3–M4** renombrado al estándar actual y `curso.yml` como sucesor de `temario.yml`; mapas archivo a
  archivo en `docencia/migracion/historico/`.
- **M5** los scaffolds dejan de ser árboles de carpetas y pasan a ser **registros mínimos**; `CURSO` y
  `DICTADO` aceptan slug o ruta; `new-period.sh` retirado; los dictados viven en `docencia/dictados/`.
- **M6** reescritura de referencias. **M7** el tema Beamer pasa a minúsculas (`\usetheme{academic}`);
  67 sesiones y 54 cursos al registro §7 de la normativa; 1 954 apuntes a kebab con frontmatter.
- **M8** el estándar 00–09 queda sustituido en `README.md`, `CLAUDE.md` y `docs/`.
- Remotos: `docencia/` → `achalmed/Academic_Class`; framework → `achalmed/CampusTeX-Research`.

## 2026-09-06 — F5.0–F5.4 · el currículo único y el ecosistema de aprendizaje

- **F5.0** separación de roles: los cursos que el autor *toma* y sus apuntes salen a
  `01 notes/40-cursos-y-formacion/`; aquí queda solo docencia propia.
- **F5.1** `temario.py` + `temario-generar.sh`: el currículo vive una sola vez en el registro del
  curso y de ahí se generan README, ficha web, temario del learning-skill y checklist.
- **F5.2** publicación framework → web **por hardlink**: `publish-session.sh` congela (tag) y
  `publish-web.sh` enlaza en `04 index/cursos/`; la web nunca tiene copias.
- **F5.3** `enlazar.py`: posts, modelos del laboratorio y bancos de exámenes como recursos del tema.
- **F5.4** el material bibliográfico externo deja de vivir en `05-recursos` y se cita por
  `calibre_id` desde `curso.yml.bibliografia`.
- **F5a** (mismo día, luego revertida por M2): las 23 áreas pasaron a submódulos del framework.

## 2026-07-23 — la migración a LuaLaTeX

- Motor único soportado: **LuaLaTeX** (antes pdfLaTeX y luego XeLaTeX). La migración preserva la
  apariencia —mismo número de páginas— y hace efectiva la expansión de microtype que el diseño ya
  prometía y XeLaTeX ignoraba. Registro cambio a cambio en
  `docs/historial/2026-07-23-migracion-lualatex.md`.
- Rediseño integral de la plataforma editorial (`docs/arquitectura.md`): se retiran `evaluaciones/`
  (→ `academic-exam` + `templates/exam/`), `_PLANTILLAS/` (→ `templates/` + `scaffolds/`) y
  `_BIBLIOTECA/` (→ `bibliography/`).
