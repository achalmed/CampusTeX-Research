# examen_parcial — Exámenes parciales

> Exámenes del **momento parcial** (durante el curso), en cualquiera de las tres
> estructuras: desarrollo, objetivo o problemas.

- **Plantillas que aterrizan aquí:** `01-examen-desarrollo`, `02-examen-objetivo`,
  `03-examen-problemas` (destino por defecto de `new-evaluacion.sh`).
- **Sigla:** `EP` (parcial). Un examen genérico usaría `EX`.
- **Momento vs. estructura:** si el mismo formato se usa para un **final**, el archivo
  va a [`examen_final/`](../examen_final/README.md); aquí solo lo **parcial**.

## Nomenclatura

`AAAAMMDD_EP[-NN].tex` — `20260521_EP.tex`, `20260521_EP-02.tex` (dos parciales el
mismo día).

## Crear

```bash
./scripts/new-evaluacion.sh "$COURSE" examen-problemas "Examen Parcial" --fecha 20260521
./scripts/build.sh "$COURSE/04_EVALUACIONES/examen_parcial/20260521_EP.tex" --modo todos
```

## Ejemplo — contenido esperado de la carpeta

```
examen_parcial/
├── 20260521_EP.tex        ← examen + solucionario (una fuente, 3 modos)
├── 20260521_EP.pdf        ← compilado (modo examen)
└── 20260521_EP-soluciones.pdf
```
