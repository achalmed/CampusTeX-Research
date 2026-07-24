# 04_EVALUACIONES/rubricas — Rúbricas de evaluación

> Rúbricas **ligadas a una evaluación concreta** (la de este examen, esta práctica,
> este proyecto). Es el destino de `new-report.sh rubrica`.

## Qué va aquí vs. `01_PLANIFICACION/rubricas/`

| Aquí | En [`01_PLANIFICACION/rubricas/`](../../01_PLANIFICACION/rubricas/README.md) |
|---|---|
| Rúbrica de **una** evaluación puntual | Rúbrica **transversal** del curso |
| Acompaña a un `.tex` de `04_EVALUACIONES` | Se reutiliza en muchas sesiones |

## Crear

```bash
./scripts/new-report.sh "$COURSE" rubrica "Rúbrica — Proyecto Final"   # → 04_EVALUACIONES/rubricas/rubrica.tex
./scripts/build.sh "$COURSE/04_EVALUACIONES/rubricas/rubrica.tex"
```

Usa la clase `academic-report` (misma identidad visual que el examen que evalúa).

## Ejemplo — `rubrica_proyecto_final.md` (contenido de muestra)

```markdown
# Rúbrica — Proyecto Final (0–20)

| Criterio                  | Peso | Descriptor de logro máximo            |
|---------------------------|:----:|---------------------------------------|
| Planteamiento del problema | 4   | Claro, pertinente, bien delimitado    |
| Metodología               |  6   | Rigurosa y adecuada a los datos       |
| Resultados y discusión    |  6   | Correctos, interpretados en contexto  |
| Formato APA y redacción   |  4   | Impecable, sin errores de citación    |
```
