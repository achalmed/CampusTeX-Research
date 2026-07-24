# 00 · Arquitectura del Academic_Class_Framework

> **Estado:** blueprint del rediseño integral (2026-07-23). Define la
> arquitectura objetivo; la implementación es por fases (§10). Este documento es
> la fuente de verdad arquitectónica: toda decisión estructural se justifica aquí.

El `Academic_Class_Framework` es la **plataforma editorial universitaria** con la
que Edison Achalma produce **todo** su material docente. No es un conjunto de
plantillas: es un sistema editorial con separación estricta de responsabilidades,
identidad visual única y un solo motor tipográfico, pensado para mantenerse 10+
años sin romper compatibilidad.

Complementa —sin solaparse— al [`Academic_Writing_Framework`](../../Academic_Writing_Framework/README.md),
que ya es dueño de **tesis, monografías, ensayos y artículos**. Este framework es
dueño de la **docencia**: presentaciones, evaluaciones, sílabos, calendarios,
manuales, guías, notas de clase, laboratorios, rúbricas, bancos y pósters.

---

## 1. Diagnóstico de la arquitectura actual

La estructura actual creció por acreción y mezcla responsabilidades:

| Problema | Dónde | Consecuencia |
|---|---|---|
| **Diseño dentro de plantillas** | cada `plantilla-NN.tex` fija metadatos y a veces estilo | un cambio visual obliga a tocar N archivos |
| **Duplicidad de plantillas** | `_PLANTILLAS/Plantilla_Examen/` vs `evaluaciones/plantillas/` | dos orígenes de verdad para "un examen" |
| **Dos motores** | Beamer usa el compilador universal (pdf/xe/lua); `evaluacion.cls` usa **pdfLaTeX** | dos toolchains, dos identidades tipográficas |
| **Identidad fragmentada** | diapositivas (Beamer Madrid) y exámenes (evaluacion.cls) no comparten fuentes, paleta ni cajas | el material no "se siente" un solo sistema |
| **Responsabilidades mezcladas** | `_PLANTILLAS/` contiene a la vez esqueletos de carpetas (00–09) y plantillas de documento | el mismo directorio hace dos trabajos distintos |
| **`config/course.yml` sobrecargado** | identidad del docente + parámetros de compilación | mezcla datos con configuración de motor |
| **Sin capa de estilos compartida** | no existe un punto único de identidad visual | imposible "cambiar un color y que afecte a todo" |

Ninguno es fatal hoy, pero todos escalan mal. El rediseño los elimina de raíz.

---

## 2. Principios de diseño (no negociables)

1. **Separación absoluta de capas.** Infraestructura, estilos, clases, plantillas,
   contenido, recursos y proyectos son capas distintas. Cada capa solo mira hacia
   abajo (usa las inferiores; nunca al revés).
2. **Responsabilidad única.** Cada archivo y cada directorio hace **una** cosa.
3. **Cero duplicidad.** Si algo existe en un lugar, no existe en otro. Un único
   origen de verdad por plantilla, por clase, por recurso.
4. **Un solo punto de cambio visual.** Cambiar un color, una fuente o un espaciado
   se hace en **un** archivo y afecta a diapositivas, exámenes, manuales y pósters
   a la vez.
5. **LuaLaTeX exclusivo** (migración 2026). Nada de pdfLaTeX ni XeLaTeX.
   `fontspec`, Unicode, OpenType/TrueType, `unicode-math`, microtipografía
   moderna (protrusion + **expansion** — esta última *efectiva solo bajo
   LuaLaTeX*; XeLaTeX la ignoraba), versalitas reales, números elzevirianos.
6. **El documento depende del framework, nunca al revés.** Una plantilla solo
   `\documentclass{academic-…}` y rellena contenido. Ningún estilo vive en los
   documentos.
7. **Escalabilidad sin rupturas.** Modular, sin dependencias circulares,
   compatibilidad hacia atrás sagrada.

---

## 3. El modelo en capas

