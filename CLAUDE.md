# CLAUDE.md

Guía para Claude Code (claude.ai/code) y para Codex (`AGENTS.md` es un enlace simbólico a este archivo) al trabajar en este repositorio.

## Reorganización 2026-09-15 (hecha) — contexto antes que el resto

`docs/DIAGNOSTICO_AREAS_2026-09.md` (fases M0–M8, ejecución en §8; tag `reorg-2026-09-done`) sustituyó el
estándar 00–09 por el que describe este archivo. Los 23 submódulos `areas/Academic_Class-*` ya no existen:
sus repos se fusionaron, con historial, en el **único submódulo `docencia/`** (repo `Academic_Class`; tags
`<area>/pre-reorg-2026-09`). Los 23 repos originales se borraron del disco el 2026-09-15 tras verificar el push: su estado previo vive en GitHub
(M0 en los 5 repos heredados con remote, archivados; los 23 dentro de `Academic_Class` bajo `<area>/pre-reorg-2026-09`).
Si un documento, prompt o script habla de `areas/Academic_Class-<Área>/course_NN_<slug>/0N_…`, es histórico:
léelo como `docencia/cursos/<slug>/0N-…` (mapas archivo a archivo: `docencia/migracion/mapa-m3.csv`, `mapa-m4.csv`).

## El ciclo de trabajo, en este sistema

Una clase o un curso siguen `~/Documents/prompts/00 metodo/CICLO.md` en **nivel estándar**:
conocimiento pedagógico y disciplinar consultado en la biblioteca (paso 4), diseño con
alineamiento constructivo (`05 docencia/`), y la lección del aula —qué no entendió la cohorte—
vuelve al `curso.yml` del curso (o al `guion.md` de la sesión) y, si es general, al prompt de `05 docencia/`.

## La arquitectura documental, en este sistema

`~/Documents/prompts/00 metodo/ARQUITECTURA_DOCUMENTAL.md` (2026-09-11) registra los
documentos de docencia —sílabo, sesión de clase, evaluación (12 tipos), rúbrica, nota
docente, calendario— como tipo 22 de la taxonomía del ecosistema, y **su esquema es el
estándar de docencia de este repo** (`docs/09-estandar-docencia.md`: curso, sesión tipada
por artefacto, dictado; `templates/exam/` y `templates/report/`; `scripts/validate.sh`).
No se re-especifica allí: se apunta aquí. La presentación de clase tiene esquema propio en
`03 writing/esquemas/presentacion-clase.tex` (objetivos de aprendizaje → activación →
desarrollo → síntesis → evaluación → próxima sesión, por alineamiento constructivo), que
es también el arco que sigue `guion.md`.

## Qué es este repositorio

El **framework canónico `Academic_Class`** (todo en **español** — mantener el contenido y
las ediciones en español). Cumple tres funciones:

1. **Define el estándar** de organización del contenido docente (curso, sesión, dictado,
   registro, nomenclatura). El spec completo está en `docs/09-estandar-docencia.md`; el
   resumen, en `README.md`.
2. **Aloja lo compartido**: `scaffolds/` (registros mínimos), `templates/` (documentos
   vacíos), `bibliography/` (`.bib`) y `assets/branding/` (logo).
3. **Produce los entregables LaTeX** de cada curso: diapositivas (Beamer o Quarto, en la
   sesión), evaluaciones (`04-evaluaciones/`, clase `academic-exam` + `templates/exam/`) y
   documentos de diseño (`01-diseno/`, clase `academic-report`) — ver `docs/00-arquitectura.md`.

**Los cursos reales NO viven en el núcleo del framework.** Viven en `docencia/` (submódulo,
repo `Academic_Class`): `cursos/<slug>/` (50), `dictados/<clave>/` y `_inbox/` (legado por
clasificar). Lo privado (estudiantes, calificaciones, evidencias) vive en `registro/`, repo
hermano git-ignorado que **nunca** tiene remote público (el doctor lo comprueba). Flujo:
commit dentro de `docencia/` → `git add docencia` + commit aquí (mueve el puntero). Clon
nuevo: `git clone --recurse-submodules`. Los scripts de `scripts/` reciben `CURSO` y
`DICTADO` como **slug o ruta**.

No hay suite de tests. Verificación = `./scripts/validate.sh CURSO|--todos` (estructura y
registros) + compilar a PDF y mirarlo + `./scripts/doctor.sh` (entorno, `validate --todos`,
verificadores de vistas y enlaces, `_inbox`, binarios, remote de `registro/` **y** la
normativa de archivos vía `core/archivos.py validar "10 Class"`).

