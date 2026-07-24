# 01_PLANIFICACION — Diseño instruccional del curso

> **Responsabilidad única:** cómo está **pensado y planificado** el curso (no cómo se
> administra ante la universidad, eso es `00_`). Aquí vive el diseño: competencias,
> secuencia didáctica, nota del docente, matriz de evaluación y las **rúbricas
> genéricas** reutilizables entre sesiones.

## Organización:

    01_PLANIFICACION/
        competencias.md
        resultados_aprendizaje.md
        unidades.md
        cronograma.md
        plan_semanal.xlsx
        mapa_curricular.pdf
        rúbricas/
    
        checklist_docente.md 

## Qué va aquí

- **Nota del docente** (`nota-docente.tex`): la visión del curso, enfoque pedagógico,
  decisiones de diseño.
- **Matriz / plan de evaluación**: qué pesa cuánto, qué se evalúa y cuándo.
- **Secuencia didáctica** global, mapa de competencias → sesiones.
- [`rubricas/`](rubricas/README.md): rúbricas **genéricas del curso** (participación,
  exposición, informe) reutilizables por varias sesiones o evaluaciones.

## Qué NO va aquí

- El **sílabo oficial** y el calendario → [`00_ADMINISTRACION/`](../00_ADMINISTRACION/README.md).
- La rúbrica **de una evaluación concreta** → [`04_EVALUACIONES/rubricas/`](../04_EVALUACIONES/README.md).
- El plan de una **sesión** puntual (`lesson_plan.md`) → `03_SESIONES/SNN/01_Antes/`.

## Cómo se crea la nota docente

```bash
./scripts/new-report.sh "$COURSE" nota-docente "Nota del docente"   # → 01_PLANIFICACION/nota-docente.tex
```

Usa la clase `academic-report`.

## Ejemplo — `plan_evaluacion.md` (contenido de muestra)

```markdown
# Plan de Evaluación — Sistema APA

| Instrumento          | Peso | Semana | Carpeta destino                    |
|----------------------|:----:|:------:|------------------------------------|
| Examen parcial       | 30%  |   8    | 04_EVALUACIONES/examen_parcial/    |
| Examen final         | 30%  |  16    | 04_EVALUACIONES/examen_final/      |
| Prácticas calificadas| 25%  | 3–15   | 04_EVALUACIONES/practicas/         |
| Tareas / control lect| 15%  | var.   | 04_EVALUACIONES/tareas/            |

Competencia general: aplica normas APA 7 con integridad académica.
```
