# Academic_Class · estándar de docencia + plataforma editorial

> Este repositorio hace **dos cosas** para la docencia de **Edison Achalma B.Sc. Econ.**
> (todo en **español**):
>
> 1. **Define el estándar** de cursos, sesiones y dictados que sigue **todo** el contenido
>    docente, que vive en el único submódulo [`docencia/`](docencia/) (repo `Academic_Class`,
>    desde la reorganización del 2026-09-15) y cuya parte privada vive en `registro/`.
> 2. Es la **plataforma editorial LaTeX (LuaLaTeX)** con **identidad visual única**
>    que produce **todo el material docente**: diapositivas, exámenes, sílabos,
>    notas de docente, calendarios, rúbricas, pósters…
>
> **Motor:** LuaLaTeX exclusivo (migración 2026). **Fuente de verdad arquitectónica:**
> [`docs/00-arquitectura.md`](docs/00-arquitectura.md). **Estándar de contenido:**
> [`docs/09-estandar-docencia.md`](docs/09-estandar-docencia.md).

Principio rector: **el documento depende del framework, nunca al revés.** El diseño
vive una sola vez en `styles/` + `classes/`; cada documento solo *elige* su clase y
*rellena* contenido. Cambiar un color en `sistema-editorial/temas/docencia.yml` (de donde
se GENERA `config/palette.tex`, Fase 6, 2026-09-20) re-tinta exámenes,
diapositivas y sílabos a la vez.

---

## Estructura (arquitectura por capas)

```
10 Class/
├── styles/       Identidad visual única (academic.sty + colores, fuentes fontspec
│                 Libertinus+Inconsolata, math, iconos, cajas, código, tablas, idioma).
│                 La cargan por igual las clases de documento y el tema Beamer.
├── classes/      Clases delgadas que encapsulan el diseño:
│                 academic-base · academic-exam · academic-report · academic-beamer
├── themes/       Tema Beamer propio: beamer{,color,font,inner,outer}themeacademic (minimalista)
├── config/       palette.tex (GENERADO desde sistema-editorial/temas/docencia.yml) · course.yml (datos del docente)
├── templates/    Documentos vacíos, sin diseño: presentation/ (8 tipos) · exam/ (12) · report/ (4)
├── scaffolds/    Registros mínimos, no árboles: curso/ (curso.yml, README) · sesion/ (sesion.yml,
│                 guion.md, deck.tex|qmd) · dictado/ (dictado.yml)
├── bibliography/ .bib compartidos · assets/ (branding)
├── examples/     Ejemplos compilados (documentación viva)
├── scripts/      Automatización (crear/compilar/validar/publicar)
├── docs/         Documentación técnica (00-arquitectura.md y 09-estandar-docencia.md son las canónicas)
├── docencia/     SUBMÓDULO (repo Academic_Class): cursos/ · dictados/ · _inbox/ · migracion/
└── registro/     repo privado hermano (git-ignorado): estudiantes, calificaciones, evidencias
```

---

## El estándar de docencia (resumen; detalle en `docs/09-estandar-docencia.md`)

```
docencia/cursos/<slug>/                 ← 50 cursos; slug kebab-case sin número
├── curso.yml · README.md (generado)    ← lo único obligatorio
├── 01-diseno/ 02-contenido/ 03-sesiones/ 04-evaluaciones/ 05-recursos/   ← lista cerrada; existen solo con contenido
└── 03-sesiones/sNN-<slug>/{sesion.yml, guion.md, <artefacto del tipo>}   ← clase | laboratorio | taller | evaluacion

docencia/dictados/<AAAA-ciclo>-<institucion>-<materia>/   ← dictado.yml (sesiones de varios cursos) + publicacion/ (producto)
registro/<misma clave>/                                    ← lo privado, en repo aparte
```

- **`curso.yml` es la única fuente del currículo** (sucesor de `temario.yml`): README del
  curso, ficha web, temario del learning-skill y checklist de estudio se generan con
  `temario-generar.sh`. Edita el registro, no las vistas.
- **La sesión se tipa por archivo**: `tipo: clase` exige `deck.tex|qmd`; `laboratorio`,
  un cuaderno o script; `taller`, un libro de cálculo; `evaluacion`, `evaluacion.tex`.
  `guion.md` siempre. Sin subcarpetas fijas.
- **Congelar = etiquetar** (`tag dictado/<clave>/<sesion>`); el producto de
  `publish-session.sh` es git-ignorado y la web lo recibe por hardlink (`publish-web.sh`).
- Lo externo no se copia: libros por `calibre_id`, datasets por clave de `02 analysis`,
  logo y plantillas desde el framework; muestras ≤ 5 MB dentro del curso.

---

## Inicio rápido

