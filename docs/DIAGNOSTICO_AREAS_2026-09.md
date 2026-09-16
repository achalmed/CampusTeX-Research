---
tipo: doc
titulo: "Diagnóstico de `areas/` y propuesta de reorganización (2026-09-15)"
estado: hecho
fecha: 2026-09-15
---
# Diagnóstico de `areas/` y propuesta de reorganización

> Ciclo de trabajo (`prompts/00 metodo/CICLO.md`), nivel **profundo**: el cambio toca 23
> repositorios, la web, el learning-skill, la biblioteca y `02 analysis`. Este documento
> cubre diagnóstico → diseño (pasos 2–8). Las fases M0–M8 de §6 se ejecutaron el 2026-09-15
> (§8; bitácoras `meta/reparaciones/R1_areas_…` a `R8_leccion_…`; tag `reorg-2026-09-done`). Todas las cifras se midieron sobre el árbol real el 2026-09-15 (`estructura.txt`
> generado a las 08:08 más un censo por script sobre `areas/`, excluyendo `.git`).

## 0. Resumen ejecutivo

1. **Los conceptos del estándar 00–09 son correctos** (separar contenido, sesiones,
   evaluaciones y dictados; un registro YAML por curso y por sesión; publicar por
   hardlink) y deben conservarse. **Su implementación como molde uniforme no.**
2. El molde produjo un árbol donde el **57 % de los directorios están vacíos**
   (1 787 de 3 145), hay **1 403 `.gitkeep`**, 145 `README.md` idénticos y **1 934 de
   1 954 notas de `02_CONTENIDO` son esqueletos sin cuerpo** marcados `estado: activo`.
3. La capa `Academic_Class-<Área>` **duplica la identidad**: 13 de las 23 áreas contienen un
   solo `course_00_curso_base` (área = curso), mezcla disciplinas con herramientas y cuesta
   23 repos git, de los que **18 apuntan a remotes que no existen**.
4. El número `NN` de `course_NN_` tiene **dos semánticas** (orden en la malla vs. `00` =
   cajón) y **colisiona** (siete `course_01_` distintos).
5. **Duplicación real**: 148 MB en 105 grupos de archivos idénticos; la misma diapositiva
   de 42,8 MB vive tres veces (sesión, `publicacion/`, backup).
6. **Riesgo de privacidad**: trabajos y documentos de estudiantes (escrituras públicas,
   planes de negocio) están versionados en dos repos **públicos** de GitHub.
7. **Inversión fuente/vista**: los 8 cursos con más material real son justo los que tienen
   `temario.yml` con 0 unidades; los 40 cursos que el temario describe no tienen material.
   La web tiene una edición (2025-I) con 183 archivos que no existe en el framework.
8. Propuesta (§4): **un solo repo de contenido** con dos colecciones (`cursos/` plano por
   slug, `dictados/` por período), un **repo privado `registro/`** para datos de
   estudiantes, **cinco carpetas por curso creadas bajo demanda**, sesiones tipadas por
   archivo y no por subcarpetas, congelar por **tag git** y no por copia, y lo pesado o
   ajeno **por clave** (Calibre, `02 analysis`, framework).

## 1. Diagnóstico de la estructura actual

### 1.1 Qué hay

| Magnitud | Valor |
|---|---|
| Áreas (`Academic_Class-*`, submódulos) | 23 |
| Cursos `course_*` | 54 (el `CLAUDE.md` habla de 61; conciliar) |
| Sesiones `SNN_*` | 67, en solo 5 áreas (LaTeX 8, Metodología 12, Ofimática 20, Stata 14, python 13) |
| Archivos (sin `.gitkeep`) / tamaño | 4 695 / 1 207 MB |
| Directorios / hojas vacías (solo `.gitkeep` o `README`) | 3 145 / 1 787 (57 %) |
| `.gitkeep` | 1 403 |
| `README.md` / idénticos byte a byte | 247 / 145 (17 plantillas de scaffold) |
| Notas `.md` en `02_CONTENIDO` / con cuerpo real | 1 954 / 20 |
| `temario.yml` en estado `borrador` / `activo` | 50 / 4 |
| Tamaño acumulado de los 23 `.git` | ≈ 1,0 GB |
| Rutas con espacios o tildes (fuera de inboxes) | 924 |

Tipos de archivo dominantes: `.md` 2 636, `.ods` 283, `.pdf` 206, `.tex` 172, `.png` 145,
`.yml` 142, `.odt` 103, `.xlsx` 96, `.docx` 86, `.do` 74, `.dta` 70, `.ipynb` 19.

### 1.2 Cómo se usa realmente el 00–09

Cursos con al menos un archivo real en cada carpeta (de 54):

| Carpeta | Cursos con contenido | Observación |
|---|---|---|
| `00_ADMINISTRACION` | 1 | solo el seminario de Metodología (sílabo + fuentes vendor) |
| `01_PLANIFICACION` | 1 | lineamientos CAU, mismo curso |
| `02_CONTENIDO` | 49 | pero el contenido es el esqueleto generado por `temario.py`; cuerpo real en 3 cursos |
| `03_SESIONES` | 7 | 67 sesiones; 47 sin deck `.tex`/`.qmd` |
| `04_EVALUACIONES` | 4 | Econometría I (19), Gestión c00 (11), Crecimiento (3), Seminario (1) |
| `05_ESTUDIANTES` | 3 | volcados legados (Gestión c00: 278 archivos; Estadística c00: 17) |
| `06_RECURSOS` | 13 | el cajón real: datasets, talleres, vendor, código, sílabos |
| `07_MULTIMEDIA` | 1 | Stata c01 (13 imágenes) |
| `08_INVESTIGACION` | 2 | banco de temas del seminario |
| `09_SEMESTRES` | 4 con dictado (Metodología 2026-I); 50 con solo el README | un dictado en 54 cursos |

Anatomía de sesión (`01_Antes … 07_Notas`): las seis subcarpetas distintas de `02_Clase`
tienen contenido únicamente en las 12 sesiones de Metodología. En las otras 55 sesiones
**todo está en `02_Clase`**, y lo que hay allí no es un deck: hojas `.ods` (22 sesiones),
cuadernos `.ipynb` (11), scripts `.do` (5), datos `.csv`/`.dta`, exportaciones `.mht` de
81 MB. La anatomía modela una clase magistral; el 70 % de las sesiones son laboratorio.

### 1.3 Qué funciona y debe conservarse

- **`temario.yml` como única fuente del currículo** y las vistas generadas (README, web,
  learning-skill, checklist). Es la mejor decisión del sistema; solo cambia de nombre y
  gana campos.
- **Registro YAML por sesión** (`metadata.yml` con `id · titulo · estado`) y número
  derivado de la carpeta.
- **`dictado.yml` + publicación por hardlink** hacia `04 index/cursos/` (regla D5: el
  framework es la fuente). Once hardlinks reales en 2026-I lo demuestran.
- **La plataforma editorial** (`academic-*`, `styles/`, `templates/`, LuaLaTeX) y la regla de
  decks autocontenidos.
- **Bibliografía por `calibre_id`** y la regla "subir no es catalogar" (F5.4).
- **`vendor/`** para lo ajeno, fuera del validador.
- **Notas en régimen del vault** (kebab + frontmatter `tipo: apunte`).
- **Validador + doctor** como mecanismo, y **reversibilidad por git** como política.
- La separación conceptual **contenido · sesión · evaluación · dictado**.

## 2. Problemas y riesgos identificados

### P1. El área como contenedor y como repo no aporta y cuesta

- 13 áreas tienen exactamente un curso, llamado `course_00_curso_base` (Bash, Git, LaTeX,
  Stata, python, R, Eviews, Gretl, SPSS, Geogebra, Ofimática, Programming-concepts,
  Languages). Dos niveles de carpeta y un repo para nombrar una sola cosa.
