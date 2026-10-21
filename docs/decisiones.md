---
tipo: decision
titulo: "Decisiones del framework de docencia"
estado: activo
---
# Decisiones del framework de docencia

Registro acumulativo por tema (`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §15.6): una entrada por decisión, con su
fecha y su porqué. Cubre el framework, su contenido (`docencia/`) y su registro privado (`registro/`).
Lo **decidido** no se vuelve a discutir sin anotar aquí por qué; lo abierto está en [`../estado.md`](../estado.md)
§Por hacer (el del contenido, en `docencia/estado.md`), con fecha y dueño. El detalle de cada fase cerrada está en
[`historial/`](historial/README.md) y en el asiento de `meta/docs/historial/progreso-2026.md`.

## Plataforma editorial

**Decidido (2026-07-23): un solo motor, LuaLaTeX.**
Antes convivían pdfLaTeX (exámenes, `evaluacion.cls`) y un Beamer multimotor: dos cadenas de
herramientas y dos identidades tipográficas. Con `fontspec`, `unicode-math` y Libertinus OpenType se
obtienen versalitas reales, números elzevirianos y `microtype` con protrusión **y** expansión (XeLaTeX
ignoraba la expansión). La migración conservó la paginación; el registro cambio a cambio está en
[`historial/2026-07-23-migracion-lualatex.md`](historial/2026-07-23-migracion-lualatex.md).

**Decidido (2026-07-23): rediseño en capas; la identidad vive en `styles/`, no en las clases.**
El diagnóstico de julio encontró diseño dentro de las plantillas, plantillas duplicadas
(una carpeta `_PLANTILLAS` y otra de plantillas dentro de `evaluaciones`, hoy retiradas) y ninguna capa de estilos compartida. Las
decisiones del rediseño, vigentes:

- **D1 · Identidad en `styles/`.** Beamer y `article` son clases base distintas y una no hereda de la
  otra; solo un paquete `.sty` agnóstico lo pueden cargar las dos, y así diapositivas y exámenes
  comparten colores, fuentes y bloques.
- **D2 · Herencia = compartir identidad.** `academic-exam` y `academic-report` heredan de
  `academic-base` por `\LoadClass` (las tres son `article`); `academic-beamer` carga `beamer` y comparte
  identidad cargando `styles/academic.sty` a través del tema.
- **D4 · `evaluacion.cls` → `academic-exam.cls`.** La clase de exámenes se reescribió sobre la base y
  conservó toda su funcionalidad (entornos `pregunta`/`solucion`/`opciones`, modos de salida, puntaje).
- **D5 · `templates/` único; `scaffolds/` aparte.** Una plantilla de documento es algo que se compila;
  un scaffold es el registro con el que nace un curso, una sesión o un dictado.
- **D6 · No duplicar `escritura`.** Tesis, monografías, ensayos y artículos tienen su framework; aquí
  solo lo docente (presentaciones, evaluaciones, sílabos, calendarios, notas, rúbricas).
- **D7 · `config/` separa datos de lógica.** Los valores ajustables y los datos del docente salen de las
  clases; la lógica queda en `styles/`.
- **D8 · Tema Beamer propio y minimalista**, partido en los cinco archivos canónicos de Beamer.

`academic-poster` y los `examples/` del plan de julio no se llegaron a construir.

**Decidido (2026-09-15, R9 y R10): `mathtools` antes de `unicode-math`, y bloques distintos según el
medio.** Al revés, `\underbrace`/`\overbrace` salen como bloques negros. En texto los bloques van sin
caja, líneas ni iconos; en Beamer conservan caja, filete e icono: es directriz visual del piloto de
exámenes, no descuido.

**Decidido (2026-09-15, M7): el tema Beamer se llama `academic`, en minúsculas.**

**Decidido (2026-09-20, Fase 6 del sistema de diseño): el color sale del repo.**
`config/palette.tex` es un espejo generado desde `sistema-editorial/temas/docencia.yml`; los once
nombres `academic*` conservan valores y modelo, de modo que ningún examen cambió. `\academicbn` (la
salida en gris) la define el generado y la invocan las tres clases con `bn`/`salida=bn`. Contrato en
`sistema-editorial/docs/consumidores.md` §2.

## Estándar de docencia

**Decidido (2026-09-15, M0–M8): un solo repo de contenido, `docencia/`.**
Los 23 repos `Academic_Class-<Área>` con el estándar 00–09 se consolidaron con su historial en el
submódulo `docencia/` (tags `<área>/pre-reorg-2026-09`; tags del framework `pre-reorg-2026-09` y
`reorg-2026-09-done`). Por qué y cómo: [`historial/DIAGNOSTICO_AREAS_2026-09.md`](historial/DIAGNOSTICO_AREAS_2026-09.md);
los mapas archivo a archivo, en `contenido/migracion/historico/`. Lo que no era contenido docente salió:
datasets a `datafw`, trabajos de estudiantes a `registro/`, material de inglés a `notas`.

**Decidido (2026-09-15, M3–M5): `curso.yml` sucede a `temario.yml`; los scaffolds son registros, no
árboles; el dictado vive fuera del curso.**
Las cinco carpetas del curso existen solo con contenido; `CURSO` y `DICTADO` aceptan slug o ruta;
`new-period.sh` queda como aviso de retiro; un dictado puede tomar sesiones de varios cursos y por eso
tiene clave propia en `contenido/dictados/`.

**Decidido (2026-10-04, DOC10): `docencia/` es un repo privado en GitHub y no lleva `LICENSE`**
(`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §15.11: la licencia corresponde solo con remoto público). Si algún día se
publica, antes se separa lo ajeno (`cursos/<slug>/05-recursos/vendor/`, evaluaciones de otras
universidades) de lo propio y el autor elige la licencia.