## El estándar (resumen; detalle en `docs/09-estandar-docencia.md`)

- **Curso** = `docencia/cursos/<slug>/` con `curso.yml` (registro; sucesor de `temario.yml`)
  y `README.md` (generado). Slug kebab-case **sin número**: el orden de malla es
  `malla.orden`. Carpetas de **lista cerrada** `01-diseno · 02-contenido · 03-sesiones ·
  04-evaluaciones · 05-recursos`, que existen solo con contenido; carpeta desconocida o
  vacía = error de `validate.sh`; **sin `.gitkeep`**.
- **`curso.yml`** (normativa §7): línea 1 de identidad; núcleo `id` (= carpeta) · `titulo` ·
  `estado` (`borrador | activo | archivado`) · `tipo` (`asignatura | herramienta |
  nivelacion | taller`); más `alias[]` (ids antiguos), `area[]`, `malla`, `materia_web`,
  `prerrequisitos`, `etiqueta`, `dominio_fuat`, `unidades[]`, `bibliografia[]`,
  `banco_examenes[]`, `datasets[]`, `ajeno[]`. `validate.sh` exige el núcleo.
- **Sesión** = `03-sesiones/sNN-<slug>/` con `sesion.yml` (`id` = carpeta, `titulo`, `tipo`,
  `estado`, `artefacto`…), `guion.md` (plan + notas + retrospectiva) y **el artefacto que
  exige el tipo**: `clase` → `deck.tex|qmd`; `laboratorio` → `cuaderno.ipynb` /
  `script.do|.R|.py|.rmd`; `taller` → `libro.ods|xlsx`; `evaluacion` → `evaluacion.tex`.
  Nada más es obligatorio; no hay subcarpetas de anatomía. El número lo da la carpeta.
  `revisar: <motivo>` rebaja a aviso una incoherencia tipo/artefacto.
- **Dictado** = `docencia/dictados/<AAAA-ciclo>-<institucion>-<materia>/dictado.yml`
  (`sesiones: [{orden, curso, sesion, web}]`, `web: {materia, edicion}`; puede cruzar varios
  cursos). Congelar = `tag dictado/<clave>/<sesion>`; `publicacion/<web>/` es producto
  git-ignorado; la web lo enlaza por hardlink. `legado: true` = dictado anterior al
  estándar, no se republica.
- Las **notas de estudio** de `02-contenido/**/*.md` son régimen del vault (§10.4):
  nombre kebab (`1-2-tema.md`) y frontmatter `tipo: apunte · titulo · estado · tags`.
  `normalizar-notas.py --aplicar` las normaliza; `archivo:` en `curso.yml` es `null`
  hasta que la nota existe (**sin esqueletos**).
- Lo **ajeno** (plantillas de terceros, fuentes, clases descargadas) vive en `vendor/`
  (`05-recursos/vendor/`): sin cabecera propia, fuera del validador, anotado en `ajeno:`.
- **Nomenclatura**: kebab-case ASCII minúsculas en carpetas y archivos; claves `snake_case`;
  períodos `AAAA-i`/`AAAA-ii`. Fuera de norma solo `vendor/` y `_inbox/`.

## Arquitectura del repo

- `config/course.yml` — valores por defecto del docente (identidad, logo, tema,
  compilador). YAML **plano**; los scripts lo parsean con grep/sed (no anidar).
- `scripts/` — automatización. La lógica compartida está en `scripts/lib/common.sh`
  (rutas `DOCENCIA_DIR/CURSOS_DIR/DICTADOS_DIR/INBOX_DIR/REGISTRO_DIR`, `yaml_get`,
  `config_get`, `slugify`, `latex_engine`, `compile_tex`, y los helpers `is_course`/
  `course_dir`/`dictado_dir`/`session_dir`/`list_sessions`/`list_courses`/`list_dictados`/
  `session_artifact`, que aceptan slug o ruta). Los scripts de entrada solo orquestan.
  Nuevos parámetros → `config/course.yml`.
**Plataforma editorial (rediseño 2026-07-23, ver `docs/00-arquitectura.md` — fuente de verdad arquitectónica). Motor LuaLaTeX exclusivo (migración 2026). Capas, cada una con responsabilidad única:**

