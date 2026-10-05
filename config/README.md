---
tipo: readme
estado: activo
---
# config/ — los datos del docente y la paleta espejada

Dos archivos con dueños distintos: uno se edita a mano y el otro **nunca**.

## Uso

```bash
$EDITOR config/course.yml                 # identidad del curso, docente, institución, logo, idioma
```

`palette.tex` se regenera y se verifica desde `sistema-editorial`: las órdenes y el contrato están en
`sistema-editorial/docs/consumidores.md` §2 y §4.

## Estructura

| Archivo | Qué es | Dueño / generador |
|---|---|---|
| `course.yml` | fuente única de la identidad del curso: curso, código, ciclo, docente, institución, `logo`, `tema_beamer` y `aspecto` (los usa el `deck.tex` de `new-session.sh`), idioma. Lo leen los scripts `new-*` al rellenar plantillas | el autor |
| `palette.tex` | la paleta Academic: los once nombres `academic*`, de los que `styles/academic-colors.sty` deriva sus siete roles, y `\academicbn` (salida en gris). **GENERADO** desde `sistema-editorial/temas/docencia.yml` y espejado aquí; lleva la marca `GENERADO … no editar` en la línea 1 | `sistema-editorial/generador.py` |

## Límite honesto

- **`course.yml` es YAML plano y así debe quedarse**: los scripts lo parsean con `grep`/`sed`, no con
  un parser de YAML. No anidar estructuras en las claves marcadas `[script]`.
- **`palette.tex` no se edita**: cualquier cambio a mano se pierde en la siguiente generación. El
  color se cambia en `sistema-editorial/temas/docencia.yml`, que es donde vive la decisión.
- Todo parámetro nuevo de compilación o de identidad va a `course.yml`, nunca dentro de
  `scripts/lib/common.sh`.
- La clave `compilador:` apunta al compilador universal de `scripts-latex`; qué espera de él este
  repo está en `scripts-latex/docs/arquitectura.md` §Consumidores.
