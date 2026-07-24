# examen_final — Exámenes finales y sustentaciones

> Exámenes del **momento final** (cierre del curso) y **exámenes orales /
> sustentaciones** (defensa con rúbrica de jurado).

- **Plantillas:** `08-examen-oral` (destino por defecto del script); además cualquier
  examen final de estructura desarrollo/objetivo/problemas se **mueve aquí** desde
  `examen_parcial/` cuando el momento es final.
- **Sigla:** `EF` (final), `ES` (sustitutorio), `EA` (aplazado), `EU` (suficiencia);
  `OR`/`EO` para el oral.

## Nomenclatura

`AAAAMMDD_EF[-NN].tex`, `AAAAMMDD_OR.tex`. Ej.: `20260716_EF.tex`.

## Crear

```bash
# Final de problemas: se andamia como examen-problemas y se mueve aquí
./scripts/new-evaluacion.sh "$COURSE" examen-problemas "Examen Final" --fecha 20260716
mv "$COURSE/04_EVALUACIONES/examen_parcial/20260716_EP.tex" \
   "$COURSE/04_EVALUACIONES/examen_final/20260716_EF.tex"
# Sustentación oral:
./scripts/new-evaluacion.sh "$COURSE" examen-oral "Sustentación Final"
```

## Ejemplo — carpeta

```
examen_final/
├── 20260716_EF.tex / .pdf
└── 20260720_OR.tex          ← protocolo + preguntas guía + rúbrica de jurado
```
