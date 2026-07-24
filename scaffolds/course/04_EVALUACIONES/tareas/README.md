# tareas — Tareas domiciliarias y controles de lectura

> Trabajo **fuera del aula**: tareas domiciliarias (con condiciones de entrega) y
> controles de lectura (comentario crítico de un texto).

- **Plantillas:** `10-tarea` (`TA`/`TAR`), `07-control-de-lectura` (`CL`).
- La tarea lleva **condiciones de entrega y criterios**; el control de lectura,
  **rúbrica** de comentario de texto.

## Nomenclatura

`AAAAMMDD_TA[-NN].tex` · `AAAAMMDD_CL[-NN].tex`. Ej.: `20260418_TA.tex`.

## Crear

```bash
./scripts/new-evaluacion.sh "$COURSE" tarea              "Tarea 05 — Referencias APA" --fecha 20260418
./scripts/new-evaluacion.sh "$COURSE" control-de-lectura "Control de Lectura 02"
```

## Ejemplo — carpeta

```
tareas/
├── 20260418_TA.tex / .pdf        ← tarea domiciliaria (entrega + criterios)
└── 20260502_CL.tex               ← control de lectura (rúbrica de comentario)
```
