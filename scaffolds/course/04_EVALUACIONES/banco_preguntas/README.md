# banco_preguntas — Banco de preguntas del curso

> Repositorio de preguntas **por tema y nivel de Bloom**, con claves. Fuente de la que
> se arman exámenes; no es una evaluación que se rinda tal cual.

- **Plantilla:** `11-banco-de-preguntas` (`BP`). Usa el segundo argumento `[tema]` de
  `\begin{pregunta}[puntos][tema]` para el nivel de Bloom (recordar, comprender,
  aplicar, analizar…).

## Nomenclatura

`banco_<tema>.tex` o `AAAAMMDD_BP.tex` si es una versión fechada del banco.
Ej.: `banco_citas_apa.tex`.

## Crear

```bash
./scripts/new-evaluacion.sh "$COURSE" banco-de-preguntas "Banco — Citación APA"
```

## Ejemplo — carpeta

```
banco_preguntas/
├── banco_citas_apa.tex        ← preguntas etiquetadas por tema/nivel Bloom, con claves
└── banco_referencias.tex
```