- `styles/` — **identidad visual única** (`academic.sty` carga colores, fuentes
  fontspec Libertinus+Inconsolata, math, iconos, bloques, código, tablas, idioma). Orden
  de carga obligatorio: `mathtools` (amsmath) **antes** de unicode-math, si no
  `\underbrace`/`\overbrace` salen como bloques negros (R9, 2026-09-15). Los bloques
  (`instrucciones`, `datos`, `solucion`, `nota`…) siguen la directriz visual de evaluaciones
  (R10): en texto, lavado gris casi imperceptible (`fondobloque`), rótulo en versalitas y
  cuerpo alineados, **sin caja, líneas ni iconos**; en Beamer conservan caja, filete e icono.
  amssymb no existe bajo unicode-math (`\blacksquare` → `\mdlgblksquare`); `\nota{}` como
  comando ya no existe: es `\interpreta{}`.
  La cargan por igual las clases de documento **y** el tema Beamer → un examen y
  una diapositiva comparten diseño al carácter. **El color se cambia en un solo
  sitio, `config/palette.tex`; las tipografías, en `styles/academic-fonts.sty`.**
- `classes/` — clases delgadas que encapsulan el diseño: `academic-base` (núcleo
  `article`), `academic-exam` (evaluaciones, 3 modos, hereda base), `academic-report`
  (sílabo/calendario/nota-docente/rúbrica, hereda base), `academic-beamer` (beamer + tema).
- `themes/` — tema Beamer propio `beamer{,color,font,inner,outer}themeacademic` (minimalista; consume `styles/`).
  Se llama `academic` en minúsculas (`\usetheme{academic}`) desde M7 (2026-09-15): nombres de archivo
  en minúsculas como el resto del framework.
- `templates/` — documentos vacíos, **sin diseño** (`presentation/` 8 tipos, `exam/` 12 tipos, `report/` 4); solo `\documentclass{academic-*}` + contenido.
- `scaffolds/` — **registros mínimos**, no árboles de carpetas (M5): `curso/` (`curso.yml`, `README.md`),
  `sesion/` (`sesion.yml`, `guion.md`, `deck.tex`, `deck.qmd`), `dictado/` (`dictado.yml`).
- `bibliography/` — `.bib`. `assets/branding/` — logo canónico. `examples/` — ejemplos compilados.
  `config/` — `course.yml` (datos) + `palette.tex` (color).
- `docs/` — documentación técnica (`00-arquitectura.md` para la plataforma; `09-estandar-docencia.md` para el contenido).
- `docencia/` — submódulo de contenido; `registro/` — repo privado hermano (ignorado).

> Nota histórica: se retiraron `evaluaciones/` (→ `academic-exam` + `templates/exam/`),
> `_PLANTILLAS/` (→ `templates/` + `scaffolds/`) y `_BIBLIOTECA/` (→ `bibliography/`) en el
> cutover del rediseño; `libraries/Banco_*` (vacíos) y `scaffolds/{course,session,period}`
> (árboles 00–09) se retiraron en la reorganización de 2026-09-15; el motor pasó de pdfLaTeX
> a XeLaTeX y, en la migración de 2026, a **LuaLaTeX** (único motor soportado).

## Comandos