```
┌──────────────────────────────────────────────────────────────────────┐
│  CONTENIDO / PROYECTOS   (fuera del framework: los 23 Academic_Class)  │  ← solo selecciona y rellena
│  course_NN/03_SESIONES/…/clase.tex   ·   course_NN/04_EVALUACIONES/…   │
└───────────────────────────────▲──────────────────────────────────────┘
                                │ \documentclass{academic-beamer|exam|report|poster}
┌───────────────────────────────┴──────────────────────────────────────┐
│  PLANTILLAS   templates/      documentos vacíos, sin diseño            │
└───────────────────────────────▲──────────────────────────────────────┘
                                │ hereda / usa
┌───────────────────────────────┴──────────────────────────────────────┐
│  CLASES   classes/*.cls   ·   TEMA BEAMER   themes/beamertheme…        │  ← encapsulan el diseño
└───────────────────────────────▲──────────────────────────────────────┘
                                │ cargan la MISMA identidad
┌───────────────────────────────┴──────────────────────────────────────┐
│  IDENTIDAD VISUAL ÚNICA   styles/*.sty   (colores, fuentes, cajas,     │  ← «Academic Theme»
│  tablas, código, figuras, iconos, matemática)                         │     un solo origen
└───────────────────────────────▲──────────────────────────────────────┘
                                │ leen valores de
┌───────────────────────────────┴──────────────────────────────────────┐
│  INFRAESTRUCTURA   config/ (paleta, fuentes, espaciados)  ·  assets/   │  ← el punto de cambio
│  bibliography/  ·  libraries/  ·  scripts/                             │
└──────────────────────────────────────────────────────────────────────┘
```

**La clave del rediseño:** la identidad visual **no** vive en las clases ni en el
tema Beamer, sino en `styles/` (paquetes `.sty` **agnósticos al motor**) que
`academic-base.cls` (documentos) **y** `beamerthemeAcademic.sty` (diapositivas)
cargan por igual. Así diapositivas y exámenes comparten literalmente los mismos
colores, fuentes y cajas: un único «Academic Theme» para todo.

---

## 4. Árbol completo del framework

