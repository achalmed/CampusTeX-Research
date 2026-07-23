# Academic_Class · Estándar de organización de cursos

> Repositorio **canónico** del estándar de carpetas, archivos y nomenclatura para
> **todas** las carpetas `~/Documents/Academic_Class-*` — cualquier asignatura
> universitaria (Economía, Matemática, Estadística, Programación, Investigación, …).
> Este repo, además de definir el estándar, **aloja lo compartido** (`_PLANTILLAS/`,
> `_BIBLIOTECA/`) y **produce los dos entregables LaTeX de cada curso**:
> **diapositivas** de clase (Beamer, en `03_SESIONES/`) y **evaluaciones**
> (exámenes/prácticas, en `04_EVALUACIONES/` — ver [`evaluaciones/`](evaluaciones/README.md)).
>
> Docente: **Edison Achalma B.Sc. Econ.** · Idioma de todo el contenido: **español**.

La idea rectora: **pensar como una universidad, no como un profesor que solo guarda
archivos**. Lo compartido (plantillas, bancos) vive **una sola vez** aquí en el
framework; cada `Academic_Class-<Area>` es un **contenedor de cursos**; y lo que
cambia cada vez que se dicta un curso se separa dentro de `11_SEMESTRES/`.

---

## Índice

1. [Filosofía: los 4 niveles de trabajo](#1-filosofía-los-4-niveles-de-trabajo)
2. [Arquitectura: framework + cursos + semestres](#2-arquitectura-framework--cursos--semestres)
3. [Lo compartido (vive en este framework)](#3-lo-compartido-vive-en-este-framework)
4. [La estructura 00–11 de cada curso](#4-la-estructura-0011-de-cada-curso)
5. [Anatomía de una sesión (01_Antes…07_Notas)](#5-anatomía-de-una-sesión)
6. [11_SEMESTRES (cada dictado)](#6-11_semestres-cada-dictado)
7. [Nomenclatura de archivos](#7-nomenclatura-de-archivos)
8. [Convenciones técnicas](#8-convenciones-técnicas)
9. [Flujo de trabajo](#9-flujo-de-trabajo)
10. [Recetas: crear cosas nuevas](#10-recetas-crear-cosas-nuevas)
11. [Tooling del framework](#11-tooling-del-framework)
12. [Estado de despliegue](#12-estado-de-despliegue)

---

## 1. Filosofía: los 4 niveles de trabajo

Todo curso, en cualquier asignatura, se descompone en cuatro planos. La estructura
física (sección 2) da un hogar claro a cada uno:

| Plano | Qué es | Dónde vive |
|---|---|---|
| **1. Gestión** | Planificación del curso: qué se enseña y cómo se evalúa | `00_ADMINISTRACION/`, `01_PLANIFICACION/` |
| **2. Enseñanza** | El material que preparas (canónico, reutilizable) | `02_CONTENIDO/`, `03_SESIONES/`, `06_RECURSOS/`, `07_MULTIMEDIA/` |
| **3. Sesión** | Lo que ocurre en cada clase | `03_SESIONES/SNN/` |
| **4. Evaluación y evidencias** | Lo que producen los estudiantes | `04_EVALUACIONES/` (instrumentos) + `11_SEMESTRES/` (evidencias reales) |

---

## 2. Arquitectura: framework + cursos + semestres

Tres planos físicos, cada uno con un dueño claro:

```
Academic_Class_Framework/            ◀── COMPARTIDO · este repo (sirve a TODOS los Academic_Class)
├── _PLANTILLAS/                     ←   esqueletos vacíos para copiar
├── _BIBLIOTECA/                     ←   bancos compartidos (preguntas, ejercicios, imágenes…)
└── (tooling: scripts/ docs/ config/ templates/ bibliography/ assets/)

Academic_Class-<Area>/               ◀── CANÓNICO · el Academic_Class ES el contenedor de cursos
├── course_00_<slug>/                    (cada curso, con su estructura 00–11)
│   ├── 00_ADMINISTRACION/  …  10_ARCHIVO/
│   └── 11_SEMESTRES/            ◀── DICTADOS · cada vez que se imparte ESE curso
│       └── 2026-I/                  (listas, notas, evidencias de ese periodo)
└── course_NN_<slug>/
```

Cada plano resuelve un requisito real:

| Requisito | Solución |
|---|---|
| «lo compartido no se duplica en cada asignatura» | `_PLANTILLAS/` + `_BIBLIOTECA/` viven **solo** en el framework |
| «varios cursos por asignatura» | el `Academic_Class-<Area>` contiene `course_NN_<slug>/` directamente |
| «un curso se dicta 2×/año o varias veces en años» | `course_NN/11_SEMESTRES/<periodo>/` — el curso canónico **no se duplica**, solo se **instancia** |

> **Regla anti-redundancia.** Material que sirve a **más de un curso** → `_BIBLIOTECA/`
> (framework). Material de **un solo curso** → `06_RECURSOS/` o `08_INVESTIGACION/` de
> ese curso. Datos de **un dictado concreto** → `11_SEMESTRES/<periodo>/`.

---

## 3. Lo compartido (vive en este framework)

### `_PLANTILLAS/` — esqueletos vacíos para copiar

No se editan; se **copian** hacia un `Academic_Class`. Garantizan que todo
curso/sesión/dictado nazca con la estructura correcta.

| Plantilla | Qué contiene | Función |
|---|---|---|
| `Plantilla_Curso/` | árbol 00–11 completo, vacío | crear un curso nuevo |
| `Plantilla_Sesion/` | anatomía `01_Antes…07_Notas` + plantillas con `{{PLACEHOLDERS}}` (metadata, plan de clase, deck `.tex`/`.qmd`, notas, links) | crear una sesión nueva |
| `Plantilla_Periodo/` | esqueleto de un dictado | crear un periodo dentro de `11_SEMESTRES/` |
| `Plantilla_Examen/` · `Plantilla_Practica/` · `Plantilla_Rubrica/` · `Plantilla_Caso/` · `Plantilla_Lectura/` | documento base (quiz, guía de práctica, rúbrica, caso, guía de lectura) | documentos consistentes |

### `_BIBLIOTECA/` — bancos compartidos por todos los cursos

Material reutilizable **guardado una sola vez** para todas las asignaturas:

| Banco | Qué contiene |
|---|---|
| `Banco_Preguntas/` | preguntas reutilizables (exámenes/quizzes) |
| `Banco_Ejercicios/` | ejercicios reutilizables |
| `Banco_Diapositivas/` | slides/plantillas de diapositiva |
| `Banco_Casos/` | casos de estudio |
| `Banco_Datasets/` | conjuntos de datos |
| `Banco_Imagenes/` | figuras, logos, diagramas |
| `Banco_Lecturas/` | lecturas/PDF de referencia |
| `Bibliografia/` | `.bib` maestro |

---

## 4. La estructura 00–11 de cada curso

Cada `course_NN_<slug>/` (directamente bajo un `Academic_Class-<Area>/`) tiene
**exactamente estas 12 carpetas + README** (existan o no aún los archivos):

```
course_NN_<slug>/
├── README.md            ← ficha del curso
├── 00_ADMINISTRACION/
├── 01_PLANIFICACION/
├── 02_CONTENIDO/
├── 03_SESIONES/
├── 04_EVALUACIONES/
├── 05_ESTUDIANTES/
├── 06_RECURSOS/
├── 07_MULTIMEDIA/
├── 08_INVESTIGACION/
├── 09_PUBLICACION/
├── 10_ARCHIVO/
└── 11_SEMESTRES/        ← cada dictado del curso (ver §6)
```

### Qué contiene y qué función cumple cada carpeta

| # | Carpeta | Qué contiene | Función |
|---|---|---|---|
| 00 | **ADMINISTRACION** | `syllabus/`, `calendario/`, horario, normativa base | Datos administrativos **canónicos**. Lo por-dictado va en `11_SEMESTRES/`. |
| 01 | **PLANIFICACION** | competencias, resultados, unidades, cronograma, `rubricas/`, `lineamientos/` | El **diseño** del curso: qué se aprende y cómo se mide. |
| 02 | **CONTENIDO** | `Unidad_01/ … Unidad_NN/` (con `lecturas/`, `figuras/`) | El **saber** del curso, por unidades. |
| 03 | **SESIONES** | una carpeta `SNN_<slug>/` por sesión (ver §5) | El **desarrollo de cada clase**. |
| 04 | **EVALUACIONES** | `diagnostica/ practicas/ laboratorios/ tareas/ proyectos/ examen_parcial/ examen_final/ banco_preguntas/ soluciones/ rubricas/` | Los **instrumentos** de evaluación. |
| 05 | **ESTUDIANTES** | `entregas/ proyectos/ exposiciones/ retroalimentacion/` | **Plantilla**; los datos reales de cada dictado van en `11_SEMESTRES/`. |
| 06 | **RECURSOS** | `libros/ articulos/ videos/ software/ datasets/ talleres/` | Material propio de **este** curso (si sirve a varios → `_BIBLIOTECA/`). |
| 07 | **MULTIMEDIA** | `imagenes/ diagramas/ audio/ videos/ animaciones/ logos/` | Activos multimedia del curso. |
| 08 | **INVESTIGACION** | `papers/ casos/ datasets/ notebooks/ referencias/`, `topics/` | Profundización e investigación. |
| 09 | **PUBLICACION** | `aula_virtual/ moodle/ classroom/ github/ web/ pdf_finales/` | Lo que se **publica** (versión final canónica). |
| 10 | **ARCHIVO** | histórico del curso | Nada se borra; lo viejo se archiva. |
| 11 | **SEMESTRES** | `<periodo>/` por cada dictado (ver §6) | Instancias del curso a lo largo del tiempo. |

---

## 5. Anatomía de una sesión

Cada `03_SESIONES/SNN_<slug>/` sigue el **flujo real de una clase**:

```
SNN_<slug>/
├── metadata.yml · README.md   ← ficha e índice de la sesión
├── 01_Antes/       ← objetivos, plan de clase, guion (preparación)
├── 02_Clase/       ← diapositivas + ejemplos (el deck y sus assets)
├── 03_Actividad/   ← trabajo en aula
├── 04_Evaluacion/  ← quiz y solución de la sesión
├── 05_Despues/     ← tarea, lecturas posteriores
├── 06_Recursos/    ← enlaces, datasets de la sesión
└── 07_Notas/       ← notas del docente, retrospectiva
```

| Carpeta | Función |
|---|---|
| `01_Antes/` | Lo que preparas **antes** de entrar |
| `02_Clase/` | Lo que **proyectas** en clase (deck `.tex`/`.qmd` + imágenes) |
| `03_Actividad/` | Lo que hacen los estudiantes **en** clase |
| `04_Evaluacion/` | Cómo mides lo aprendido en la sesión |
| `05_Despues/` | Lo que dejas **para después** |
| `06_Recursos/` | Apoyo específico de la sesión |
| `07_Notas/` | Memoria docente para mejorar el curso |

---

## 6. 11_SEMESTRES (cada dictado)

Un curso se **imparte varias veces**. Cada dictado tiene su carpeta dentro del
propio curso, con **solo lo que cambia ese periodo** — el contenido canónico
(00–10) **no se duplica**:

```
course_NN_<slug>/11_SEMESTRES/<AAAA-ciclo>/
├── estudiantes/            ← lista, asistencia, grupos, correos
├── calificaciones/         ← notas del periodo
├── evaluaciones_aplicadas/ ← la versión concreta del examen usada este dictado
├── evidencias/             ← entregas/ proyectos/ exposiciones/
├── cronograma/             ← ajustes al cronograma de este dictado
└── publicacion/            ← lo subido a aula_virtual/moodle/classroom este periodo
```

Formato del periodo: `AAAA-<ciclo>` → `2026-I`, `2026-II`, `2027-I`, …

---

## 7. Nomenclatura de archivos

El **mayor problema a 5–10 años no es la estructura, son los nombres**
(`Clase1.pdf`, `Examen bueno.tex`, `final2 FINAL.pdf`). El estándar los hace
ordenables, entendibles sin abrir, y automatizables.

### Patrón jerárquico (dentro de la carpeta del curso)

```
U<unidad>_S<sesion>_<TIPO>[_<AAAAMMDD>]_v<NN>.ext
```

Ejemplo: `U02_S05_SLD_v01.pdf` = Unidad 2 · Sesión 5 · Diapositivas · versión 1.

El **código del curso** se antepone **solo cuando el archivo sale de su carpeta**
(correo, repositorio, banco común). Dentro del curso, la carpeta ya da el contexto.

### Abreviaturas de TIPO

| | | | |
|---|---|---|---|
| `SYL` syllabus | `CRON` cronograma | `PLAN` planificación | `COMP` competencias |
| `RA` result. aprendizaje | `PCL` plan de clase | `SLD` diapositivas | `GUI` guía |
| `EJE` ejercicios | `SOL` solucionario | `ACT` actividad | `TAR` tarea |
| `QZ` quiz | `PRA` práctica | `LAB` laboratorio | `TAL` taller |
| `EP` examen parcial | `EF` examen final | `RUB` rúbrica | `BP` banco preguntas |
| `BE` banco ejercicios | `DATA` datos | `LEC` lectura | `ART` artículo |
| `LIB` libro | `REF` referencias | `BIB` bibliografía | `IMG` imagen |
| `VID` video | `CODE` código | `SCR` script | `NOT` notas docente |

### Versionado

Usar `v01`, `v02`, … **nunca** `final`, `final2`, `ultimo`. Reserva `vNN` para
versiones oficiales que distribuyas; el borrador diario lo gestiona Git.

### Ejemplos

```text
# Una clase completa (Unidad 2, Sesión 5)
U02_S05_PCL.md   U02_S05_SLD.tex   U02_S05_SLD.pdf   U02_S05_GUI.pdf
U02_S05_EJE.pdf  U02_S05_SOL.pdf   U02_S05_QZ.pdf    U02_S05_TAR.pdf

# Una evaluación
U02_EP_ENU.tex   U02_EP_SOL.tex    U02_EP_RUB.pdf
```

---

## 8. Convenciones técnicas

- **Nombres ASCII** en carpetas (`rubricas`, `articulos`, `imagenes` — sin tildes):
  portabilidad Windows/Linux/macOS y compatibilidad con scripts.
- **`.gitkeep`** marca las carpetas vacías para que sobrevivan en Git.
- **Reversibilidad**: los árboles `Academic_Class-*` **no** son repos Git; por eso
  toda reorganización deja un **backup** de lo migrado y scripts `UNDO` en
  `_ESTANDARIZACION/`. Verificar integridad por conteo de archivos (antes = después).
- **Homogeneidad total**: al estandarizar, se convierte **todo** al estándar
  (incluida la anatomía interna de sesiones); si algún deck deja de compilar, se
  reconstruye — el estándar tiene prioridad.
- **Dry-run primero** en herramientas que mutan archivos; `bash -n` para chequear
  sintaxis de los scripts.

---

## 9. Flujo de trabajo

```
Planificación → Preparación → Presentación → Actividad → Evaluación
     ↓              ↓              ↓             ↓            ↓
01_PLANIFIC.   02_CONTENIDO   03_SESIONES   03_SESIONES   04_EVALUAC.
                               /02_Clase     /03_Activid.
                                                              ↓
                     Archivo ← Publicación ← Retroalimentación
                        ↓          ↓               ↓
                   10_ARCHIVO  09_PUBLIC.    11_SEMESTRES/<periodo>/evidencias
```

---

## 10. Recetas: crear cosas nuevas

Con los **scripts** del framework (rellenan metadatos y eligen formato del deck):

```bash
cd ~/Documents/Academic_Class_Framework
AC=~/Documents/Academic_Class-<Area>

./scripts/new-course.sh  "$AC" NN "Título del curso"                 # curso 00–11
C="$AC/course_NN_<slug>"
./scripts/new-session.sh "$C" NN "Título de la sesión" [--quarto]    # sesión SNN_slug
./scripts/new-period.sh  "$C" 2026-II                               # dictado en 11_SEMESTRES
./scripts/validate.sh    "$C"                                       # comprobar estructura
```

O a mano, copiando el esqueleto: `cp -a _PLANTILLAS/Plantilla_Curso "$AC/course_NN_<slug>"`.

---

## 11. Tooling del framework

Automatización **alineada al estándar 00–11**. Los scripts reciben la **ruta del
curso** (los cursos viven fuera del framework) y operan sobre `_PLANTILLAS/`.

| Ruta | Qué es |
|---|---|
| `config/course.yml` | valores por defecto del docente (identidad, logo, tema, compilador) — YAML plano |
| `scripts/lib/common.sh` | lógica compartida: colores, `config_get`, `slugify`, `latex_engine`, `compile_tex`, helpers de curso/sesión |
| `scripts/new-course.sh` | crea un curso 00–11 (`ACADEMIC_CLASS_DIR NN "Título"`) |
| `scripts/new-session.sh` | crea una sesión (`COURSE_DIR NN "Título" [--quarto]`) |
| `scripts/new-period.sh` | crea un dictado en `11_SEMESTRES/` (`COURSE_DIR AAAA-ciclo`) |
| `scripts/validate.sh` | valida 00–11 (`COURSE_DIR` o `ACADEMIC_CLASS_DIR`) |
| `scripts/stats.sh` · `build-session.sh` · `build-course.sh` | resumen y compilación (deck en `02_Clase/`) |
| `scripts/new-evaluacion.sh` · `build-evaluacion.sh` | crear/compilar exámenes en `04_EVALUACIONES/` (ver `evaluaciones/`) |
| `evaluaciones/` | sistema LaTeX de evaluaciones: `evaluacion.cls` + 12 plantillas + muestras |
| `scripts/clean.sh` · `doctor.sh` | limpiar auxiliares LaTeX · chequeo de entorno |
| `assets/branding/` | logo institucional canónico |

```bash
./scripts/doctor.sh                       # diagnóstico del entorno (LaTeX, Quarto)
./scripts/validate.sh <curso>             # valida la estructura 00–11
bash -n scripts/*.sh scripts/lib/*.sh     # chequeo de sintaxis
```

- **LaTeX Beamer** es el formato estándar de diapositivas (motor autodetectado); los
  decks Quarto RevealJS (`.qmd`) se renderizan con `quarto render`.

---

## 12. Estado de despliegue

El estándar aplica a los **23** `Academic_Class-*` del workspace (Macroeconomia,
Microeconomia, Finanzas, Gestion-empresarial, Gestion-publica, Math, Estadistica,
Eviews, Gretl, Stata, Spss, R, Geogebra, python, Programming-concepts, Bash, Git,
LaTex, Ofimatica, Filosofia, Languages, Metodologia-investigacion, 00-curso-0).

| Academic_Class | Estado |
|---|---|
| **Metodologia-investigacion** | ✅ **Piloto** — 4 cursos con estructura 00–11, sesiones separadas, `11_SEMESTRES/2026-I`, backup + `UNDO` |
| Los otros 22 | ⏳ pendientes de estandarizar |

### Documentación adicional

| Documento | Contenido |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Diseño y decisiones (tooling) |
| [docs/workflow.md](docs/workflow.md) | Flujo semestral |
| [docs/session-creation.md](docs/session-creation.md) | Crear y preparar una sesión |
| [docs/teaching-guide.md](docs/teaching-guide.md) | Manual para docentes |
| [docs/developer-guide.md](docs/developer-guide.md) | Manual técnico |
| [docs/automation.md](docs/automation.md) | Referencia de scripts |
| [docs/templates.md](docs/templates.md) | Referencia de plantillas |