```bash
# Los argumentos CURSO y DICTADO aceptan ruta o slug (docencia/cursos/<slug>, docencia/dictados/<clave>). M5, 2026-09-15.

# Crear (solo el registro y el artefacto del tipo; sin árboles de carpetas)
./scripts/new-course.sh  SLUG "Título" [--tipo asignatura|herramienta|nivelacion|taller] [--area a,b] [--materia-web m]
./scripts/new-session.sh CURSO NN "Título" [--tipo clase|laboratorio|taller|evaluacion] [--quarto] [--artefacto NOMBRE]
./scripts/new-dictado.sh AAAA-ciclo INSTITUCION MATERIA "Título"   # docencia/dictados/<clave>/dictado.yml + registro/<clave>/

# Documentos LaTeX (plantillas de templates/, identidad única, LuaLaTeX)
./scripts/new-presentation.sh CURSO NN "Título" [--tipo clase]        # deck academic-beamer en la sesión (declara artefacto)
./scripts/new-evaluacion.sh   CURSO <tipo|01-12> "Título" [--fecha AAAAMMDD]   # → 04-evaluaciones/<sub>/AAAAMMDD_sig.tex
./scripts/new-report.sh       CURSO <silabo|calendario|nota-docente|rubrica> "Título"   # → 01-diseno/
./scripts/build.sh ARCHIVO.tex [--modo examen|claves|soluciones|todos]   # compila cualquier .tex con LuaLaTeX
./scripts/build-session.sh CURSO NN        # compila el artefacto declarado en sesion.yml (.tex/.qmd)
./scripts/build-course.sh  CURSO [--solo-sesiones]

# Currículo único: curso.yml es la fuente; README/web/skill/checklist se generan
./scripts/temario-generar.sh generar  [--aplicar] [--que readme,web,skill,resumen] [CURSO...]
./scripts/temario-generar.sh verificar                              # exit!=0 si un README no coincide con su curso.yml (lo corre el doctor)
./scripts/temario-generar.sh migrar   [--aplicar] [CURSO...]        # solo cursos heredados sin curso.yml
python3 scripts/enlazar.py posts|simuladores|examenes [--aplicar]   # F5.3; verificar lo corre el doctor

# Validación y resumen
./scripts/validate.sh CURSO|DICTADO|--todos    # reglas §4 (lista cerrada, sin vacías, artefacto por tipo, guion.md)
./scripts/stats.sh CURSO                       # sesiones: tipo · estado · artefacto · PDF · guion
./scripts/doctor.sh                            # entorno + validate --todos + verificadores + _inbox + binarios + normativa

# Normativa de archivos (meta/NORMATIVA_ARCHIVOS.md). Simulan sin --aplicar.
python3 scripts/normalizar-archivos.py todo|registros|cursos|nombres|cabeceras|frontmatter|artefactos|vendor [--aplicar] [--bitacora DIR]
python3 scripts/normalizar-notas.py [--aplicar] [--bitacora DIR] [CURSO...]

# Publicación: publicar = etiquetar (tag dictado/<clave>/<sesion>) + producto git-ignorado; la web enlaza por hardlink
./scripts/publish-session.sh DICTADO CURSO NN [--refrescar]   # → docencia/dictados/<clave>/publicacion/<web>/
./scripts/publish-web.sh     DICTADO [--aplicar]              # dictado.yml → 04 index/cursos/<materia>/<edicion>/ (simula sin --aplicar)

./scripts/clean.sh [--pdf] [DIR]
bash -n scripts/<archivo>.sh            # uno por invocación: con varios archivos bash -n solo comprueba el primero
```

`compile_tex` prefiere el compilador universal del workspace
(`~/Documents/scripts_for_latex/script_compilar_latex/main.sh`, autodetecta motor);
si no existe, usa el motor detectado por `latex_engine()` (comentario `%!TEX`, clase
`yaac-*`, `fontspec`) dos veces.

`compile_tex` prefiere el compilador universal del workspace
(`~/Documents/scripts_for_latex/script_compilar_latex/main.sh`, autodetecta motor);
si no existe, usa el motor detectado por `latex_engine()` (comentario `%!TEX`, clase
`yaac-*`, `fontspec`) dos veces. Ojo: el compilador universal **borra el PDF** cuando la
compilación falla; si es un PDF versionado, se recupera con `git checkout`.

## Convenciones

- **Español** en todo. **kebab-case ASCII** (sin tildes ni espacios) en carpetas y archivos
  nuevos. **Sin carpetas vacías** (error del validador; ya no se usan `.gitkeep`).
- **Homogeneidad total**: al estandarizar se convierte todo al estándar; si un deck deja
  de compilar, se reconstruye.
- Los decks Beamer son **autocontenidos** (preámbulo propio + copia local del logo).
  Al mover una sesión, mover su carpeta **completa** (los assets son hermanos del `.tex`).
- **Reversibilidad por git (todo)**: el framework, `docencia/` y `registro/` son repos.
  Cualquier reorganización sigue el ciclo (auditoría → propuesta → aprobación → tag → cambio
  con dry-run → validate → doctor → commit) y deja su mapa de rutas en `docencia/migracion/`
  y su bitácora con `UNDO.sh` en `meta/reparaciones/`.
- En zsh y con rutas que llevan espacios (`10 Class`): iterar con `while read`, nunca con
  `for x in $(…)`; `bash -n` comprueba **un** archivo por invocación.
- `*.sdr/` = metadatos de KOReader; ignorar.

## Estado

- **50 cursos** en `docencia/cursos/` cumplen el estándar (`validate.sh --todos`: 0 errores;
  67 sesiones tipadas; 2 dictados de Metodología, 2025-I marcado `legado`).
