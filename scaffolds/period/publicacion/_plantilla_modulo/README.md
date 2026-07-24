# _plantilla_modulo — Plantilla de un módulo MOOC (una sesión)

> Esqueleto de **un módulo del MOOC** = **una sesión publicada** de este dictado.
> **Copia esta carpeta** por cada sesión que publiques, con el nombre de la sesión:

```bash
cp -a _plantilla_modulo S01_introduccion      # mismo nombre que 03_SESIONES/S01_introduccion
```

Al publicarse, el módulo queda **congelado** (no se vuelve a editar).

## Contenido del módulo

| Elemento | Qué es |
|---|---|
| `index.md` | la **página del módulo** (objetivos + enlaces a las 4 partes) |
| [`slides/`](slides/README.md) | diapositivas finales de la sesión |
| [`evaluation/`](evaluation/README.md) | examen propuesto **+ su solución** |
| [`practice/`](practice/README.md) | práctica final |
| [`homework/`](homework/README.md) | tarea final |

Los archivos finales se **enlazan por hardlink** desde su fuente (`03_SESIONES`,
`04_EVALUACIONES`); ver [`../README.md`](../README.md).

## Nomenclatura

- Carpeta del módulo: `S<NN>_<slug>` (idéntica a la sesión en `03_SESIONES/`).
- El prefijo `_` de `_plantilla_modulo` la marca como plantilla (no se publica).
