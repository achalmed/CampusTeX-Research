---
tipo: readme
estado: activo
---
# themes/ — el tema Beamer propio `academic`

Tema minimalista que consume `styles/`, para que una diapositiva y un examen compartan paleta,
tipografía y bloques. Lo carga `classes/academic-beamer.cls`.

## Uso

```latex
\usetheme{academic}      % lo hace academic-beamer.cls; un deck nuevo no lo escribe a mano
```

```bash
./scripts/new-presentation.sh CURSO NN "Título" --tipo clase
./scripts/build-session.sh CURSO NN
```

## Estructura

| Archivo | Qué es |
|---|---|
| `beamerthemeacademic.sty` | el tema: carga los cuatro subtemas y `styles/academic.sty` |
| `beamercolorthemeacademic.sty` | colores, derivados de la paleta |
| `beamerfontthemeacademic.sty` | tipografía |
| `beamerinnerthemeacademic.sty` | elementos interiores (listas, bloques, títulos de cuadro) |
| `beamerouterthemeacademic.sty` | elementos exteriores (cabecera, pie, barra de navegación) |

## Límite honesto

- **El nombre es `academic`, en minúsculas**, desde M7 (2026-09-15); `\usetheme{Academic}` ya no
  existe y los decks heredados que lo escriban así no compilan.
- **Los colores se resuelven al usarlos**: por eso basta redefinir los once nombres `academic*`
  después de `\usetheme` para obtener la salida en blanco y negro (`\academicbn`).
- **Los decks Beamer heredados son autocontenidos** (preámbulo propio y copia local del logo) y no
  pasan por este tema: se reconstruyen al usarlos, no se parchean.