- **Banco de exámenes rendidos** (R9–R11, 2026-09-15/16) — **migración completa**. El estándar de
  evaluaciones (tipos, siglas, subcarpetas, expediente `AAAAMMDD_sig/` con `code/{data,figures,table}`, flujo de
  transformación y registro) es `docs/10-estandar-evaluaciones.md` (2026-09-15); el prompt maestro remite a él. Migrar = transformar cada
  examen al sistema `.tex` (`academic-exam`, solucionario, `code/`, nomenclatura del prompt
  `prompts/05 docencia/prompt_resolucion_examenes_plantillas.md`) y eliminar el original una vez validado.
  Estado real (`docencia/migracion/estado-examenes.csv`, regenerar con `estado-examenes.py --aplicar`): al 2026-09-16
  (R11, cierre) hay **172 expedientes transformados** en 18 cursos (Econometría I 58, Estadística para Economistas 35,
  Econometría II 34, Macroeconomía II 8, Comercio Internacional 8, Finanzas I 7, Macroeconomía I 5, Evaluación Privada
  de Proyectos 4, Recursos Naturales 3, Formulación de Proyectos 2 y uno en Organización Industrial, Micro I y II,
  Matemáticas I y II, Excel, Economía Pública y Crecimiento Económico; el curso `estadistica` quedó sin banco porque
  todo era EPE), **16 `manual`** documentados (sin enunciado, sin base de datos o manuscritos sin transcribir; uno de
  ellos, `econometria-i/practicas/2020_pc`, espera la decisión sobre un PDF «no borrar») y **0 pendientes**. Los cursos
  `macroeconomia-dinamica`, `economia-politica` y `economia-monetaria` quedaron sin `04-evaluaciones/` porque sus
  bancos eran exámenes de otras universidades o de otros cursos (devueltos al vault).
  Los exámenes teórico-gráficos se transforman con figuras matplotlib en `code/<tallo>.py` (sin datos); cuando el
  enunciado pide datos que no trae, se ilustran con series públicas (BCRP, FMI, Banco Mundial) declaradas en la cabecera.
  Los tests de Google Forms se reconstruyen con la clave del docente (respuesta correcta de las erradas y opción
  marcada de las acertadas). Los años de tallo se fijan por la evidencia interna (fechas de salidas EViews, horizonte
  de los datos, fechas de creación de los PDF de respuestas), no por la carpeta de origen; `sinfecha_sig` cuando no la hay.
  Cada transformación se cierra con
  `docencia/migracion/cerrar-expediente.sh CURSO SUB TALLO [ORIGEN…]` (compila, borra el original —también si está en
  otro curso—, regenera registro y README, valida y hace los dos commits). Los materiales que no son evaluaciones
  (guías de clase, lecturas, exámenes de otras universidades o de cursos sin dictado, datasets sueltos, respuestas
  manuscritas) no se transforman: vuelven al vault (`material-de-apoyo/`, `_datasets/`, `otras-universidades/`,
  `sin-clasificar/` o una carpeta nueva del curso sin dictado) y se anotan en su `readme.md`.
  `curso.yml.banco_examenes` los declara (`enlazar.py examenes`); mapa y migrador en `docencia/migracion/`;
  bitácoras `meta/reparaciones/R9_…` y `R10_…`. En el vault quedan las carpetas sin curso docente (12: las 7
  originales más `planeamiento-y-gestion-de-empresas`, `costos-y-presupuestos`, `finanzas-internacionales`,
  `planificacion-y-presupuesto` y el `politica-economica-ec547` de `sin-clasificar`), `otras-universidades/`
  (PUCP, UNMSM, MIT, ESPOL, Bacchetta), `material-de-apoyo/` por curso y `_datasets/`.
- **Pendiente del docente** (heredado, no de la migración): 5 de los 6 decks Beamer
  heredados probados no compilan (logo `cau-logo.png` ausente o `%!TEX program = xelatex`);
  se reconstruyen al usarlos, no se "arreglan" borrando contenido. 15 binarios > 5 MB
  (avisa el doctor; los dos del banco de EPE volvieron al vault con las sesiones Stata 2021-II). `_inbox/` (401 archivos) por clasificar. 20 datasets aterrizados en
  `02 analysis/data/raw/_docencia_por_catalogar/` por catalogar.
