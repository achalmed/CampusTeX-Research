# laboratorios — Laboratorios de software y código

> Evaluaciones basadas en **software/código**: R, Python, Stata, EViews. Enunciado con
> salidas de consola, simulación y programación. Casi siempre traen **expediente
> `code/`** con datos y figuras reproducibles.

- **Plantilla:** `06-laboratorio`. **Sigla:** `LB` (prompt) / `LAB` (script).
- Usa los entornos `{codigo}[language=R|Python|Stata]` y `{salida}` de la clase.

## Expediente reproducible (lo habitual aquí)

```
laboratorios/
├── 20260605_LB.tex / .pdf
└── code/
    ├── 20260605_LB.py        ← corre con: python code/20260605_LB.py
    ├── data/data.xlsx        ← nombre de datos estándar
    ├── figures/              ← gráficos → \includegraphics{code/figures/…}
    └── table/                ← tablas .tex → \input{code/table/…}
```

El nombre citado en el `.tex` (`\texttt{data.xlsx}`) **debe** coincidir con el archivo
real en `code/data/`. Ver la sección «Expediente reproducible» del
[README de 04_EVALUACIONES](../README.md).

## Crear

```bash
./scripts/new-evaluacion.sh "$COURSE" laboratorio "Laboratorio 04 — Regresión en R" --fecha 20260605
python "$COURSE/04_EVALUACIONES/laboratorios/code/20260605_LB.py"   # genera figuras/tablas
./scripts/build.sh "$COURSE/04_EVALUACIONES/laboratorios/20260605_LB.tex" --modo todos
```