- Las áreas mezclan **disciplinas** (Math, Micro, Macro, Finanzas, Filosofía…) con
  **herramientas** (Stata, R, python, LaTeX…). Un curso "Econometría con Python" cae en
  dos áreas: existe `R/course_01_econometria_r_y_python` y
  `python/course_02_econometria_r_y_python`, el mismo curso partido por lenguaje, con dos
  `id` (`_r`, `_python`), ambos con 0 unidades en su temario.
- `Academic_Class-00-curso-0` es un curso disfrazado de área; `Languages` (niveles de
  inglés, Duolingo, 186 archivos en un inbox) no es docencia: contradice F5.0 ("las áreas
  contienen solo docencia") y pertenece a `01 notes/40-cursos-y-formacion/`.
- **Git**: 23 repos para 1,2 GB de un solo autor. 18 remotes `Academic_Class-*` no existen
  en GitHub (URL relativa nunca materializada); 5 áreas llevan 6–10 commits sin push; los
  5 remotes reales tienen nombres heredados (`econometric`, `CampusTeX-Projects`, `LaTex`,
  `Machine-learning-con-R`, `Python`). Cada cambio transversal es 23 commits + 23 punteros.

### P2. `NN` en `course_NN_` tiene dos significados y no identifica

- En Math/Micro/Macro/Finanzas/Filosofía/Gestión pública el número es el **orden en la
  malla** de Economía (01 Mate I, 02 Micro I, 03 Mate II, 04 Macro I … 25 Filosofía
  política). En las áreas-herramienta es `00` = "cajón". En Gestión empresarial conviven
  01/02/03 locales con 22 (malla). Estadística usa 01, 02, 13, 16.
- Colisiones: `course_01_` en 7 áreas, `course_02_` en 5, `course_00_` en 16.
- El orden de la malla es **metadato de un plan de estudios**, no propiedad de la carpeta:
  cambia si cambia el plan y no sirve para el curso taller de la CAU.

### P3. El molde 00–09 se aplica siempre, se usa casi nunca

- Cinco de las diez carpetas (`00`, `01`, `05`, `07`, `08`) tienen contenido en 1–3 cursos.
  El scaffold crea por curso ≈ 40 directorios con `README` y `.gitkeep`; multiplicado por 54
  da los 1 787 directorios vacíos y los 145 README idénticos.
- El scaffold de sesión crea 7 subcarpetas + 4 archivos plantilla (`lesson_plan.md`,
  `teacher_notes.md`, `retrospective.md`, `links.md`) que quedan vacíos en 55 de 67
  sesiones.
- Efecto práctico: la navegación (Obsidian, `find`, `ls`) muestra una estructura que no
  informa; buscar "qué hay en Stata" exige abrir 40 carpetas para encontrar 3.

### P4. `02_CONTENIDO` está lleno de notas vacías que dicen estar activas

- `temario.py generar --que esqueleto` creó 1 934 notas de ≈ 120 bytes (solo frontmatter).
  Todas declaran `estado: activo`, con lo que Dataview, el learning-skill y cualquier
  búsqueda las cuentan como apuntes existentes. El dato es falso.
- Los 8 temarios con 0 unidades (Stata c01, python c01/c02, R c01, Languages, Geogebra,
  Gestión c00, Estadística c00) son precisamente los cursos con material real (sesiones,
  código, datos). El sistema de currículo describe lo que no existe y calla lo que existe.

### P5. Duplicación y "congelación" por copia

- 105 grupos de archivos idénticos (> 20 KB), 147,7 MB. Tres capas del mismo archivo:
  `03_SESIONES/S02/02_Clase/index.pdf` (42,8 MB) = `09_SEMESTRES/2026-I/publicacion/S02/slides/index.pdf`
  = `_ESTANDARIZACION/_backup_originales/…/index.pdf`.
- `publish-session.sh` congela **copiando** dentro del mismo repo; la web sí usa hardlinks.
  La copia no congela nada (git ya congela por commit/tag) y duplica el repositorio.
- `_ESTANDARIZACION/` (446 archivos, 100 MB) no está versionado y **sus originales no
  están en el historial git**: es la única copia del estado anterior al estándar, dentro
  del árbol de trabajo, sin índice. `CLAUDE.md` ya declara que no se usan más.
- `04 index/cursos/metodologia-de-la-investigacion/2025-1-cau-unsch/` tiene 183 archivos,
  0 hardlinks y ningún dictado en el framework: la web es fuente de una edición completa
  (inversión de D5).

### P6. Legado sin integrar, con nombres de otra época

- Cuatro `03_temas/` a nivel de área (Geogebra 32 archivos, Gestión 28, LaTeX 127, SPSS 4)
  fuera de cualquier curso; el validador no los ve.
- Siete `_POR_REVISAR/inbox/desde_*` (251 archivos versionados) y `_MAPEO_ESTANDAR.md`,
  `leeme-estandar.md` que describen un estándar 00–10/11 ya retirado.
- 924 rutas con espacios o tildes (`taller flujodecaja unah.odt`, `8 01 group project 01`),
  concentradas en Gestión empresarial (364), Ofimática (60), LaTeX vendor (27), Stata (≈70).
- Nombres de sesión heterogéneos: `S01` sin slug (Stata c01), `S01_01_elementos…` doble
  número (LaTeX), `S00_sesion_econometria_00_introduccion…` triple redundancia y sesión
  cero (python), `S07_sesion` (Ofimática).

### P7. Cuatro convenciones de caja en una misma ruta

`areas/Academic_Class-Gestion-empresarial/course_01_formulacion_de_proyectos/02_CONTENIDO/Unidad_01/1-2-tema.md`
combina `Título-Con-Guiones`, `snake_lower`, `MAYÚSCULAS_CON_NÚMERO`, `Capitalizado_NN` y
`kebab`. Además: `LaTex` (sic), `python` vs `R`, `Spss`, `seminario-de-investigacion` con
guiones donde el resto usa `_`. La normativa de archivos (§ nombres) pide una sola forma.

### P8. Binarios pesados y datos de estudiantes en repos públicos

- Blobs versionados de 80,9 MB (`.mht`), 79,2 MB (`.pptx` de estudiantes), 58,3 MB, 42,8 MB
  ×2, 37 MB, 29,6 MB (`.dta` ENAHO). GitHub rechaza > 100 MB y avisa > 50 MB; el repo de
  Gestión ocupa 330 MB en GitHub.
- `Gestion-empresarial/course_00/05_ESTUDIANTES/proyectos/` (escrituras públicas de
  asociaciones, planes de negocio, trabajos grupales) está en `CampusTeX-Projects`,
  **público**; `Estadistica/course_00/05_ESTUDIANTES` en `econometric`, **público**. El
  estándar llama "privado" a `05_ESTUDIANTES` y a `09_SEMESTRES/<p>/{estudiantes,calificaciones}`,
  pero los pone en el mismo repo que la publicación.
- Datasets estadísticos oficiales (ENAHO sumaria 2019, módulos INEI) viven en `02_Clase` de
  una sesión, cuando el ecosistema tiene `02 analysis` (datafw) como capa de datos con catálogo.
- Artefactos LaTeX versionados pese al `.gitignore` (9 en LaTeX, 1 en Estadística, 1 en Gestión).

### P9. Desacople curso ↔ web ↔ bancos

- `web_slug` es muchos-a-uno: `finanzas` (3 cursos), `econometria` (2), `macroeconomia` (2),
  `microeconomia` (2), `estadistica` (2). La web modela la **materia**; el framework, la
  **asignatura semestral**. Ninguno lo declara.
- 8 fichas web (`algebra-lineal`, `calculo`, `optimizacion`, `power-bi`, `pre_*`, `sql`) no
  tienen curso; otras 30 tienen ficha con `draft: true`.
- `libraries/Banco_*` (7 bancos "compartidos") tienen **0 archivos**; la reutilización que
  prometen no ocurre. Lo compartido real (logo, fuentes, plantillas) se copia por sesión
  (19 copias de `cau_logo.png`).
- Superficie de referencias externas a las rutas actuales: 145 archivos citan
  `Academic_Class-`, 106 `course_NN_`, 82 `03_SESIONES` (learning-skill 28, fichas de
  catalogación 11, reportes de ingesta 8, `CLAUDE.md`, `temario.py`; el resto son bitácoras
  de `meta/reparaciones/`, que no se tocan).

**Riesgos si no se actúa**: exposición de datos de terceros en repos públicos (ya
ocurre); rechazo de push por tamaño; crecimiento del árbol vacío con cada curso nuevo
(+40 directorios por curso, +7 por sesión); divergencia web/framework; imposibilidad de
saber qué material existe sin abrir carpetas; 23 repos que nunca se sincronizan.

## 3. Principios de diseño

1. **La unidad de trabajo es el curso.** El área es una etiqueta del curso, no una carpeta
   ni un repo. Un curso puede pertenecer a varias áreas; una carpeta no.
2. **Estructura por necesidad, no por molde.** El núcleo obligatorio es mínimo (un
   registro YAML y un README generado); cada carpeta existe solo cuando tiene contenido.
   El validador rechaza lo desconocido y lo vacío, no exige lo ausente.
3. **La naturaleza determina la estructura** (ARQUITECTURA_DOCUMENTAL). Una sesión de
   laboratorio no tiene la forma de una clase magistral: el tipo se declara y el validador
   exige el artefacto propio de ese tipo. La pedagogía (antes/durante/después) vive en el
   esquema del documento (`guion.md`, `presentacion-clase`), no en subcarpetas.
4. **Una cosa, un lugar; lo compartido, por clave.** Libros por `calibre_id`, datasets por
   clave de `02 analysis`, plantillas/logo/fuentes desde el framework. Ninguna copia dentro
   del repo de contenido salvo lo autocontenido de un deck.
5. **Separar contenido · proceso · producto · registro.** Contenido (`cursos/`), proceso
   (`dictados/`: cuándo y cómo se dictó), producto (lo compilado/publicado: generado, no
   versionado, congelado por tag), registro (estudiantes, notas: repo privado).
6. **El nombre es identidad estable; el orden es metadato.** El slug de carpeta no lleva
   número de malla ni área; el orden se declara en `curso.yml` y las vistas lo muestran.
   El prefijo numérico solo donde el orden es intrínseco y fijo (subcarpetas del curso,
   sesiones).
7. **Una sola convención de nombres**: kebab-case ASCII en minúsculas para carpetas y
   archivos, `snake_case` para claves YAML (normativa §nombres). Sin excepciones fuera de
   `vendor/` y `_inbox/`.
8. **Fuente y vistas.** `curso.yml`, `sesion.yml`, `dictado.yml` son la fuente; README,
   índices, ficha web, temarios del learning-skill y checklists son generados y se
   regeneran, nunca se editan.
9. **Versionado proporcional.** Un repo de contenido (texto y código), un repo privado de
   registro, el framework aparte. Binarios > 5 MB fuera del repo o en LFS; artefactos de
   compilación nunca.
10. **Reversibilidad y trazabilidad por git**: tag antes, tag después, manifiesto de hashes
    para demostrar que ningún archivo se perdió, mapa de rutas viejas → nuevas versionado.

## 4. Propuesta de estructura reorganizada

### 4.1 Nivel `10 Class/`

```
10 Class/                         ← repo Academic_Class_Framework (tooling; sin cambio de fondo)
├── classes/ styles/ themes/ templates/ scaffolds/ scripts/ config/ docs/ bibliography/
├── docencia/                     ← UN submódulo: repo `Academic_Class` (contenido docente)
│   ├── cursos/<slug>/            ← qué se enseña (54 → ≈ 45 tras fusiones)
│   ├── dictados/<AAAA-ciclo>-<slug>/   ← cada vez que se dicta (manifiesto + producto)
│   ├── _inbox/<origen>/          ← legado por clasificar; temporal; el doctor avisa mientras exista
│   └── README.md                 ← índice generado: por área, por malla, por estado
└── registro/                     ← repo PRIVADO `Academic_Class_Registro`, git-ignorado aquí
    └── <AAAA-ciclo>-<slug>/      ← misma clave que el dictado
```

`areas/` y sus 23 submódulos desaparecen. `libraries/Banco_*` (vacíos) se retiran; lo que
prometían lo cubren Calibre, `02 analysis` y `templates/`.

### 4.2 El curso

```
cursos/econometria-i/
├── curso.yml            ← registro del curso (sucesor de temario.yml)
├── README.md            ← vista generada
├── 01-diseno/           ← sílabo, calendario, competencias, matriz de evaluación, rúbricas (academic-report)
├── 02-contenido/        ← apuntes: 1-2-tema.md (solo los escritos), img/
├── 03-sesiones/         ← s01-<slug>/ … (anatomía §4.3)
├── 04-evaluaciones/     ← *.tex academic-exam (12 tipos), banco/
└── 05-recursos/         ← datasets/ (≤ 5 MB), talleres/, plantillas/, vendor/, curso.bib
```

Reglas: `curso.yml` y `README.md` son lo único obligatorio; las cinco carpetas se crean al
primer uso; una carpeta fuera de esta lista o vacía es error del validador. Fusiones
respecto al 00–09: `00`+`01` → `01-diseno`; `05` → `registro/` (lo privado) o
`04-evaluaciones/ejemplos/` (consignas y trabajos modelo anonimizados); `07` → junto al
deck que lo usa o `05-recursos/media/`; `08` → `05-recursos/` (temas de investigación,
lecturas avanzadas); `09` → `dictados/`.

`curso.yml` (claves `snake_case`, normativa §7):

```yaml
# cursos/econometria-i/curso.yml — registro del curso econometria-i
id: econometria-i                 # = nombre de la carpeta
titulo: "Econometría I"
estado: borrador                  # borrador | activo | archivado
tipo: asignatura                  # asignatura | herramienta | nivelacion | taller
area: [estadistica, econometria]  # etiquetas; un curso puede tener varias
malla: {plan: economia-unsch, ciclo: 5, orden: 13}   # el antiguo NN vive aquí
materia_web: econometria          # ficha de 04 index/cursos/ (muchos cursos → una materia)
nivel: pregrado
prerrequisitos: [estadistica-para-economistas]
unidades: [...]                   # como hoy: id, titulo, temas[] con archivo opcional
bibliografia: [{calibre_id: 1234, ...}]
datasets: [{clave: inei/enaho/2019/sumaria, uso: "S01 pobreza"}]   # 02 analysis
ajeno: [05-recursos/vendor/plantilla-sbs]
```

### 4.3 La sesión: tipada por archivo, no por subcarpeta

```
03-sesiones/s07-series-temporales/
├── sesion.yml           ← id · titulo · tipo · estado · unidad · duracion_min · modalidad
├── deck.tex | deck.qmd  ← exigido si tipo: clase (assets hermanos en img/)
├── cuaderno.ipynb | script.do|.R|.py | libro.ods   ← exigido si tipo: laboratorio | taller
├── guion.md             ← plan de clase + notas del docente + retrospectiva (esquema presentacion-clase)
├── practica.*           ← actividad (opcional)
├── evaluacion.tex       ← opcional (academic-exam)
└── datos/ img/ recursos/ ← opcionales
```

`tipo ∈ {clase, laboratorio, taller, evaluacion}`. El validador exige el artefacto del
tipo, `sesion.yml` y `guion.md`; nada más. Las siete subcarpetas y los cuatro archivos
plantilla desaparecen: 47 de 67 sesiones no tenían deck y 55 tenían las subcarpetas
vacías. El arco antes/durante/después queda en las secciones de `guion.md`.

### 4.4 El dictado y el registro

```
dictados/2026-i-cau-unsch-metodologia/
├── dictado.yml          ← periodo, institucion, cursos[], sesiones[] {orden, curso, sesion}, web {materia, edicion}
├── cronograma.md
└── publicacion/         ← PRODUCTO de publish-session (git-ignorado); la web lo enlaza por hardlink
```

Congelar una sesión publicada = `git tag dictado/2026-i-cau-unsch-metodologia/s03` sobre
el commit de sus fuentes; no se copia nada. Un dictado puede tomar sesiones de varios
cursos (el caso real de Metodología 2026-I) sin vivir dentro de uno de ellos.

```
registro/2026-i-cau-unsch-metodologia/      ← repo privado, nunca con remote público
├── estudiantes.ods · asistencia.ods · calificaciones.ods
├── evaluaciones-aplicadas/ · evidencias/
```

### 4.5 Nomenclatura única

- Carpetas y archivos: `kebab-case` ASCII minúsculas. `cursos/econometria-i/`,
  `s07-series-temporales/`, `1-2-medicion-del-pib.md`, `deck.tex`.
- Prefijo numérico solo en las cinco carpetas fijas del curso (`01-…05-`) y en sesiones
  (`sNN-`). Ningún número en el slug del curso.
- Claves YAML `snake_case`; `id` = slug de la carpeta; `estado` del ciclo §2.1.
- Períodos: `AAAA-i` / `AAAA-ii` (minúsculas, ASCII), más institución y materia en el
  slug del dictado.
- Fuera de norma solo `vendor/` y `_inbox/`, excluidos del validador.

### 4.6 Relación con el ecosistema

| Necesidad | Antes | Después |
|---|---|---|
| Libros y artículos | copias en `06_RECURSOS` | `bibliografia[].calibre_id` (F5.4, sin cambio) |
| Datasets oficiales (ENAHO, INEI, Damodaran) | `.dta`/`.csv` en `02_Clase` | `datasets[].clave` → catálogo de `02 analysis`; el curso conserva solo muestras ≤ 5 MB |
| Logo, fuentes, plantillas | copiados por sesión | `assets/branding/`, `styles/`, `templates/` del framework; los decks siguen autocontenidos con **una** copia local del logo |
| Apuntes de Edison como alumno | `Languages`, inboxes | `01 notes/40-cursos-y-formacion/` (F5.0) |
| Ficha web | `web_slug` 1:1 fallido | `materia_web` n:1 declarado; `publish-web.sh` agrupa |
| Temarios del learning-skill | ruta por área | ruta por `cursos/<slug>` (`dominio_fuat` sin cambio) |

## 5. Justificación de los principales cambios

| Cambio | Evidencia | Criterio que satisface |
|---|---|---|
| Quitar la capa `Academic_Class-<Área>` y aplanar `cursos/<slug>` | 13/23 áreas con un solo curso; curso R/python partido; disciplina vs herramienta | claridad, escalabilidad (añadir curso = una carpeta), reutilización (etiquetas múltiples) |
| Un repo de contenido en vez de 23 | 18 remotes inexistentes, 5 sin push, 5 nombres heredados, 1,0 GB de `.git` | administración, trazabilidad (un commit por cambio transversal), automatización |
| Repo privado `registro/` | datos de terceros en 2 repos públicos; el estándar ya lo llamaba "privado" | separación, cumplimiento, sostenibilidad |
| Cinco carpetas bajo demanda, sin `.gitkeep` ni README de scaffold | 57 % de directorios vacíos; 145 README idénticos; `00/01/05/07/08` usados en ≤ 3 cursos | claridad, navegación, mantenimiento |
| Sesión tipada por archivo | 47/67 sin deck; 55/67 con anatomía vacía; laboratorios con `.ipynb`/`.do`/`.ods` | compatibilidad con flujos reales (LaTeX, Quarto, notebooks, hojas), naturaleza → estructura |
| Número de malla como metadato | dos semánticas de `NN`; 7 colisiones de `course_01_` | consistencia, estabilidad de rutas cuando cambia el plan |
| Dejar de generar esqueletos; `estado` veraz | 1 934 notas vacías `activo` | fiabilidad de Dataview, learning-skill y búsqueda |
| Congelar por tag, publicación como producto no versionado | 148 MB duplicados; PDF de 42,8 MB ×3 | reutilización sin duplicar, tamaño de repo |
| `dictados/` fuera del curso | el dictado 2026-I ya cruza 4 cursos | separación proceso/contenido, escalabilidad a talleres compuestos |
| Datasets por clave de `02 analysis` | `.dta` de 30 MB en sesiones; el ecosistema ya tiene capa de datos | una cosa en un lugar, automatización (enlazar.py F5.3) |
| Kebab único | 4 cajas en una ruta; 924 rutas con espacios | consistencia, scripts sin escapes |
| Retirar `libraries/Banco_*` | 0 archivos en 7 bancos | honestidad estructural: no prometer lo que no existe |

Lo que **no** cambia: la plataforma editorial, el motor LuaLaTeX, la idea de registro
YAML por curso/sesión/dictado, la publicación por hardlink a la web, Calibre por id, la
regla `vendor/`, el régimen de notas del vault, validador + doctor, reversibilidad por git.

## 6. Estrategia de migración (M0–M8)

Regla del ecosistema: `auditoría → propuesta → aprobación → backup → cambio → validación →
doctor → commit`, con simulación previa en cada fase. Cada fase termina con `validate.sh`
(reglas nuevas), `doctor.sh`, y un commit o tag.

**M0 · Congelar y medir.** Push de las 5 áreas atrasadas (crear antes los 18 repos que
faltan **o** decidir que no se crean: la consolidación los vuelve innecesarios). Tag
`pre-reorg-2026-09` en los 23 repos y en el framework. Manifiesto
`meta/reparaciones/R1_areas_2026-09/manifiesto_pre.sha256` con hash y ruta de los 4 695
archivos: es la prueba de no pérdida. Tarball de `_ESTANDARIZACION/` en la misma carpeta
(única copia del estado pre-estándar).

**M1 · Sacar lo que no es contenido docente** (sin renombrar nada aún).
- `05_ESTUDIANTES/*` con datos de terceros y `09_SEMESTRES/<p>/{estudiantes,calificaciones,evidencias,evaluaciones_aplicadas}` → `registro/` (repo privado nuevo). Hacer privados o archivar en GitHub `CampusTeX-Projects` y `econometric` hasta reescribir su historial.
- `Languages/_POR_REVISAR/*` → `01 notes/40-cursos-y-formacion/ingles/`.
- Datasets > 5 MB → catálogo de `02 analysis` (ingesta con clave); dejar en el curso la referencia.
- `_POR_REVISAR/inbox/*` y los 4 `03_temas/` → `docencia/_inbox/<área-origen>/` (LaTeX `03_Temas` es contenido de curso: va directo a sesiones del curso `latex`).
- `_ESTANDARIZACION/`: verificar por hash que cada archivo del backup existe en el árbol actual o en el tarball de M0; después borrar del árbol.

**M2 · Consolidar los 23 repos en `Academic_Class`.** Por área: `git filter-repo
--to-subdirectory-filter _migracion/<area>` sobre un clon, luego `git merge
--allow-unrelated-histories` en el repo nuevo. El historial de cada archivo se conserva
(`git log --follow`). Después `git filter-repo --strip-blobs-bigger-than 50M` (los blobs ya
están reubicados en M1). En el framework: quitar los 23 submódulos, añadir `docencia/` como
submódulo único. Archivar (solo lectura) los 5 repos públicos con un README que apunte al
nuevo; los 18 remotes inexistentes se eliminan del `.gitmodules`.

**M3 · Mapa de rutas y renombrado.** Generar `migracion/mapa.csv` (`ruta_vieja;ruta_nueva;
accion`) por script, revisarlo a mano (fusiones: R+python → `econometria-r-y-python`;
`00-curso-0` → `curso-0`; `Ofimatica/course_00` → `excel-avanzado` o el nombre que decida el
docente; `Estadistica/course_00` y `Gestion/course_00` se reparten entre sus cursos o van a
`_inbox`). Ejecutar con `git mv` (dry-run primero): `cursos/<slug>/`, `01-diseno … 05-recursos`,
`sNN-<slug>/`, kebab en todos los nombres (`normalizar-archivos.py nombres` ya hace la
transliteración). Borrar `.gitkeep`, README de scaffold (por hash contra `scaffolds/`) y las
notas esqueleto (cuerpo vacío **y** no listadas como escritas), conservando las 20 reales.

**M4 · Registros.** `temario.yml` → `curso.yml` (añadir `tipo`, `area[]`, `malla.orden` desde el
antiguo `NN`, `materia_web` desde `web_slug`, `datasets[]`); `metadata.yml` → `sesion.yml`
con `tipo` inferido (deck → `clase`; `.ipynb/.do/.R/.py` → `laboratorio`; `.ods/.xlsx` →
`taller`) y revisado; `dictado.yml` → `dictados/2026-i-cau-unsch-metodologia/`. Aplanar la
anatomía de sesión según el tipo. Reconstruir la edición web 2025-I como dictado
`2025-i-cau-unsch-metodologia` (fuente en el framework) o marcarla `legado: true` en su
`_metadata.yml`; no puede quedar como fuente huérfana.

**M5 · Herramientas.** Actualizar `scripts/lib/common.sh` (`is_course` = existe `curso.yml`;
`list_sessions` = `03-sesiones/s[0-9]*`), `validate.sh` (lista cerrada de carpetas,
prohibición de vacías, artefacto por `tipo`), `new-course.sh`/`new-session.sh` (sin
scaffold de carpetas; crean solo el registro y el artefacto del tipo), `temario.py` (ya no
genera esqueletos; `archivo` nulo hasta que la nota exista), `publish-session.sh` (producto
git-ignorado + tag), `publish-web.sh` (agrupa por `materia_web`), `enlazar.py`, `stats.sh`,
`doctor.sh` (avisa si `_inbox/` no está vacío, si hay binario > 5 MB, si `registro/` tiene
remote). Actualizar `.gitignore` (`publicacion/`, `.build/`, `*.mht`).

**M6 · Referencias externas.** Reescribir por script las 145 referencias a
`Academic_Class-`/`course_NN_`/`03_SESIONES` fuera de `areas/` (learning-skill 28,
`scripts_for_calibre/script_catalogacion_biblioteca/fichas` 11, `ingesta_cursos/reportes` 8,
`05 tasks/temarios-cursos.md`, `prompts/ECOSISTEMA_APRENDIZAJE.md`, `CLAUDE.md` del
workspace y de `10 Class`, `docs/09-estandar-00-09.md`, `_links.md` de `04 index/cursos`).
Las bitácoras de `meta/reparaciones/` no se tocan (son registro histórico).

**M7 · Verificación.** (1) Todo hash de `manifiesto_pre` existe en `manifiesto_post` o
figura en `eliminados.txt` con motivo (esqueletos, `.gitkeep`, README de scaffold,
duplicados de `publicacion/`, backup). (2) `validate.sh` y `doctor.sh` en 0 errores.
(3) Compilar tres decks (Beamer, Quarto, examen) y `quarto render` de `04 index/cursos`.
(4) `git log --follow` sobre cinco archivos elegidos al azar muestra historial previo a M2.
(5) `find docencia -type d -empty` vacío; `find docencia -name '* *'` vacío fuera de
`vendor/` y `_inbox/`. Tag `reorg-2026-09-done`.

**M8 · Lección escrita** (CICLO §5). Reemplazar `docs/09-estandar-00-09.md` por el
estándar nuevo (este §4 y §7), actualizar `CLAUDE.md` y `README.md` del framework, la
entrada tipo 22 de `ARQUITECTURA_DOCUMENTAL.md`, el prompt de `05 docencia/` que genera
sesiones, y una nota en `meta/DIAGNOSTICO_INTEGRAL_2026-09.md` (F5 cerrado con la nueva
forma). Este documento pasa a `estado: hecho` con enlace a la bitácora de reparaciones.

Orden y reversibilidad: M0 y M1 son reversibles por `git mv` inverso y por el tarball; M2
se hace sobre clones, los repos originales quedan intactos y archivados; M3–M6 llevan
`mapa.csv` versionado, que es también el `UNDO`. Ninguna fase borra un archivo cuyo hash
no esté probado en otro lugar.

## 7. Reglas para mantener la estructura

1. **Un curso = `cursos/<slug>/curso.yml`.** Se crea con `new-course.sh <slug> "Título"`; el
   script no crea carpetas, solo el registro y el README generado.
2. **Carpetas cerradas y no vacías.** Solo `01-diseno 02-contenido 03-sesiones
   04-evaluaciones 05-recursos`; existen cuando tienen contenido. Sin `.gitkeep`. Carpeta
   desconocida o vacía = error de `validate.sh`.
3. **Sesión = `sNN-<slug>/sesion.yml` con `tipo`.** El artefacto obligatorio lo fija el
   tipo (`deck.*`, `cuaderno.*`/`script.*`/`libro.*`, `evaluacion.tex`); `guion.md` siempre.
   Sin subcarpetas fijas. El número lo da la carpeta.
4. **Nombres**: kebab-case ASCII minúsculas para carpetas y archivos; `snake_case` para
   claves; `id` = carpeta; `estado` del ciclo. Excepciones solo `vendor/` y `_inbox/`.
5. **Edita la fuente, no la vista.** README, índices, ficha web, temarios del
   learning-skill y checklists se regeneran con `temario-generar.sh`; nunca a mano.
6. **Nada externo se copia.** Libros por `calibre_id`; datasets oficiales por clave de
   `02 analysis`; plantillas, logo y fuentes desde el framework. Dentro del curso solo
   material propio y muestras ≤ 5 MB. El doctor avisa de binarios mayores.
7. **Sin esqueletos.** Una nota existe cuando está escrita; `estado: activo` significa
   contenido real. `temario.py` no crea archivos vacíos.
8. **Producto ≠ fuente.** PDF, `publicacion/`, `.build/` y artefactos LaTeX no se
   versionan; congelar = tag `dictado/<clave>/<sesion>`. La web recibe hardlinks del
   producto y nunca es fuente.
9. **Datos de personas solo en `registro/`** (repo privado sin remote público), con la
   clave del dictado. Nada con nombres de estudiantes en `docencia/`.
10. **Un dictado = `dictados/<AAAA-ciclo>-<institucion>-<materia>/dictado.yml`**, aunque
    tome sesiones de varios cursos.
11. **`_inbox/` es temporal.** Todo lo que entra lleva carpeta de origen y fecha; el doctor
    avisa mientras no esté vacío; nada se cita desde un curso mientras siga allí.
12. **Cambios estructurales por el ciclo**: auditoría → propuesta → aprobación → tag →
    cambio con dry-run → validate → doctor → commit; mapa de rutas versionado como UNDO.
13. **Un repo de contenido, un commit por cambio.** No se crean repos por área ni por curso;
    si un curso necesita publicarse aparte, se exporta (subtree), no se separa.
14. **Cada curso nuevo o migrado declara `tipo`, `area[]`, `materia_web` y, si aplica,
    `malla`.** Sin ellos el validador no lo acepta (paralelo a "todo documento declara su
    esquema", 2026-09-11).

## 8. Ejecución

### M0 · Congelar y medir (2026-09-15, hecho)

- Tag `pre-reorg-2026-09` en los 23 repos de `areas/` y en el framework (hashes en
  `meta/reparaciones/R1_areas_2026-09-15_083347/`).
- Manifiesto `manifiesto_pre.sha256`: 6 098 rutas (4 695 archivos + 1 403 `.gitkeep`).
- Tarball `backup_ESTANDARIZACION_*.tar.gz`: 446 archivos, `gzip -t` correcto y tres entradas
  cotejadas por hash contra disco.
- **Decisión:** no se crean los 18 repos `Academic_Class-*` que faltaban en GitHub. M2 los vuelve
  innecesarios; la reversibilidad de esas áreas es local (tag + historial). Su `.gitmodules`
  se limpia en M2.
- `CampusTeX-Projects` y `econometric` pasaron a **privados** antes de cualquier push (contienen
  trabajos de estudiantes en su historial; M2 lo reescribe).
- **Pendiente para Edison:** el push de las 5 áreas con remote y del framework lo bloqueó el
  clasificador de permisos de la sesión. Comandos en el README de la reparación.

### M1 · Sacar lo que no es contenido docente (2026-09-15, hecho)

| Movimiento | Cantidad | Destino |
|---|---|---|
| Datasets ≥ 5 MB (`.dta`, `.csv`, shapefile con sus hermanos) | 20 archivos, 201 MB | `02 analysis/data/raw/_docencia_por_catalogar/<área>/<curso>/…` (no versionado; estado *por catalogar*) + `datos-reubicados.md` en cada carpeta de origen |
| Trabajos de estudiantes (`05_ESTUDIANTES/proyectos`) de Gestión empresarial, Estadística y Stata | 3 carpetas, 302 archivos | `10 Class/registro/_legado/<área>/…` (repo privado nuevo, sin remote) |
| Área Languages completa (`_POR_REVISAR/` y `06_RECURSOS/`, material ICPNA y Duolingo) | 8 carpetas + 25 archivos | `01 notes/40-cursos-y-formacion/ingles/` (F5.0) |
| `_POR_REVISAR/inbox` de 6 cursos base y los 4 `03_temas` de área | 198 archivos | `10 Class/docencia/_inbox/<área>/` (repo de contenido nuevo; será el submódulo único en M2) |
| `_ESTANDARIZACION/` | 446 archivos, 100 MB | borrado del árbol; íntegro en el tarball de M0 (217 hashes existían solo allí) |

Verificación: `manifiesto_post.sha256` (5 669 rutas) contiene **todos** los hashes del manifiesto
previo salvo los 217 justificados en `bitacora/eliminados.txt` (0 no justificados);
`validate.sh` 23/23 áreas sin errores; `doctor.sh` 0 fallos · 412 avisos (los avisos son los
binarios con nombre fuera de norma de siempre; la línea base M7 era 0 · 713).

Desviaciones respecto al plan de §6: (a) `LaTex/03_Temas` va a `_inbox/latex/`, no directamente a
sesiones del curso `latex` (crear sesiones es M3–M4); (b) los datasets no entran aún al catálogo
de datafw porque su procedencia no está verificada y datafw prohíbe metadatos inventados: quedan
en una raíz de entrada de la ingesta con `LEEME.md`; (c) los binarios grandes que **no** son datos
(tres `.mht` de Ofimática de 155 MB, PDF de 42,8 MB, talleres `.docx`, `.odp`) siguen en las áreas:
M2 no puede aplicar `--strip-blobs-bigger-than 50M` sin decidir antes LFS, conversión o Calibre para
ellos; (d) se sacó Languages entero, no solo su inbox, porque todo su contenido es material de alumno.

Bitácora completa, `UNDO.sh` y hashes de commits: `meta/reparaciones/R1_areas_2026-09-15_083347/`.

### M2 · Consolidar los 23 repos en `docencia/` (2026-09-15, hecho)

| Paso | Resultado |
|---|---|
| Clon + `git filter-repo --to-subdirectory-filter _migracion/<área> --tag-rename :<slug>/` por área | 23 clones; mismo número de commits que cada original |
| Merge `--allow-unrelated-histories` en `docencia/` | 315 commits (3 propios + 289 de las áreas + 23 merges) |
| Purga: blobs de `registro/_legado` por id + blobs > 50 MB | 0 blobs de estudiantes y 0 blobs > 50 MB en todo el historial; `.git` de 1,0 GB repartido → **601 MB** |
| Verificación de árboles (`arboles_pre/` vs `HEAD`) | 4 858 de 4 860 rutas idénticas por blob; las 2 restantes son los `.mht` > 50 MB, en disco sin versionar con puntero |
| Tags | 23 `<slug>/pre-reorg-2026-09` recreados sobre los commits reescritos vía `commit-map` |
| Web | 11 hardlinks de `04 index/cursos/…/2026-1-cau-unsch/` reenlazados a `docencia/` tras cotejar hash |
| Framework | 23 submódulos retirados; `docencia/` submódulo único (`../Academic_Class.git`); originales en `meta/reparaciones/R2_…/areas_originales/` |
| `validate.sh` / `doctor.sh` | 23/23 sin errores; 2 599 archivos · 0 fallos · 412 avisos (línea base de M1) |

Incidentes corregidos durante la fase, documentados en la bitácora: (1) la lista de blobs de
estudiantes contenía el blob vacío (tres trabajos de tamaño cero), y `filter-repo` retiró del
historial los 1 364 `.gitkeep`; se repusieron en HEAD (su historial previo se pierde, solo son
marcadores). (2) Tres archivos del docente compartían blob con material de estudiantes (dos casos de
ejercicios y un logo) y cayeron con la purga; repuestos en HEAD. (3) 274 carpetas del estándar
00–09 y de la anatomía de sesión existían en las áreas **solo vacías en disco**, nunca versionadas:
un clon limpio de los originales tampoco pasaba `validate.sh`; se crearon con `.gitkeep`.
(4) Los `.log` de Stata y los `.directory` no viajan: estaban ignorados por git en los originales.

Desviaciones respecto al plan de §6: no se archivan aún en GitHub los 5 repos públicos ni se crea el
remote de `Academic_Class`: ambos esperan el push de M0, que sigue bloqueado para esta sesión.
`.gitmodules` ya no tiene los 18 remotes inexistentes. Los scripts Python resuelven `AREAS` a
`docencia/_migracion` mientras `areas/` no exista (M5 lo rehace); `CLAUDE.md` lleva una nota de
migración al inicio (M6/M8 reescriben la documentación).

Bitácora, `UNDO.sh`, árboles y verificaciones: `meta/reparaciones/R2_consolidacion_2026-09-15_090152/`.

### M3 · Mapa de rutas y renombrado (2026-09-15, hecho)

| Paso | Resultado |
|---|---|
| `docencia/migracion/generar-mapa-m3.py` → `mapa-m3.csv` (versionado; es también el UNDO) | 5 135 filas: 1 338 `mover`, 3 797 `baja` con motivo; 0 conflictos de destino |
| `aplicar-mapa-m3.py --aplicar` (renombra con `rename`, mismo inodo) | 1 310 renombres detectados por git; hardlinks de la web 11/11 intactos |
| Cursos | 54 → 50 en `cursos/<slug>/` (`01-diseno`, `02-contenido` aplanado, `03-sesiones/sNN-<slug>`, `04-evaluaciones`, `05-recursos` con `media/` e `investigacion/`) |
| Bajas | 1 934 notas esqueleto · 1 601 `.gitkeep` · 174 plantillas de scaffold (cuerpo normalizado idéntico) · 46 archivos de área · 40 Languages · 2 fusión |
| `temario.yml` | rutas reescritas; `archivo: null` en los temas sin nota (M4 lo convierte en `curso.yml`) |
| Verificación | 1 273 movidos con blob idéntico (+2 `.mht` no versionados); 0 `.gitkeep`; 0 carpetas vacías; 16 carpetas con espacios, todas justificadas (vendor, geodatabase, rutas leídas por código) |
| Herramientas | `temario.py`, `enlazar.py`, `normalizar-*.py` ven `docencia/cursos/*`; `verificar` OK 50 cursos |

Pendiente que hereda M4: `09_SEMESTRES/2026-I` está en `dictados/2026-i-cau-unsch-metodologia/_migracion/<curso>/`;
la anatomía interna de sesión (`01_Antes…07_Notas`) sigue igual; `_inbox/` recibe además los dos cursos base
no repartidos (Estadística, Gestión empresarial). `validate.sh` (reglas 00–09) ya no aplica: M5 escribe las nuevas.
Decisiones de nombre y detalle en `meta/reparaciones/R3_renombrado_2026-09-15_094921/README.md`.

### M4 · Registros (2026-09-15, hecho)

| Paso | Resultado |
|---|---|
| `temario.yml` → `curso.yml` (`docencia/migracion/aplicar-m4.py`, mapa `mapa-m4.csv`) | 50: `tipo` (30 asignatura · 12 herramienta · 7 taller · 1 nivelación), `area[]`, `malla.orden` en los 25 cursos de la malla, `materia_web`, `prerrequisitos[]`, `datasets[]` (4 cursos, por catalogar), `alias` con el id antiguo |
| `metadata.yml` → `sesion.yml` | 67 con `tipo` inferido del artefacto (27 laboratorio · 20 taller · 20 clase) y `artefacto` declarado; 3 marcadas `revisar` |
| Anatomía de sesión aplanada | `02_Clase`, `03_Actividad` → raíz; `01_Antes`, `07_Notas`, `README.md` → `guion.md` (12 con contenido, 55 esqueleto `borrador`); 587 archivos con blob idéntico |
| Dictados | `dictados/2026-i-cau-unsch-metodologia/{dictado.yml, publicacion/<web>/}` (6 sesiones de 2 cursos; mismo inodo que la web, 11/11); `2025-i-cau-unsch-metodologia` como dictado legado y `legado: true` en la web |
| Herramientas | `temario.py`/`enlazar.py`/`normalizar-notas.py` leen `curso.yml` y resuelven `alias`; README regenerados: `verificar` OK 50 cursos |

Desviaciones respecto a §4.3: los artefactos conservan su nombre (`sesion.yml: artefacto`) en vez de `deck.tex`/`cuaderno.ipynb`,
y los subdirectorios de contenido de la sesión no se renombran (los leen `.do`, `.ipynb`, `index_files/`). Pendiente que hereda M5:
`validate.sh` con las reglas nuevas (lista cerrada de carpetas de curso, artefacto por tipo, `guion.md`, `_inbox` vacío),
`new-*.sh`, `publish-*.sh` y `stats.sh` sobre `curso.yml`/`sesion.yml`/`dictado.yml`. Detalle y decisiones en
`meta/reparaciones/R4_registros_2026-09-15_100908/README.md`.

### M5 · Herramientas (2026-09-15, hecho)

| Pieza | Cambio |
|---|---|
| `scripts/lib/common.sh` | `is_course` = existe `curso.yml`; `course_dir`/`dictado_dir` aceptan ruta o slug; `list_sessions` = `03-sesiones/s[0-9][0-9]-*`; `session_artifact`, `yaml_get`, `slugify` en kebab; sin `libraries/` |
| `validate.sh` | reglas §4: lista cerrada de carpetas de curso, sin vacías ni `.gitkeep`, `curso.yml`/`sesion.yml` con núcleo y `tipo`, `guion.md`, artefacto declarado y coherente con el tipo, dictados con sesiones existentes; `--todos` |
| `new-course.sh` · `new-session.sh` · `new-dictado.sh` | crean solo el registro y el artefacto del tipo (deck, cuaderno, evaluación); `new-period.sh` retirado; scaffolds 00–09 (89 archivos) sustituidos por `scaffolds/{curso,sesion,dictado}/` (8) |
| `new-presentation.sh` · `new-evaluacion.sh` · `new-report.sh` · `build-*.sh` | destinos `01-diseno/`, `04-evaluaciones/`, raíz de sesión; compilan el artefacto declarado |
| `publish-session.sh` · `publicar-web.py` | módulo `dictados/<clave>/publicacion/<web>/` (producto ignorado); congelar = tag `dictado/<clave>/<sesion>`; la web agrupa por `web.materia`; dictado `legado` no se publica |
| `temario.py` · `enlazar.py` · `normalizar-*.py` | leen `docencia/cursos/*/curso.yml`; sin esqueletos (`archivo: null` hasta que la nota exista); `migrar` escribe `curso.yml` |
| `doctor.sh` | además del entorno y la normativa: `validate --todos`, `temario verificar`, `enlazar verificar`, `_inbox/` no vacío, binarios > 5 MB, `registro/` con remote |
| `.gitignore` de docencia | `*.mht` (el de 15 MB deja de versionarse; sigue en disco) |

Pruebas: curso y dictado desechables con las cinco variantes de sesión (validate 0 errores; el validador detecta
el artefacto ausente), sílabo `academic-report` compilado con `build.sh`, ciclo `publish-session --refrescar` →
`publish-web --aplicar` sobre Metodología 2026-I con hashes idénticos y 11/11 hardlinks, normalizadores y
generadores en simulación, `doctor.sh` completo. Lección: `bash -n` solo comprueba el primer archivo que recibe.
Pendiente que hereda M7: los decks heredados con `%!TEX program = xelatex` y logo ausente (`cau-logo.png`) no
compilan; el compilador universal elige pdflatex para ellos. Bitácora en `meta/reparaciones/R5_herramientas_2026-09-15/`.

### M6 · Referencias externas (2026-09-15, hecho)

| Bloque | Qué se hizo |
|---|---|
| Rutas literales (`docencia/migracion/reescribir-referencias-m6.py`, mapa `mapa-m6.csv`) | resolutor que encadena las bitácoras M1 → M3 → M4 (con retroceso por carpeta y rutas con espacios): 364 referencias reescritas en las fichas de Calibre (11), los reportes e historial de `ingesta_cursos` (11), los apuntes de `01 notes/40-cursos` (enlaces al tema; 3 notas esqueleto retiradas → enlace al curso), una ficha de `03 writing`, `INTEGRACION_ECOSISTEMA.md`, el README del compilador; 44 líneas de identidad dentro de `docencia/cursos` pasan a su ruta actual |
| Código vivo | `meta/doctor/lib/chequeos.sh` y `temarios_calibre.py`, `meta/consultar/config.sh`, `scripts_for_fuentes/ingesta_cursos` (config, clasificar, ingestar, temario_bib, suite), `scripts_git_studio/repos-config.yml` (dos áreas → `10 Class/docencia`) leen `docencia/cursos/*/curso.yml`, `05-recursos` y `dictados/` |
| Prosa normativa | `CLAUDE.md` del workspace, `prompts/ECOSISTEMA_APRENDIZAJE.md`, `MEJORA_CONTINUA.md`, `METODO_DOCUMENTAL.md`, `prompt_09`, los cuatro prompts de `05 docencia`, `learning-skill` (SKILL, preset, acciones, 21 punteros de dominio; marca `<!-- curso.yml -->`), `meta/ARQUITECTURA.md`, `NORMATIVA_ARCHIVOS.md` (§ cursos y tabla de registros: curso · sesión · dictado), `MODELO_METADATOS.md`, `04 index/cursos/README.md` |
| Vistas regeneradas desde `curso.yml` | 27 fichas web («Contenidos / Sílabo»), 23 temarios del skill, `05 tasks/temarios-cursos.md`, README de los 50 cursos (15 títulos heredados del nombre de carpeta corregidos: `Stata — Curso Base` → `Stata`, etc.) |

Residuos que se dejan a propósito: bitácoras y diagnósticos históricos de `meta/`, `prompts/archive`, `meta/grafo` (instantánea),
los cursos tomados de `01 notes/40-cursos-y-formacion/inei_*` y `uni_*` (conservan su propio 00–09 interno: régimen del vault, no del
framework), los ids antiguos en los reportes de ingesta (registros; `curso.yml: alias` los resuelve), `datasets[].clave` de `curso.yml`
(reflejan la ruta real del aterrizaje en `02 analysis`), `docencia/_inbox` y `guion.md` (texto heredado), y los comentarios «Sucesor de».
`README.md`, `docs/09-estandar-00-09.md`, `docs/00-arquitectura.md` y el cuerpo de `CLAUDE.md` del framework describen aún el 00–09: M8.
Los posts de `04 index/_pubs` conservan `curso: <id antiguo>`; `alias` en `curso.yml` los resuelve (`enlazar.py verificar`: 0 desconocidos).
Bitácora: `meta/reparaciones/R6_referencias_2026-09-15/`.

### M7 · Verificación (2026-09-15, hecho)

| Comprobación (§6 M7) | Resultado |
|---|---|
| (1) No pérdida: cada hash del manifiesto de M0 (4 231 distintos, 6 098 rutas) existe hoy en `docencia/`, `registro/`, `01 notes/…/ingles`, `02 analysis/…/_docencia_por_catalogar` o el tarball de `_ESTANDARIZACION`, o su ruta tiene justificación en las bitácoras | 2 475 rutas sin su hash de M0, **0 sin justificar**: 1 934 notas esqueleto · 174 plantillas de scaffold · 46 archivos de área · 5 Languages/fusión (M3); 67 `sesion.yml`, 50 `curso.yml`, 1 `dictado.yml` transformados y 14 fusionados en `guion.md` (M4); 50 README regenerados; 122 archivos movidos y modificados después (identidad M6, registros); 11 artefactos de construcción ignorados por git que no viajaron en M2 y siguen en `areas_originales/` |
| (2) `validate.sh --todos` y `doctor.sh` | 0 errores (avisos: `_inbox/` 401 archivos, 9 binarios > 5 MB, 414 de normativa) |
| (3) Compilar tres decks y la web | Beamer `latex/s03` ✓ · Quarto RevealJS `seminario-de-investigacion/s02` ✓ · examen `econometria-i/…/2012_ea.tex` en modos examen, claves y soluciones ✓ · `quarto render` de la edición 2026-1 de Metodología 9/9 ✓ (tras entrecomillar 15 `titulo:` con dos puntos en `_links.md`, defecto previo) |
| (4) `git log --follow` en 5 archivos al azar | historial hasta 2026-07-23 (anterior a M2) en los cinco |
| (5) Carpetas vacías en `docencia/` | 0 (dos subcarpetas vacías de `publicacion/` que creaba `publish-session.sh`; ahora las crea bajo demanda) |
| (5) Nombres con espacios fuera de `vendor/` e `_inbox/` | 10 directorios y 317 archivos, todos justificados: adjuntos que la normativa admite (§4) y carpetas que leen `.do`, `.rmd` e `.ipynb` (`687 modulo 34`, `curso_r/sesion NN`, `curso_python/sesion NN`); no se renombran |
| Tag `reorg-2026-09-done` | `docencia/`, framework y `registro/` |

Hallazgo que hereda el docente: de los 20 decks Beamer heredados, 5 de los 6 probados no compilan (logo `cau-logo.png`
ausente o `%!TEX program = xelatex`), rotura anterior a la reorganización ya anotada en `CLAUDE.md`; el compilador universal
borra el PDF al fallar, así que se restauraron de git. La verificación completa está en `meta/reparaciones/R7_verificacion_2026-09-15/`.

### M8 · Lección escrita (2026-09-15, hecho)

| Pieza (§6 M8) | Qué se hizo |
|---|---|
| `docs/09-estandar-00-09.md` | `git mv` → `docs/09-estandar-docencia.md` (historial conservado) y reescrito con §4 y §7: dónde vive cada cosa, curso, sesión tipada, dictado y registro, nomenclatura, relación con el ecosistema, 14 reglas, herramientas |
| `README.md` del framework | reescrito: estructura por capas con `docencia/` y `registro/`, resumen del estándar, inicio rápido con la CLI de M5 (slug o ruta), tooling, convenciones, documentación |
| `CLAUDE.md` del framework | cuerpo reescrito (la nota «Migración en curso» pasa a «Reorganización 2026-09-15 (hecha)»; el bloque «Comandos» de M5 se conserva íntegro); estado real: 50 cursos, 67 sesiones, pendientes del docente y del usuario |
| `docs/00-arquitectura.md` | capa de contenido, árbol (`scaffolds/` como registros, `docencia/`, `registro/`, scripts actuales), tabla de responsabilidades, flujo de un documento y D5 actualizados; §1, §8 y §9 marcados como históricos (rediseño de julio) |
| `ARQUITECTURA_DOCUMENTAL.md` | fila del tipo 22 y tabla «Sistema que lo implementa»: el esquema es el estándar de docencia (`curso.yml`, `sesion.yml` + `guion.md` + artefacto, `dictado.yml`) |
| `05 docencia/` | `prompt_02_diseno_de_sesion` llena `sesion.yml` y `guion.md` (no la anatomía); `prompt_01` (comando y normativo); preset `apuntes_clase` (rutas); `README.md` regenerado |
| `meta/` | `DIAGNOSTICO_INTEGRAL_2026-09.md`: F5 cerrada con la nueva forma y F5a superada; `NORMATIVA_ARCHIVOS.md` (`05-recursos/vendor/`, `02-contenido`), `ARQUITECTURA.md`, `MODELO_METADATOS.md`, `consultar/README.md` |
| Restos vivos | `CLAUDE.md` del workspace, `ECOSISTEMA_APRENDIZAJE.md` (6 pasajes), `01 notes/40-cursos-y-formacion/README.md`, `core/archivos.py` (A14 reconoce `02-contenido`), `temario.py`, `temario-generar.sh`, `ingesta_cursos/config.sh`, `02 analysis/docs/INTEGRACION_ECOSISTEMA.md` |
| Este documento | `estado: hecho`; cabecera con el enlace a las bitácoras |

Se dejan a propósito, por históricos: `MIGRACION_LUALATEX.md`, `new-period.sh` (aviso de retiro), §1/§8/§9 de
`00-arquitectura.md`, los diagnósticos y planes anteriores de `meta/`, `PROGRESO.md`, los reportes TSV y fichas de
Calibre (registros) y `prompt_09` (sus «pasos 00–09» son los del Método Documental, no este estándar).
Bitácora: `meta/reparaciones/R8_leccion_2026-09-15_121422/` (copias previas en `antes/`, parches por repo, `UNDO.sh`).

**Remote de `docencia/`.** Se revisaron los 56 repos de `achalmed` para no crear uno nuevo: `MyTestProyect` (ensayo de
tutorial de 2025, un README y un logo, sin referencias locales) se renombró a `achalmed/Academic_Class` y se puso privado;
`docencia/` ya lo tiene como `origin`. Los pasos de red (M0 a las 5 áreas con remote, push de `docencia/` con sus 25 tags,
push del framework, archivo de los 5 repos heredados) quedan en `R8_…/subir-remotos.sh` porque el clasificador del modo
automático no permite `git push`; `areas_originales/` se borra después de verificar el push.

**Push hecho (usuario, 2026-09-15).** El primer intento por HTTPS falló por falta de token (los 5 remotes se cambiaron a SSH) y el
segundo se cortó por red a mitad de los 600 MB de `docencia/`; el script pasó a subir por tramos de 40 commits con reintentos y
keepalive. Resultado verificado: `Academic_Class` `main` = `49589af` con los 25 tags y sin ramas de prueba; framework `main` =
`origin/main`; las 5 áreas con remote reciben M0 (`main` + `pre-reorg-2026-09`) y quedan archivadas en GitHub con nota. Hallazgo:
las refs `pre-reorg-2026-09` y `reorg-2026-09-done` del framework habían desaparecido (los objetos tag seguían colgantes) y se
restauraron con `update-ref`; el remote no tiene tags, así que falta `git push origin --tags` en el framework. Las bitácoras R1–R8
están versionadas en `meta` (`areas_originales/` git-ignorado). Queda al usuario borrar `areas_originales/` (1,6 GB).