```bash
cd ~/Documents/10 Class          # CURSO y DICTADO aceptan slug o ruta

# 1) Registros (sin árboles de carpetas)
./scripts/new-course.sh  econometria-i "Econometría I" --tipo asignatura --area estadistica,econometria --materia-web econometria
./scripts/new-session.sh econometria-i 07 "Series temporales" --tipo clase        # sesion.yml + guion.md + deck.tex
./scripts/new-dictado.sh 2026-ii unsch econometria "Econometría I · 2026-II"     # dictado.yml + registro/<clave>/

# 2) Documentos LaTeX (identidad única, LuaLaTeX)
./scripts/new-presentation.sh econometria-i 07 "Series temporales"               # deck academic-beamer en la sesión
./scripts/new-evaluacion.sh   econometria-i examen-desarrollo "Parcial"          # → 04-evaluaciones/
./scripts/new-report.sh       econometria-i silabo "Sílabo 2026-II"              # → 01-diseno/

# 3) Compilar, validar, publicar
./scripts/build-session.sh econometria-i 07                                      # el artefacto declarado
./scripts/build.sh ARCHIVO.tex [--modo examen|claves|soluciones|todos]
./scripts/validate.sh --todos && ./scripts/doctor.sh
./scripts/publish-session.sh 2026-ii-unsch-econometria econometria-i 07          # tag + publicacion/
./scripts/publish-web.sh     2026-ii-unsch-econometria --aplicar                 # hardlinks a 04 index/cursos
```

---

## Tooling

| Script | Función |
|---|---|
| `new-course.sh` · `new-session.sh` · `new-dictado.sh` | crean solo el registro (y el artefacto del tipo) desde `scaffolds/` |
| `new-presentation.sh` | deck `academic-beamer` (8 tipos) en la sesión; declara `artefacto` en `sesion.yml` |
| `new-evaluacion.sh` | examen/práctica → `04-evaluaciones/` (`academic-exam`, 12 tipos, modos claves/soluciones) |
| `new-report.sh` | sílabo/calendario/nota-docente/rúbrica → `01-diseno/` (`academic-report`) |
| `build.sh` · `build-session.sh` · `build-course.sh` | LuaLaTeX (o Quarto) sobre un `.tex`, el artefacto de una sesión o todo un curso |
| `temario-generar.sh` · `enlazar.py` | vistas desde `curso.yml` (`verificar` lo corre el doctor) · enlaces a posts, simuladores y bancos |
| `publish-session.sh` · `publish-web.sh` | congela una sesión (tag + `publicacion/`) · enlaza el producto por hardlink en la web |
| `validate.sh` · `stats.sh` | invariantes del estándar (`CURSO`, `DICTADO` o `--todos`) · resumen por sesión |
| `doctor.sh` · `clean.sh` | entorno + validate + verificadores + `_inbox` + binarios + normativa (`core/archivos.py`) · auxiliares |
| `normalizar-archivos.py` · `normalizar-notas.py` | normativa de archivos (registros, nombres, cabeceras, notas); simulan sin `--aplicar` |

---

## Convenciones

- **LuaLaTeX** exclusivo (fontspec, Libertinus + Inconsolata, `unicode-math`,
  microtype con **protrusion + expansion**).
- **kebab-case ASCII** en carpetas y archivos; **sin carpetas vacías** (una carpeta vacía es
  error del validador); excepciones solo `vendor/` y `_inbox/`.
- **Un solo punto de cambio visual:** `config/palette.tex` (color; GENERADO desde `sistema-editorial/temas/docencia.yml`) y
  `styles/academic-fonts.sty` (tipografías).
- **El diseño vive en `styles/`+`classes/`**, nunca en los documentos ni en las plantillas.
- **Reversibilidad por git**: `docencia/` es un repo con un solo historial; cada
  reorganización deja su mapa en `docencia/migracion/` y su bitácora en `meta/reparaciones/`.
- Tesis, monografías, ensayos y artículos tienen su propio framework
  (`Academic_Writing_Framework`); este repo cubre la **docencia**.

## Documentación

| Doc | Contenido |
|---|---|
| [`docs/00-arquitectura.md`](docs/00-arquitectura.md) | **Blueprint canónico** de la plataforma editorial: capas, decisiones, árbol |
| [`docs/09-estandar-docencia.md`](docs/09-estandar-docencia.md) | **El estándar de contenido**: curso, sesión, dictado, registro, nomenclatura, reglas |
| [`docs/DIAGNOSTICO_AREAS_2026-09.md`](docs/DIAGNOSTICO_AREAS_2026-09.md) | por qué se dejó el 00–09: diagnóstico, diseño y ejecución M0–M8 |

---

## Ecosistema de aprendizaje

Este framework es la pieza de **docencia y estándar** del ecosistema: define la forma de
`docencia/cursos/<slug>/` a la que enlazan los apuntes de estudio (`learning-skill`, en
`01 notes/40-cursos-y-formacion/`) y que consumen la web (`04 index/cursos/`), la
biblioteca (Calibre, por `calibre_id`) y la capa de datos (`02 analysis`, por clave). Las
funciones hermanas y el contrato completo (casos de uso, claves compartidas, enlaces
recíprocos, checklist de propagación) viven en `~/Documents/prompts/ECOSISTEMA_APRENDIZAJE.md`.