**Decidido (2026-09-20): la bandeja `_inbox` de `docencia` sale del repo.**
El legado sin clasificar pasó al archivo del vault (`archivo/2026-09-20-docencia-inbox/`); nada
se cita desde allí. Regla vigente: lo que llegue fuera del estándar se clasifica o sale al archivo.

## Currículo y publicación

**Decidido (2026-09-06, F5.0): aquí solo hay docencia propia.** Los cursos que el autor toma y sus
apuntes están en `notas/40-cursos-y-formacion/`.

**Decidido (2026-09-06, F5.1): el currículo vive una vez, en `curso.yml`.** README del curso, ficha web,
temario del learning-skill y checklist de `tareas` se generan (`scripts/temario.py`).

**Decidido (2026-09-06, F5.2): la web se alimenta por hardlink.** `publish-session.sh` congela (tag) y
`publish-web.sh` enlaza en `web/cursos/`; la web nunca tiene copias.

**Decidido (2026-09-06, F5.3–F5.4): los recursos se enlazan, no se copian.** `enlazar.py` une temas con
posts, modelos de `simuladores/` y bancos; la bibliografía externa se cita por `calibre_id`. Una
variante del mismo día (F5a: cada área como submódulo) se revirtió en M2.

**Decidido (2026-10-20, plataforma educativa, fase 1): `area` es un vocabulario cerrado de 12 áreas, una
por sitio.** El autor decidió que los 11 pubs sean las aulas de los cursos y que este repo sea la fuente
única del currículo (`web/docs/plataforma-educativa.md` §0, A1–A4). `area` tenía 20 valores que mezclaban
áreas y herramientas (`python`, `stata`) y grafías dobles (`math`/`matematicas`); `config/areas.yml` fija
las 12 áreas y el pub de cada una, y el primer `area` de un curso decide su pub, para que el vínculo no se
repita en 52 archivos. Movidos de área: microeconometría aplicada, econometría con Python, con R y Python
e indicadores de pobreza con la ENAHO → estadística y econometría; evaluación social de proyectos → gestión
pública; bash → sistemas y seguridad (área nueva de `chaska`). Mapa y migrador:
`contenido/migracion/mapa-areas.csv` y `aplicar-areas.py`; etiqueta `antes-areas-2026-10-20` en el
contenido. `validate.sh` lo exige.

**Decidido (2026-10-20, director por encargo del autor): el temario de cada curso se reconstruye desde su mejor
fuente (C1 de `web/docs/plataforma-educativa.md` §6.1).** El mapa `contenido/migracion/mapa-lecciones.py` mostró
que muchos temarios eran esquemas genéricos (índices tipo w3schools en las herramientas, unidades vagas en
economía) y que las series de los pubs tenían mejor estructura. `curso.yml` sigue siendo la fuente única (A3), pero
su temario se reescribe curso por curso a partir de una base elegida (sílabo oficial, serie del pub o sesiones
dictadas) y las demás fuentes se emparejan contra ella. Casos resueltos ese día: **Power BI** es curso propio
(serie y carpeta propias en numerus-scriptum; antes colgaba de `excel`); **ciberseguridad** no es curso docente
(el post de chaska es un apunte para la certificación CEH: curso tomado, regla F5.0; queda como blog); la
**serie 01–11 de aequilibria es Macroeconomía II** por unidades (economía abierta, consumo e inversión, dinero,
fluctuaciones), asignada en `FIJOS` del mapa; **SQL** no se da de alta mientras no haya material. Desde ese día
`new-course.sh` regenera el README con `temario.py` al crear el curso.