```
Academic_Class_Framework/
│
├── classes/                     ← CLASES LaTeX (encapsulan el diseño; LuaLaTeX)
│   ├── academic-base.cls        · núcleo sobre `article`: carga styles/ + config/, comandos comunes
│   ├── academic-exam.cls        · exámenes, prácticas, bancos, solucionarios  (hereda base)
│   ├── academic-report.cls      · sílabos, calendarios, manuales, guías, notas de docente, labs, rúbricas (hereda base)
│   ├── academic-poster.cls      · pósters científicos  (base de póster + identidad)
│   └── academic-beamer.cls      · diapositivas  (base beamer + tema Academic)
│
├── styles/                      ← IDENTIDAD VISUAL ÚNICA (paquetes .sty, agnósticos al motor)
│   ├── academic.sty             · meta-paquete: carga todo lo de abajo (ÚNICO punto de entrada)
│   ├── academic-colors.sty      · paleta monocroma + 1 acento (lee config/palette.tex)
│   ├── academic-fonts.sty       · fontspec: Libertinus Serif/Sans/Math + Inconsolata (lee config/fonts.tex)
│   ├── academic-math.sty        · unicode-math
│   ├── academic-boxes.sty       · cajas tcolorbox (instrucciones, definición, teorema, nota, ejemplo…)
│   ├── academic-tables.sty      · tablas booktabs + notas al pie de tabla
│   ├── academic-code.sty        · código R · Python · Stata (resaltado uniforme)
│   ├── academic-figures.sty     · figuras, captions, diagramas (tikz base)
│   └── academic-icons.sty       · iconografía (fontawesome5)
│
├── themes/                      ← TEMA BEAMER propio (consume styles/; sin temas comerciales)
│   ├── beamerthemeAcademic.sty      · orquesta los 4 sub-temas + carga styles/academic.sty
│   ├── beamercolorthemeAcademic.sty · mapea la paleta de styles/ a los colores de Beamer
│   ├── beamerfontthemeAcademic.sty  · usa las fuentes de styles/
│   ├── beamerinnerthemeAcademic.sty · listas, bloques, títulos de frame, figuras
│   └── beamerouterthemeAcademic.sty · cabecera/pie minimalistas, sin barras ni sombras
│
├── config/                      ← INFRAESTRUCTURA: 1 archivo = 1 responsabilidad (el punto de cambio)
│   ├── identity.yml             · datos del docente/institución (defaults de metadatos)
│   ├── palette.tex              · valores de color  ← editar aquí cambia TODO
│   ├── fonts.tex                · elección de familias tipográficas
│   ├── spacing.tex · margins.tex · headers.tex · footers.tex · captions.tex · toc.tex
│
├── templates/                   ← PLANTILLAS: documentos vacíos, SIN diseño (solo \documentclass + contenido)
│   ├── presentation/            · \documentclass{academic-beamer}
│   │   ├── clase/  conferencia/  seminario/  ponencia/  workshop/
│   │   └── defensa-tesis/  institucional/  masterclass/
│   ├── exam/                    · \documentclass{academic-exam}
│   │   ├── examen-desarrollo/  examen-objetivo/  examen-problemas/
│   │   ├── practica-calificada/  practica-dirigida/  laboratorio/
│   │   ├── control-de-lectura/  examen-oral/  caso-estudio/  tarea/
│   │   └── banco-de-preguntas/  solucionario/
│   ├── report/                 · \documentclass{academic-report}
│   │   ├── silabo/  calendario/  manual/  guia/  nota-docente/  guia-lectura/  rubrica/
│   └── poster/                 · \documentclass{academic-poster}
│
├── scaffolds/                   ← ESQUELETOS DE CARPETAS (filesystem, NO compilables)
│   ├── course/                  · árbol 00–09 (estándar del Academic_Class)
│   ├── session/                 · anatomía 01_Antes…07_Notas
│   └── period/                  · 09_SEMESTRES/<periodo> (registro privado + publicación MOOC)
│
├── libraries/                   ← BANCOS reutilizables (contenido compartido entre cursos)
│   ├── Banco_Preguntas/  Banco_Ejercicios/  Banco_Diapositivas/
│   ├── Banco_Casos/  Banco_Datasets/  Banco_Imagenes/  Banco_Lecturas/
│
├── bibliography/                ← todos los .bib (uno por área o uno maestro)
│   └── academic.bib
│
├── assets/                      ← branding: logos, iconos, fuentes vendored
│   ├── logos/  branding/  fonts/
│
├── scripts/                     ← AUTOMATIZACIÓN (LuaLaTeX)
│   ├── lib/                     · common.sh · compile.sh · args.sh · clean.sh · env.sh · logging.sh
│   ├── new-course.sh  new-session.sh  new-period.sh        · scaffolds de carpetas
│   ├── new-presentation.sh  new-evaluacion.sh  new-report.sh  new-poster.sh · nuevos documentos desde templates/
│   ├── build.sh                · compila cualquier .tex con LuaLaTeX (reemplaza build-session/course/evaluacion)
│   ├── validate.sh  stats.sh  doctor.sh  clean.sh
│
├── examples/                    ← EJEMPLOS compilados (un .tex + .pdf por clase/tipo; los "tests")
│   ├── presentation-clase/  exam-desarrollo/  report-silabo/  poster/
│
├── docs/                        ← DOCUMENTACIÓN técnica (numerada)
│   ├── 00-arquitectura.md (este) · 01-flujo-compilacion.md · 02-identidad-visual.md
│   ├── 03-clases.md · 04-tema-beamer.md · 05-evaluaciones.md · 06-plantillas.md
│   ├── 07-tipografia.md · 08-crear-tipo-documento.md · 09-scaffolds-y-estandar.md
│
├── config/ (arriba)  ·  Makefile  ·  README.md  ·  CLAUDE.md  ·  .claude/
```

### Función de cada directorio (responsabilidad única)

| Directorio | Contiene **únicamente** | No contiene |
|---|---|---|
| `classes/` | clases `.cls` (lógica de diseño encapsulada) | valores de color/fuente (van en config), contenido |
| `styles/` | paquetes `.sty` de identidad, agnósticos al motor | clases, plantillas, contenido |
| `themes/` | el tema Beamer (5 archivos) | identidad propia — la toma de `styles/` |
| `config/` | valores tunables (paleta, fuentes, espaciados) + datos del docente | lógica |
| `templates/` | documentos vacíos que solo llaman a una clase | diseño, estilos |
| `scaffolds/` | esqueletos de carpetas del estándar 00–09 | documentos compilables |
| `libraries/` | bancos de contenido reutilizable | plantillas, clases |
| `bibliography/` | archivos `.bib` | otra cosa |
| `assets/` | logos, iconos, fuentes | código |
| `scripts/` | automatización (crear/compilar/validar) | contenido, estilos |
| `examples/` | un ejemplo compilado por tipo (documentación viva) | plantillas de trabajo |
| `docs/` | documentación técnica | código |

---

## 5. Cómo interactúan las capas

**Flujo de un documento (p. ej. una clase):**

