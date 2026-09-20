---
tipo: readme
estado: activo
---
# classes/ — las clases de documento: lo único que un `.tex` elige

Cada clase es **delgada**: encapsula el diseño cargando `styles/` y no define identidad propia. Un
documento del framework empieza siempre por `\documentclass{academic-*}` y a partir de ahí solo
rellena contenido (`docs/arquitectura.md`).

## Uso

```latex
\documentclass{academic-exam}        % evaluación
\documentclass[bn]{academic-exam}    % la misma, en blanco y negro (llama \academicbn)
\documentclass{academic-report}      % sílabo, calendario, nota docente, rúbrica
\documentclass{academic-beamer}      % diapositivas (carga el tema `academic` de themes/)
```

Las plantillas vacías de cada tipo están en `templates/`; los scripts `new-evaluacion.sh`,
`new-report.sh` y `new-presentation.sh` las copian ya con la clase puesta.

## Estructura

| Archivo | Qué es |
|---|---|
| `academic-base.cls` | el núcleo (sobre `article`): geometría, idioma, carga de `styles/academic.sty`. Las otras tres heredan de aquí |
| `academic-exam.cls` | evaluaciones: tres modos de salida (examen · claves · soluciones), bloques de enunciado y solución, membrete institucional |
| `academic-report.cls` | documentos de gestión docente: sílabo, calendario, nota docente, rúbrica |
| `academic-beamer.cls` | diapositivas: `beamer` + `\usetheme{academic}` (el tema vive en `themes/`) |

## Límite honesto

- **Una clase no fija colores ni fuentes**: eso es `styles/` (y el color, `config/palette.tex`,
  generado desde `sistema-editorial`). Si una clase necesita un color nuevo, se añade a la paleta, no
  a la clase.
- **No hay clase para tesis, monografía, ensayo ni artículo**: eso es `03 writing`.
- Los decks heredados con preámbulo propio no usan `academic-beamer` y por eso envejecen aparte.
