# 00_ADMINISTRACION — Documentos oficiales del curso

> **Responsabilidad única:** la **gestión formal** del curso frente a la universidad
> y los estudiantes. Lo que la escuela pediría o firmaría: sílabo, calendario, actas,
> oficios, registros de asistencia.

## Organización:

```
00_ADMINISTRACION/
    syllabus.pdf

    calendario.xlsx

    horario.md

    normativa.pdf

    lista_estudiantes.xlsx

    asistencia.xlsx

    grupos.xlsx

    correo_estudiantes.csv
```

## Qué va aquí

- **Sílabo** del curso (`silabo.tex` → `silabo.pdf`), documento oficial.
- **Calendario / cronograma** académico (`calendario.tex`).
- **Actas de notas**, cargos de entrega del sílabo, registros de asistencia.
- **Oficios, memorandos, convalidaciones**, correspondencia con la escuela.

## Qué NO va aquí

- El **diseño instruccional interno** (objetivos, secuencia, rúbricas de trabajo) →
  [`01_PLANIFICACION/`](../01_PLANIFICACION/README.md).
- Las **evaluaciones** (exámenes, prácticas) → [`04_EVALUACIONES/`](../04_EVALUACIONES/README.md).
- Datos de un **dictado concreto** (esta lista de asistencia real, estas notas
  finales) → [`09_SEMESTRES/<periodo>/`](../09_SEMESTRES/README.md).

## Cómo se crea el sílabo y el calendario

```bash
./scripts/new-report.sh "$COURSE" silabo      "Sílabo del curso"      # → 00_ADMINISTRACION/silabo.tex
./scripts/new-report.sh "$COURSE" calendario  "Calendario académico"  # → 00_ADMINISTRACION/calendario.tex
./scripts/build.sh "$COURSE/00_ADMINISTRACION/silabo.tex"
```

Ambos usan la clase `academic-report` (misma identidad visual que exámenes y
diapositivas). Los metadatos (docente, universidad, periodo) se rellenan desde
`config/course.yml`.

## Nomenclatura

- Documentos generados por el script: nombre fijo (`silabo.tex`, `calendario.tex`).
- Documentos administrativos sueltos: `snake_case` con fecha al frente si aplica —
  `20260315_acta_notas.pdf`, `oficio_042_convalidacion.pdf`.

## Ejemplo — `acta_notas.md` (contenido de muestra)

> El acta real suele ser un PDF firmado o una hoja de cálculo; aquí se muestra su
> contenido en Markdown para revisión rápida.

```markdown
# Acta de Notas — Sistema APA (course_00_sistema_apa)
Periodo: 2026-I · Docente: Edison Achalma B.Sc. Econ. · UNSCH

| Código    | Estudiante            | Parcial | Final | Prácticas | Promedio |
|-----------|-----------------------|:-------:|:-----:|:---------:|:--------:|
| 20231001  | Apellido, Nombre      |   16    |  17   |    18     |  17.0    |
| 20231002  | Apellido, Nombre      |   13    |  15   |    14     |  14.0    |

Fecha de cierre: 2026-07-20 · Firma del docente: __________________
```