1. El docente copia `templates/presentation/clase/` a
   `course_NN/03_SESIONES/SNN/02_Clase/` (o usa `scripts/new-presentation.sh`).
2. El maestro `.tex` hace `\documentclass{academic-beamer}` y rellena contenido.
   **No define ni un color.**
3. `academic-beamer.cls` carga `themes/beamerthemeAcademic.sty`.
4. `beamerthemeAcademic.sty` carga `styles/academic.sty` (la identidad) y mapea sus
   colores/fuentes al mundo Beamer.
5. `styles/academic-colors.sty` y `academic-fonts.sty` leen los valores de
   `config/palette.tex` y `config/fonts.tex`.
6. `scripts/build.sh` compila con **LuaLaTeX** (dos pasadas donde haga falta).

**El mismo `config/palette.tex`** alimenta a `academic-exam.cls` (vía
`academic.sty`) y a `academic-report.cls`. Por eso **cambiar `\definecolor{acento}`
en un archivo re-tinta diapositivas, exámenes, manuales y pósters a la vez.**

**Regla de dependencias (acíclica):**
`config/` ← `styles/` ← {`classes/`, `themes/`} ← `templates/` ← documento.
Ninguna flecha apunta hacia arriba. `scripts/`, `assets/`, `libraries/`,
`bibliography/` son transversales (los usa quien los necesite; no dependen de
nadie del árbol de estilo).

---

## 6. Decisiones arquitectónicas justificadas

**D1 · Identidad en `styles/`, no en las clases.**
*Por qué:* Beamer y `article` son clases base distintas; una no puede heredar de la
otra. Si la identidad viviera en `academic-base.cls`, las diapositivas no podrían
reutilizarla. Al ponerla en paquetes `.sty` agnósticos, **ambos mundos cargan la
misma identidad**. Es la única forma técnicamente correcta de lograr "un color
cambia todo" entre documentos y diapositivas.

**D2 · "Herencia" = compartir identidad, no `\LoadClass`.**
`academic-exam` y `academic-report` **sí** heredan de `academic-base` (vía
`\LoadClass`, porque los tres son `article`). `academic-beamer` y `academic-poster`
usan sus bases nativas (beamer / póster) y **comparten identidad** cargando
`styles/academic.sty`. El resultado para el usuario es idéntico: una sola fuente de
verdad visual.

**D3 · LuaLaTeX exclusivo.**
Elimina la fractura previa (Beamer multi-motor + exámenes pdfLaTeX). Con `fontspec`
+ `unicode-math` + Libertinus OpenType se obtienen versalitas reales, números
elzevirianos, ligaduras y `microtype` con protrusion **y expansion** (la expansion,
algoritmo hz, ahora *sí* se aplica; XeLaTeX la ignoraba) — imposible de forma
consistente en pdfLaTeX. Un solo motor = un solo toolchain, un solo `build.sh`.

**D4 · `evaluacion.cls` → `academic-exam.cls`.**
La clase de exámenes deja de ser una isla: se reescribe sobre `academic-base` +
`styles/`, heredando tipografía, paleta, cajas, código y tablas del sistema. Se
conserva **toda** su funcionalidad (entornos `pregunta`/`solucion`/`opciones`,
modos `claves`/`soluciones`/`compacto`, puntaje automático) — solo cambia de dónde
saca el diseño.

**D5 · `templates/` único; `scaffolds/` aparte.**
Se elimina la duplicidad `evaluaciones/plantillas/` vs `_PLANTILLAS/`: **todas** las
plantillas de documento viven en `templates/`. Los esqueletos de **carpetas** (el
árbol 00–09, la anatomía de sesión) son otra responsabilidad y viven en
`scaffolds/`. "Plantilla de documento" (algo que compilas) ≠ "esqueleto de
carpetas" (algo que copias para organizar).

**D6 · No duplicar `Academic_Writing_Framework`.**
Tesis, monografías, ensayos y artículos son documentos de **redacción larga** con
su framework maduro (LuaLaTeX+Biber, APA). Este framework **no** los reimplementa.
Sí añade lo que faltaba para docencia: sílabos, calendarios, notas de clase,
manuales, guías. (A futuro ambos frameworks pueden compartir una identidad común;
hoy cada uno es autónomo.)

**D7 · `config/` separa datos de lógica.**
Los valores tunables (colores, fuentes, espaciados) y los datos del docente salen
de las clases hacia `config/` (patrón `core/config/*.tex` del Writing Framework).
Un archivo por tema. La lógica queda en `styles/`; los valores, en `config/`.

