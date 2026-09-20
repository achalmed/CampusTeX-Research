---
tipo: readme
estado: activo
---
# styles/ — la identidad visual única del framework

Un examen y una diapositiva comparten diseño **al carácter** porque las clases de `classes/` y el tema
de `themes/` cargan exactamente estos paquetes. `academic.sty` es el único punto de entrada: carga el
resto en el orden correcto.

## Uso

```latex
\usepackage{academic}     % lo hace academic-base.cls; un documento no lo carga a mano
```

Para ver el efecto de un cambio: compilar **un deck, una evaluación y un sílabo** y mirarlos
(`./scripts/build.sh ARCHIVO.tex`).

## Estructura

| Archivo | Qué es |
|---|---|
| `academic.sty` | meta-paquete: el ÚNICO punto de entrada; fija el orden de carga |
| `academic-colors.sty` | la API de color estable: incluye `config/palette.tex` (generado) y deriva por `\colorlet` los siete roles; define `\academicbn` para la salida en gris |
| `academic-fonts.sty` | la tipografía única (LuaLaTeX + fontspec): Libertinus para texto y matemática, Inconsolata para código |
| `academic-math.sty` | matemática con `unicode-math` |
| `academic-boxes.sty` | los bloques informativos (`instrucciones`, `datos`, `solucion`, `nota`…) sobre tcolorbox |
| `academic-code.sty` | código fuente (R · Python · Stata) y salidas de consola |
| `academic-figures.sty` | figuras, captions y diagramas |
| `academic-tables.sty` | tablas editoriales (booktabs) e identidad de figuras |
| `academic-icons.sty` | iconografía única (fontawesome5) |

## Límite honesto

- **El orden importa**: `mathtools` (amsmath) se carga **antes** de `unicode-math`; al revés,
  `\underbrace` y `\overbrace` salen como bloques negros (hallazgo de R9, 2026-09-15).
- **Bajo `unicode-math` no existe amssymb**: `\blacksquare` es `\mdlgblksquare`. `\nota{}` como
  comando ya no existe: es `\interpreta{}`.
- **Los bloques son deliberadamente distintos según el medio**: en texto van sin caja, líneas ni
  iconos (lavado `fondobloque`, rótulo en versalitas); en Beamer conservan caja, filete e icono.
- **Aquí no se decide el color**: los valores están en `config/palette.tex`, generado desde
  `sistema-editorial/temas/docencia.yml`.
- **Solo LuaLaTeX.** `fontspec` y `unicode-math` no funcionan bajo pdfLaTeX y no se van a condicionar.