**Decidido (2026-10-20, director por encargo del autor): sin solapamientos entre cursos tras C1.** La
identificación causal con microdatos (experimentos, diferencias en diferencias, regresión discontinua, panel,
estudios de eventos) vive solo en `microeconometria-aplicada`; `econometria-ii` se queda con los estimadores
(MCG, máxima verosimilitud, GMM, variables instrumentales), las series de tiempo y la bayesiana. **Finanzas III**
es derivados y riesgo (lo respaldan su temario y su banco de evaluaciones dictadas); finanzas internacionales es
una unidad. Las **guías de terminal** de chaska son lecciones del curso `linux`. Traza en
`contenido/migracion/mapa-temas-c1.csv` y `FIJOS` de `mapa-lecciones.py`.

## Evaluaciones

**Decidido (2026-09-15, R9–R11): los exámenes propios pasan al sistema `.tex`.** Expediente =
`academic-exam` + solucionario + `code/`; el estándar se consolidó en un solo documento,
[`estandar-evaluaciones.md`](estandar-evaluaciones.md).

**Decidido (2026-09-17, R12): las evaluaciones de otras universidades se transforman como propias**,
cambiando solo el membrete y declarando el origen ajeno y toda clave reconstruida.

**Decidido (2026-09-17, R13): las evaluaciones catalogadas en Calibre salen de la biblioteca** a
expedientes pendientes con su ficha `<tallo>.md` versionada; las fuentes `*_fuente*.pdf` no se
versionan (respaldo en el disco externo del autor). El estado de cada expediente lo da
`contenido/migracion/estado-examenes.csv`, no la prosa.

## Simuladores

**Decidido (2026-10-20, fase 3 de `web/docs/plataforma-educativa.md`, A6 del autor): el laboratorio sale de este
repo a uno propio, `~/Documents/simuladores` (`SIMULADORES_DIR` de `core/env`), con su historia (63 commits por
`git subtree split`).** Es complementario de `docencia`, `divulgacion`, `datafw` y, después, de los pubs, que leerán su
`catalogo.json`; ya no es solo currículo de este repo. Etiqueta `antes-simuladores-2026-10-20`; respaldo y `UNDO.sh` en
`$RESPALDOS_DIR/renombres/2026-10-20-docencia-simuladores-a-simuladores/`. Compatibilidad durante la migración:
`scripts/enlazar.py` traduce los `archivo: docencia/simuladores/…` de `curso.yml` a la carpeta nueva. Las dos
decisiones siguientes quedan como historia.

**Decidido (2026-09-20): el laboratorio `simuladores/` vive en este repo.**
Vino de `02 analysis/simuladores/` (hoy `datafw`) con su historia git porque es currículo —fichas pedagógicas,
verificaciones que son teoremas, animaciones— y lo consumen los cursos, no el pipeline de datos.

**Decidido (2026-10-04, DOC10): `simuladores/CLAUDE.md` se conserva como guía anidada**, excepción a
`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §15.5 (que solo admite guía anidada en un subárbol con manifiesto propio).
Motivo: el laboratorio tiene doctrina propia y la usa una campaña en curso
(`meta/docs/historial/diagnosticos/DIAGNOSTICO_SIMULADORES_2026-10.md`). Sin historial ni recuentos; `AGENTS.md` de la
carpeta es su enlace. Se revisa al cerrar esa campaña.

## Registro privado

**Decidido (2026-09-15, M1): los datos de estudiantes viven en `registro/`**, repo hermano sin remoto,
git-ignorado desde el framework; `scripts/doctor.sh` falla si aparece un remoto.

**Decidido (2026-09-20): `registro/_legado/` es archivo cerrado** (decisión del autor): se conserva
intacto, no se clasifica ni se cita; su respaldo es el disco externo del autor.

## Documentación

**Decidido (2026-09-20, DOC4): la documentación sigue `meta/docs/historial/NORMATIVA_ARCHIVOS.md` §15.**
El estándar se cuenta una vez (`estandar-docencia.md`, `estandar-evaluaciones.md`); README,
`CLAUDE.md` y `docencia/README.md` apuntan; `docs/` en kebab-case con índice generado e `historial/`.

**Decidido (2026-10-04, DOC10): sin `CHANGELOG.md`.** El repo no publica versiones (las dos etiquetas
son hitos de migración); la línea de tiempo de fases quedó en este registro y en el historial de git.
`docs/arquitectura.md` describe la plataforma como es; sus decisiones están aquí.
`docencia/` recibe su propia guía de orientación (`CLAUDE.md`), porque es un repo que se clona solo y
quien lo abre aislado no ve las reglas del framework.