**D8 · Tema Beamer propio, minimalista.**
Sin temas comerciales, sin degradados, sombras ni cajas decorativas. Inspiración
editorial (Harvard/Oxford/ETH/Tufte/Keynote): retícula, jerarquía tipográfica,
paleta monocroma + un acento, figuras grandes, aire. El tema se parte en los 5
archivos canónicos de Beamer (color/font/inner/outer + orquestador) para que cada
aspecto sea editable por separado.

---

## 7. Ventajas frente a la estructura actual

| Antes | Después |
|---|---|
| Cambiar un color → tocar N plantillas | Cambiar `config/palette.tex` → afecta a todo |
| Diapositivas y exámenes con estilos distintos | Una sola identidad «Academic» en todo |
| Dos motores (pdfLaTeX + multi-motor Beamer) | Un solo motor: LuaLaTeX |
| Plantillas duplicadas (`_PLANTILLAS` vs `evaluaciones`) | Un único `templates/` |
| Diseño mezclado en plantillas | Diseño solo en `classes/` + `styles/`; plantillas vacías |
| `_PLANTILLAS/` hace dos trabajos | `templates/` (documentos) y `scaffolds/` (carpetas) separados |
| Sin capa de identidad | `styles/` como origen único de verdad visual |
| Cobertura: clases + exámenes | Cobertura: presentaciones (8 tipos), exámenes (12), reports (7), pósters |

---

## 8. Roadmap de implementación por fases

Cada fase compila y se verifica antes de la siguiente (no hay test suite: se
compila y se mira el PDF; los `examples/` son los "tests").

- **Fase 0 — Andamiaje.** Crear el árbol vacío (`classes/ styles/ themes/ config/
  templates/ scaffolds/ libraries/ bibliography/ examples/`), mover `_BIBLIOTECA`→
  `libraries/`+`bibliography/`, `assets/branding`→`assets/`. Sin romper el tooling
  del estándar 00–09.
- **Fase 1 — Identidad (`styles/` + `config/`).** Escribir los paquetes de
  identidad en LuaLaTeX (colores, fuentes fontspec, cajas, tablas, código, math,
  iconos) + `config/palette.tex`/`fonts.tex`. Es el corazón; todo lo demás la
  consume.
- **Fase 2 — `academic-base.cls`** sobre `article`+LuaLaTeX cargando `styles/`.
- **Fase 3 — `academic-exam.cls`** (migración de `evaluacion.cls` (en su día a XeLaTeX; hoy LuaLaTeX) sobre
  base; preservar toda la funcionalidad) + `templates/exam/*` + ejemplos.
- **Fase 4 — Tema Beamer** (`themes/beamer*Academic.sty`) + `academic-beamer.cls`
  + `templates/presentation/*` (8 tipos) + ejemplos.
- **Fase 5 — `academic-report.cls`** + `templates/report/*` (sílabo, calendario,
  nota-docente, manual, guía, guía-lectura, rúbrica).
- **Fase 6 — `academic-poster.cls`** + `templates/poster/`.
- **Fase 7 — Scripts** (`build.sh` LuaLaTeX + `new-*` unificados), `docs/`,
  `Makefile`, y **actualización de los prompts** (§9). Retiro de `evaluaciones/` y
  `_PLANTILLAS/` una vez migrado todo.

Compatibilidad: mientras dure la migración, el tooling del estándar 00–09
(`new-course/session/period`, `validate`) sigue funcionando intacto.

---

## 9. Prompts que se actualizan con el rediseño

- `git-awesome-ai-prompts/learning-skill/prompt_resolucion_examenes_plantillas.md`
  → referenciar `academic-exam.cls` (no `evaluacion.cls`), las nuevas rutas
  (`Academic_Class_Framework/templates/exam/…`, `04_EVALUACIONES/`) y el flujo con
  `scripts/new-evaluacion.sh` + `build.sh`.
- `git-awesome-ai-prompts/archive/presentations/` (5 prompts: estructura, beamer,
  guion, tesis, monografía) → alinear los de **clase** con el nuevo
  `academic-beamer` y `templates/presentation/*`; los de tesis/monografía siguen
  apuntando al `Academic_Writing_Framework`.

Se actualizan en la Fase 7 (cuando las clases y plantillas nuevas ya existen), para
que los prompts describan la realidad, no la meta.
