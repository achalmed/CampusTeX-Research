# 08_INVESTIGACION — Vínculo docencia ↔ investigación

> **Responsabilidad única:** el puente entre el curso y la **investigación**: papers de
> referencia avanzada, datasets de investigación, notebooks de análisis, casos de
> estudio de fuente y las referencias bibliográficas (`.bib`) del curso.

## Subcarpetas

| Subcarpeta | Contiene |
|---|---|
| [`papers/`](papers/README.md) | artículos de investigación (base de casos avanzados) |
| [`datasets/`](datasets/README.md) | datos de investigación (crudos/procesados) |
| [`notebooks/`](notebooks/README.md) | notebooks de análisis (`.ipynb`, `.Rmd`, `.qmd`) |
| [`casos/`](casos/README.md) | casos de estudio con su documentación fuente |
| [`referencias/`](referencias/README.md) | archivos `.bib` / exportes de Zotero del curso |

## Qué NO va aquí

- Datasets **para enseñar** (demos) → `06_RECURSOS/datasets/`.
- Datos que **resuelven una evaluación** → `04_EVALUACIONES/.../code/data/`.
- El caso como **evaluación** (`.tex`) → `04_EVALUACIONES/proyectos/`.

## Relación con la bibliografía del framework

Los `.bib` de `referencias/` pueden apuntar (o copiarse) desde
`~/Documents/10 Class/bibliography/`. Mantén un solo origen de verdad
por referencia.

## Ejemplo — carpeta

```
08_INVESTIGACION/
├── papers/keynes_1936.pdf
├── datasets/encuesta_hogares_2023.csv
├── notebooks/analisis_pobreza.ipynb
└── referencias/curso.bib
```