- **Remotes** (push hecho por el usuario el 2026-09-15 con `R8_…/subir-remotos.sh`): `docencia/` →
  `achalmed/Academic_Class` (privado; repo `MyTestProyect` reutilizado y renombrado, sin crear uno
  nuevo; `main` = `49589af` y 25 tags); framework → `achalmed/CampusTeX-Research`. Las 5 áreas que
  tenían remote (`econometric`, `CampusTeX-Projects`, `LaTex`, `Python`, `Machine-learning-con-R`)
  recibieron su estado M0 y quedaron **archivadas** en GitHub. Los tags `pre-reorg-2026-09` y
  `reorg-2026-09-done` del framework se restauraron desde sus objetos colgantes (alguien había
  borrado las refs): hay que subirlos (`git push origin --tags`) para que un `fetch --prune-tags`
  no los vuelva a borrar (subidos el mismo día). `areas_originales/` (1,6 GB) borrado el 2026-09-15: la migración no deja
  nada pendiente del usuario.

## El currículo: `curso.yml` (F5.1, 2026-09-06; sucesor de `temario.yml` desde M4, 2026-09-15)

Cada `docencia/cursos/<slug>/` lleva un **`curso.yml`**, registro del curso (normativa §7):
línea 1 de identidad, núcleo `id · titulo · estado · tipo`, más `alias`, `emoji`,
`descripcion`, `area[]`, `rol: docente`, `nivel`, `malla`, `prerrequisitos`, `etiqueta`,
enlaces (`materia_web` a `04 index/cursos/<materia>`, `dominio_fuat` al dominio del
learning-skill) y **`unidades[].temas[]`** (id, título, `archivo` en `02-contenido` o
`null`, `recursos[]` opcionales: apunte, simulador, libro por `calibre_id`, post, examen).
**Es la única fuente**: el `README.md` del curso, la sección «Contenidos / Sílabo» de la
ficha web, `prompts/05 docencia/learning-skill/2 domains/_temarios/<dominio>.md` y
`05 tasks/temarios-cursos.md` (nota `tipo: checklist` con marca `GENERADO`) se generan con
`scripts/temario-generar.sh`. Regla: **edita el registro, no las vistas**; el doctor avisa
si un README se desfasó. `migrar` solo se usa para un curso heredado sin `curso.yml`.
**Bibliografía (F5.4):** el material bibliográfico externo NO vive en `05-recursos`: vive en
Calibre y el registro lo cita en `bibliografia: [{calibre_id, titulo, autor, origen}]` (lo
escribe `scripts_for_fuentes/ingesta_cursos/main.sh`). En `05-recursos` quedan datasets
pequeños, talleres, plantillas y material propio. **Subir no es catalogar:** antes de añadir,
la suite busca el libro en Calibre; lo nuevo se cataloga con el patrón de la biblioteca
mediante `scripts_for_calibre/script_catalogacion_biblioteca/`.

## El dictado y la web: `dictado.yml` + hardlinks (F5.2, 2026-09-06; `dictados/` desde M4)

Un dictado (`docencia/dictados/<AAAA-ciclo>-<institucion>-<materia>/`) puede componerse de
sesiones de **varios cursos** (Metodología 2026-I = monografías + seminario + APA + LaTeX).
Su manifiesto `dictado.yml` lista `sesiones: [{orden, curso, sesion, web}]` y el destino
`web: {materia, edicion}`. Flujo: `publish-session.sh` congela cada sesión (tag
`dictado/<clave>/<sesion>` + producto en `publicacion/<web>/`, git-ignorado) →
`publish-web.sh` enlaza esos archivos **por hardlink** en
`04 index/cursos/<materia>/<edicion>/<web>/` (un solo inodo, dos canales; la web nunca
tiene copias) y crea `index.qmd`/`_links.md` solo si faltan. Regla D5: **el framework es la
fuente**; lo que aparece en la web sale de un módulo publicado. El doctor avisa si un dictado
tiene copias o huérfanos en la web. Las fichas web sin curso ni ediciones llevan `draft: true`.

## Ecosistema de aprendizaje (contexto externo)

`docencia/` contiene **solo docencia** (F5.0, 2026-09-06): los cursos que Edison toma y
sus **apuntes de estudio** viven en `01 notes/40-cursos-y-formacion/<curso>/`
(learning-skill, preset `apuntes_clase`) y enlazan al tema del curso docente en
`02-contenido`. El contrato entre piezas está en `~/Documents/prompts/ECOSISTEMA_APRENDIZAJE.md`;
si un cambio del estándar afecta a los apuntes, pasa por su checklist de propagación.
