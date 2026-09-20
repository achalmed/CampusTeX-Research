---
tipo: readme
estado: activo
---
# config/ — los datos del docente y la paleta espejada

Dos archivos con dueños distintos: uno se edita a mano y el otro **nunca**.

## Uso

```bash
$EDITOR config/course.yml                 # identidad del curso, docente, institución, logo, idioma
cd ~/Documents/sistema-editorial && python3 generador.py verificar   # ¿palette.tex diverge del tema?
cd ~/Documents/sistema-editorial && python3 generador.py generar --aplicar --espejo   # regenerarla
```

## Estructura

| Archivo | Qué es | Dueño / generador |
|---|---|---|
| `course.yml` | fuente única de la identidad del curso: curso, código, ciclo, docente, institución, `logo`, tema Beamer, aspecto, idioma. Lo leen los scripts `new-*` al rellenar plantillas | el autor |
| `palette.tex` | la paleta Academic: los once nombres `academic*`, de los que `styles/academic-colors.sty` deriva sus siete roles. **GENERADO** desde `sistema-editorial/temas/docencia.yml` y espejado aquí; lleva la marca `GENERADO … no editar` en la línea 1 | `sistema-editorial/generador.py` (Fase 6, 2026-09-20) |

## Límite honesto

- **`course.yml` es YAML plano y así debe quedarse**: los scripts lo parsean con `grep`/`sed`, no con
  un parser de YAML. No anidar estructuras en las claves marcadas `[script]`.
- **`palette.tex` no se edita**: cualquier cambio a mano se pierde en la siguiente generación. El
  color se cambia en `sistema-editorial/temas/docencia.yml`, que es donde vive la decisión.
- Todo parámetro nuevo de compilación o de identidad va a `course.yml`, nunca dentro de
  `scripts/lib/common.sh`.
