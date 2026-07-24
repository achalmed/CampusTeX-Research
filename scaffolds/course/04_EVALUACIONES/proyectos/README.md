# proyectos — Casos de estudio y proyectos

> Evaluaciones de **caso de estudio** y **proyectos**: análisis de una situación,
> interpretación de datos, gráficos (pgfplots) y tablas. Trabajo integrador, a menudo
> grupal.

- **Plantilla:** `09-caso-estudio` (`CASO`). Es la **única** que añade `pgfplots`
  (excepción documentada) para graficar dentro del `.tex`.
- Si el caso usa datos reales, aplica el **expediente `code/`** (ver
  [README de 04_EVALUACIONES](../README.md)).

## Nomenclatura

`AAAAMMDD_CASO[-NN].tex`. Ej.: `20260630_CASO.tex`.

## Crear

```bash
./scripts/new-evaluacion.sh "$COURSE" caso-estudio "Caso — Inflación 2020–2024" --fecha 20260630
```

## Ejemplo — carpeta

```
proyectos/
├── 20260630_CASO.tex / .pdf
└── code/                     ← si el caso se resuelve con datos reales
    ├── 20260630_CASO.py · data/data.xlsx · figures/ · table/
```
