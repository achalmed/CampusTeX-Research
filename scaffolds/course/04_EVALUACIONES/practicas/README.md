# practicas — Prácticas calificadas y dirigidas

> Prácticas: la **calificada** (PC, se nota) y la **dirigida** (PD, guiada, con
> ejercicio modelo resuelto + propuestos).

- **Plantillas:** `04-practica-calificada` (`PC`), `05-practica-dirigida` (`PD`).
- **Diferencia clave:** la dirigida usa el entorno `{desarrollo}` (ejercicio modelo
  resuelto en clase) además de los `{ejercicio}` propuestos; la calificada es
  evaluación con puntaje.

## Nomenclatura

`AAAAMMDD_PC[-NN].tex` · `AAAAMMDD_PD[-NN].tex`. Ej.: `20260410_PC.tex`.

## Crear

```bash
./scripts/new-evaluacion.sh "$COURSE" practica-calificada "Práctica Calificada 03" --fecha 20260410
./scripts/new-evaluacion.sh "$COURSE" practica-dirigida   "Práctica Dirigida 02"
```

## Ejemplo — carpeta

```
practicas/
├── 20260410_PC.tex / .pdf         ← práctica calificada 03
├── 20260410_PC-soluciones.pdf
└── 20260327_PD.tex                ← práctica dirigida (modelo + propuestos)
```
