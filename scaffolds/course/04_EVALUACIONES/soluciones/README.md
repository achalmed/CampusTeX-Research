# soluciones — Solucionarios formales

> Solucionarios **formales con portada** (formato de documento propio), para cuando se
> pide entregar el solucionario como pieza independiente en vez de compilar el examen
> en modo `[soluciones]`.

- **Plantilla:** `12-solucionario` (`SOL`).
- **Regla:** normalmente **no** se usa esta carpeta — el mismo `.tex` del examen ya
  genera el solucionario con `\documentclass[soluciones]{academic-exam}` (o
  `build.sh … --modo soluciones`). Reserva `soluciones/` solo para el solucionario
  **formal con portada** que se pida por separado.

## Nomenclatura

`AAAAMMDD_SOL.tex`. Ej.: `20260716_SOL.tex`.

## Ejemplo — carpeta

```
soluciones/
└── 20260716_SOL.tex / .pdf      ← solucionario formal con portada (uso alternativo)
```

> Para el caso habitual (solucionario del propio examen), ver el modo `[soluciones]`
> en el [README de 04_EVALUACIONES](../README.md).
