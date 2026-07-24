# 01_PLANIFICACION/rubricas — Rúbricas genéricas del curso

> Rúbricas **reutilizables** que no pertenecen a una sola evaluación: participación en
> clase, exposición oral, informe escrito, trabajo en equipo. Se aplican a lo largo
> del curso.

## Qué va aquí vs. `04_EVALUACIONES/rubricas/`

| Aquí (`01_PLANIFICACION/rubricas/`) | En [`04_EVALUACIONES/rubricas/`](../../04_EVALUACIONES/README.md) |
|---|---|
| Rúbrica **transversal** (participación, exposición) | Rúbrica **de un examen/práctica concreto** |
| Se reutiliza en muchas sesiones | Acompaña a una evaluación puntual |

> `new-report.sh rubrica` deposita la rúbrica en `04_EVALUACIONES/rubricas/`
> (rúbrica ligada a evaluación). Las genéricas de aquí se redactan a mano o se copian
> de esa plantilla.

## Nomenclatura

- `snake_case` describiendo el objeto evaluado: `rubrica_exposicion.pdf`,
  `rubrica_participacion.md`, `rubrica_informe.tex`.

## Ejemplo — `rubrica_exposicion.md` (contenido de muestra)

```markdown
# Rúbrica de Exposición Oral (0–20)

| Criterio            | Excelente (5) | Bueno (3–4) | En proceso (0–2) |
|---------------------|---------------|-------------|------------------|
| Dominio del tema    | Preciso y profundo | Correcto | Con vacíos |
| Uso de fuentes APA  | Cita todo bien | Cita casi todo | Cita mal/omite |
| Claridad y orden    | Muy claro | Claro | Confuso |
| Manejo del tiempo   | Ajustado | Leve desvío | Fuera de tiempo |
```
