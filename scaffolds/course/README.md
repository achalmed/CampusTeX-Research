# course/ — Estándar 00–09 de un curso

> **Esqueleto de un `course_NN_<slug>/`.** Un `Academic_Class-<Área>/` es un
> **contenedor de cursos**; cada curso tiene **10 carpetas 00–09** + `README.md` y
> sigue esta organización idéntica en toda asignatura. Este árbol es la copia fiel de
> ese estándar, con un `README.md` documentado en cada carpeta.
>
> *(En un curso real, `new-course.sh` regenera el `README.md` del curso; este archivo
> es la guía del estándar para que lo leas aquí.)*

---

## Las 10 carpetas (qué vive en cada una)

| Carpeta | Contiene | Documento típico | Se crea con |
|---|---|---|---|
| [`00_ADMINISTRACION`](00_ADMINISTRACION/README.md) | sílabo, calendario, actas, oficios, asistencia | `silabo.tex`, `calendario.tex` | `new-report.sh silabo\|calendario` |
| [`01_PLANIFICACION`](01_PLANIFICACION/README.md) | diseño del curso: nota docente, secuencia, [`rubricas/`](01_PLANIFICACION/rubricas/README.md) genéricas | `nota-docente.tex` | `new-report.sh nota-docente` |
| [`02_CONTENIDO`](02_CONTENIDO/README.md) | el temario en Markdown, por `Unidad_NN/` | `N M titulo.md` | a mano |
| [`03_SESIONES`](03_SESIONES/README.md) | una carpeta `SNN_<slug>/` por clase (deck en `02_Clase/`) | `diapositivas.tex` | `new-session.sh` + `new-presentation.sh` |
| [`04_EVALUACIONES`](04_EVALUACIONES/README.md) | **exámenes, prácticas, tareas, bancos** (academic-exam) | `AAAAMMDD_SIGLA.tex` | `new-evaluacion.sh` |
| [`05_ESTUDIANTES`](05_ESTUDIANTES/README.md) | consignas y trabajos modelo (atemporales) | (archivos del alumno) | a mano |
| [`06_RECURSOS`](06_RECURSOS/README.md) | bibliografía y material de apoyo (manuales, guías) | `manual.tex`, `guia.tex` | `new-report.sh manual\|guia` |
| [`07_MULTIMEDIA`](07_MULTIMEDIA/README.md) | imágenes, diagramas, audio, video, logos | `.png`, `.svg`, `.mp4` | a mano |
| [`08_INVESTIGACION`](08_INVESTIGACION/README.md) | papers, datasets, notebooks, casos de investigación | `.pdf`, `.ipynb`, `.csv` | a mano |
| [`09_SEMESTRES`](09_SEMESTRES/README.md) | cada dictado: **registro privado + publicación** (MOOC por sesión, congelado) | `2026-I/`, `2026-II/` | `new-period.sh` |

**Regla de oro (00–08 atemporal vs 09 por dictado):** las carpetas **00–08** son el
material **canónico y atemporal** del curso (se mejora dictado a dictado, no se
duplica). **`09_SEMESTRES`** guarda lo **específico de cada dictado** —esta lista de
alumnos, estas notas, estas evidencias— **y** su **publicación** (el MOOC, que se
congela sesión a sesión). Ver [`09_SEMESTRES/`](09_SEMESTRES/README.md).

> **Nota histórica:** `09_SEMESTRES` **fusiona** las tres carpetas del estándar anterior
> (`09_PUBLICACION` + `10_ARCHIVO` + `11_SEMESTRES`), que se duplicaban. Ahora publicación,
> archivo y registro de dictado viven juntos por semestre.

---

## Nomenclatura

- Carpeta del curso: `course_NN_<slug>` (`course_00_sistema_apa`). `NN` con dos
  dígitos; ordena los cursos dentro del `Academic_Class-<Área>`.
- Las 10 carpetas **no se renombran, no se borran, no se reordenan**: son el
  contrato que `validate.sh` verifica. Si una no aplica a un curso, se deja vacía
  (con su `README.md`).
- Subcarpetas internas: `snake_case` ASCII (ver el README de cada una).

---

## Validación

```bash
./scripts/validate.sh <ACADEMIC_CLASS_DIR | COURSE_DIR>
```

Comprueba que existan las 10 carpetas 00–09 + `README.md`, y que cada sesión tenga su
anatomía. Sale con código ≠ 0 si algo falta.

---

## Ejemplo — un curso real ya poblado

```
Academic_Class-Metodologia-investigacion/
└── course_00_sistema_apa/
    ├── README.md
    ├── 00_ADMINISTRACION/        silabo.pdf
    ├── 01_PLANIFICACION/         nota-docente.pdf · rubricas/
    ├── 02_CONTENIDO/             Unidad_01/ … Unidad_06/   (temario .md)
    ├── 03_SESIONES/              S01_introduccion/ … S06_referencias/
    ├── 04_EVALUACIONES/          examen_parcial/ practicas/ tareas/ …
    ├── 05_ESTUDIANTES/ … 08_INVESTIGACION/
    └── 09_SEMESTRES/             2026-I/   (registro privado + publicación MOOC)
```
