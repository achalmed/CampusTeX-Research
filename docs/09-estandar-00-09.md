---
tipo: doc
titulo: "09 · El estándar 00–09 (organización de los Academic_Class)"
estado: activo
---
# 09 · El estándar 00–09 (organización de los Academic_Class)

> Referencia del contrato de carpetas que respetan **todos** los
> `~/Documents/Academic_Class-<Área>`. El resumen vive en el `README.md`; este
> documento lo detalla. La fuente de verdad **arquitectónica** (capas LaTeX,
> `styles/`, clases, tema Beamer) es [`00-arquitectura.md`](00-arquitectura.md).

## Contenedor de área → cursos

Un `Academic_Class-<Área>` (p. ej. `Academic_Class-Estadistica`) es un
**contenedor de cursos**, no un curso. Contiene directamente carpetas
`course_NN_<slug>/`, una por asignatura o edición. Los scripts de `scripts/`
reciben la **ruta del curso** como argumento; los cursos reales **no** viven en
el framework.

## Las 10 carpetas 00–09 de cada curso

Cada `course_NN_<slug>/` tiene **exactamente 10 carpetas** (prefijo numérico
`00`–`09`, nombres ASCII) + su `README.md`:

```
00_ADMINISTRACION   Sílabo, calendario, datos administrativos del curso.
01_PLANIFICACION    Planificación docente (notas de docente, diseño del curso).
02_CONTENIDO        Material por unidad (Unidad_NN/); aquí viven los apuntes de estudio.
03_SESIONES         Una carpeta SNN_<slug>/ por sesión de clase (ver anatomía abajo).
04_EVALUACIONES     Exámenes y prácticas (academic-exam); rubricas/ dentro.
05_ESTUDIANTES      Listas, seguimiento y datos de estudiantes (privado).
06_RECURSOS         Recursos de apoyo, manuales, material auxiliar.
07_MULTIMEDIA       Imágenes, audio, vídeo y otros binarios.
08_INVESTIGACION    Material de investigación asociado al curso.
09_SEMESTRES        Un subdirectorio por dictado (ver abajo).
```

El prefijo numérico fija el orden y hace el estándar navegable y programable.
Carpetas vacías llevan `.gitkeep`.

## Anatomía de una sesión (`03_SESIONES/SNN_<slug>/`)

Cada sesión sigue **7 subcarpetas** con el arco de una clase:

```
01_Antes       Preparación previa a la clase (lecturas, requisitos).
02_Clase       El deck de la sesión (.tex Beamer o .qmd); assets hermanos del deck.
03_Actividad   Actividad o práctica en aula.
04_Evaluacion  Evaluación puntual de la sesión.
05_Despues     Cierre y material posterior a la clase.
06_Recursos    Recursos específicos de la sesión.
07_Notas       Notas del docente sobre el dictado.
```

Cada sesión trae además `metadata.yml` (registro de la sesión: línea 1 de identidad y núcleo `id` · `titulo` · `estado`; el número lo da la carpeta `SNN`) + `README.md`. **El deck va en
`02_Clase/`** y es autocontenido (preámbulo propio + copia local del logo): al
mover una sesión, se mueve su carpeta **completa**.

## Qué guarda `09_SEMESTRES/`

`09_SEMESTRES/<AAAA-ciclo>/` (p. ej. `2026-II/`) es **cada dictado concreto** del
curso. Reúne dos cosas:

- **Registro privado** del dictado: listas de estudiantes, calificaciones y
  evidencias de esa edición.
- **Publicación** (`publicacion/SNN/`): el MOOC por sesión, que se **congela**
  poco a poco como instantánea de solo lectura conforme avanza el semestre
  (ver `publish-session.sh`).

Fusiona las antiguas `09_PUBLICACION`/`10_ARCHIVO`/`11_SEMESTRES` en un único
lugar por período.

## Herramientas del estándar

`new-course.sh` crea el esqueleto 00–09 (desde `scaffolds/course`),
`new-session.sh` una sesión (desde `scaffolds/session`), `new-period.sh` un
dictado en `09_SEMESTRES/`, y `validate.sh` verifica los invariantes 00–09
(exit != 0 si algo no cumple). Detalle de cada script en el `README.md`.
