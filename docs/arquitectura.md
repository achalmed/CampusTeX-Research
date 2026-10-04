---
tipo: doc
titulo: "Arquitectura de la plataforma editorial"
estado: activo
---
# Arquitectura de la plataforma editorial

Cómo está hecha la plataforma LaTeX con la que se produce todo el material docente: diapositivas,
evaluaciones, sílabos, calendarios, notas de docente y rúbricas. Explica las capas y cómo se recorre
un documento; **por qué** es así está en [`decisiones.md`](decisiones.md) §Plataforma editorial. El
estándar del contenido (curso, sesión, dictado) es otro documento:
[`estandar-docencia.md`](estandar-docencia.md).

Tesis, monografías, ensayos y artículos no son de esta plataforma: son de `03 writing`.

## 1. Principios

1. **Capas que solo miran hacia abajo.** Configuración, identidad, clases, plantillas y documento son
   capas distintas; cada una usa las inferiores y ninguna a las superiores.
2. **Un solo punto de cambio visual.** Un color o una fuente se cambian en un sitio y re-tintan
   diapositivas, evaluaciones y documentos de gestión a la vez.
3. **El documento depende del framework, nunca al revés.** Un documento declara
   `\documentclass{academic-*}` y rellena contenido; no define ni un color.
4. **LuaLaTeX exclusivo**: `fontspec`, `unicode-math`, `microtype` con protrusión y expansión.

## 2. Las capas

```
documento        docencia/cursos/<slug>/…/deck.tex · 04-evaluaciones/…/<tallo>.tex · 01-diseno/silabo.tex
    ▲  \documentclass{academic-beamer | academic-exam | academic-report}
plantillas       templates/{presentation,exam,report}/<tipo>/<tipo>.tex      (las copian los scripts new-*)
    ▲
clases · tema    classes/academic-*.cls  ·  themes/beamer*themeacademic.sty
    ▲  \RequirePackage{academic}
identidad        styles/academic.sty y sus paquetes academic-*.sty
    ▲  \InputIfFileExists{palette.tex}
configuración    config/palette.tex (GENERADO por sistema-editorial) · config/course.yml (datos del docente)
```

| capa | carpeta | contiene | no contiene |
|---|---|---|---|
| configuración | `config/` | la paleta generada y los datos del docente y del curso que leen los scripts | lógica |
| identidad | `styles/` | `academic.sty` (único punto de entrada) y los paquetes de color, fuentes, matemática, iconos, tablas, figuras, bloques y código | clases, contenido |
| clases | `classes/` | `academic-base` (sobre `article`), `academic-exam` y `academic-report` (heredan de la base), `academic-beamer` (sobre `beamer`) | valores de color o fuente |
| tema Beamer | `themes/` | el tema `academic`: orquestador y subtemas de color, fuente, interior y exterior | identidad propia |
| plantillas | `templates/` | documentos vacíos por tipo (presentaciones, evaluaciones, documentos de gestión) | diseño |
| transversales | `scripts/`, `scaffolds/`, `assets/`, `bibliography/` | automatización, registros mínimos, el logo canónico, el `.bib` heredado | dependencias del árbol de estilo |

Cada carpeta tiene su `README.md` con la lista de archivos; la lista no se repite aquí.

## 3. Cómo se recorre un documento

1. `scripts/new-presentation.sh`, `new-evaluacion.sh` o `new-report.sh` copia la plantilla del tipo al
   sitio del curso y la rellena con `config/course.yml`.
2. El documento declara su clase. `academic-exam` y `academic-report` cargan `academic-base`, que
   carga `styles/academic.sty`; `academic-beamer` carga `beamer` y el tema `academic`, que carga la
   misma `styles/academic.sty`. Por eso diapositivas y evaluaciones comparten la identidad al carácter.
3. `academic.sty` fija el orden de carga (`mathtools` antes de `unicode-math`); `academic-colors.sty`
   define unos valores por defecto y lee `config/palette.tex`.
4. `scripts/build.sh` pone `classes/`, `styles/`, `config/`, `themes/` y `assets/` en `TEXINPUTS` y
   compila con LuaLaTeX; el documento no necesita rutas.
5. La opción `bn` (o `salida=bn`) de las tres clases llama a `\academicbn`, que define el generado
   `config/palette.tex` y pasa los once nombres `academic*` a gris por luminancia.

## 4. Regla de dependencias

`config/` ← `styles/` ← {`classes/`, `themes/`} ← `templates/` ← documento. Ninguna flecha apunta hacia
arriba. El color no se decide en el repo: se cambia en `sistema-editorial/temas/docencia.yml` y se
regenera `config/palette.tex` (contrato en `sistema-editorial/docs/consumidores.md` §2). Las
tipografías se eligen en `styles/academic-fonts.sty`.

## 5. Límite honesto

- No hay suite de pruebas: un cambio de diseño se comprueba compilando un deck, una evaluación y un
  sílabo y mirándolos.
- Los decks Beamer heredados con preámbulo propio no pasan por estas capas y envejecen aparte.
- No hay clase de póster ni ejemplos compilados por tipo: el plan de julio de 2026 los preveía y no se
  construyeron (`decisiones.md`).
