# Academic_Class · estándar de cursos + plataforma editorial

> Este repositorio hace **dos cosas** para la docencia de **Edison Achalma B.Sc. Econ.**
> (todo en **español**):
>
> 1. **Define el estándar** de carpetas, archivos y nomenclatura de **todas** las
>    `~/Documents/Academic_Class-*` (cualquier asignatura).
> 2. Es la **plataforma editorial LaTeX (LuaLaTeX)** con **identidad visual única**
>    que produce **todo el material docente**: diapositivas, exámenes, sílabos,
>    notas de docente, calendarios, rúbricas, pósters…
>
> **Motor:** LuaLaTeX exclusivo (migración 2026). **Fuente de verdad arquitectónica:**
> [`docs/00-arquitectura.md`](docs/00-arquitectura.md).

Principio rector: **el documento depende del framework, nunca al revés.** El diseño
vive una sola vez en `styles/` + `classes/`; cada documento solo *elige* su clase y
*rellena* contenido. Cambiar un color en `config/palette.tex` re-tinta exámenes,
diapositivas y sílabos a la vez.

---

## Estructura (arquitectura por capas)

```
Academic_Class_Framework/
├── styles/       Identidad visual única (academic.sty + colores, fuentes fontspec
│                 Libertinus+Inconsolata, math, iconos, cajas, código, tablas, idioma).
│                 La cargan por igual las clases de documento y el tema Beamer.
├── classes/      Clases delgadas que encapsulan el diseño:
│                 academic-base · academic-exam · academic-report · academic-beamer
├── themes/       Tema Beamer propio: beamer{,color,font,inner,outer}themeAcademic (minimalista)
├── config/       palette.tex (ÚNICO punto de cambio de color) · course.yml (datos del docente)
├── templates/    Documentos vacíos, sin diseño: presentation/ (8 tipos) · exam/ (12) · report/ (4)
├── scaffolds/    Esqueletos de CARPETAS (no compilables): course (00–11) · session · period
├── libraries/    Bancos reutilizables (Banco_*) · bibliography/ (.bib) · assets/ (branding)
├── examples/     Ejemplos compilados (documentación viva)
├── scripts/      Automatización (crear/compilar/validar)
└── docs/         Documentación técnica (00-arquitectura.md es la canónica)
```

---

## El estándar 00–11 (organización de los Academic_Class)

Un `Academic_Class-<Área>` es un **contenedor de cursos**. Cada `course_NN_<slug>/`
tiene **12 carpetas 00–11** + `README.md`:

```
00_ADMINISTRACION 01_PLANIFICACION 02_CONTENIDO 03_SESIONES 04_EVALUACIONES
05_ESTUDIANTES 06_RECURSOS 07_MULTIMEDIA 08_INVESTIGACION 09_PUBLICACION
10_ARCHIVO 11_SEMESTRES
```

Cada sesión (`03_SESIONES/SNN_<slug>/`) sigue la anatomía
`01_Antes 02_Clase 03_Actividad 04_Evaluacion 05_Despues 06_Recursos 07_Notas`.
`11_SEMESTRES/<AAAA-ciclo>/` guarda cada dictado (listas, notas, evidencias).
Detalle completo del estándar: [`docs/09-estandar-00-11.md`] (o la sección
correspondiente de `docs/`).

---

## Inicio rápido

```bash
cd ~/Documents/Academic_Class_Framework
AC=~/Documents/Academic_Class-<Área>

# 1) Carpetas (estándar 00–11)
./scripts/new-course.sh  "$AC" NN "Título del curso"
C="$AC/course_NN_<slug>"
./scripts/new-session.sh "$C" NN "Título de la sesión"
./scripts/new-period.sh  "$C" 2026-II

# 2) Documentos LaTeX (identidad única, LuaLaTeX)
./scripts/new-presentation.sh "$C" NN "Título" [--tipo clase|conferencia|seminario|…]
./scripts/new-evaluacion.sh   "$C" <tipo|01-12> "Título"     # → 04_EVALUACIONES/
./scripts/new-report.sh       "$C" <silabo|calendario|nota-docente|rubrica> "Título"

# 3) Compilar cualquier .tex (LuaLaTeX)
./scripts/build.sh <archivo>.tex [--modo examen|claves|soluciones|todos]
```

---

## Tooling

| Script | Función |
|---|---|
| `new-course.sh` · `new-session.sh` · `new-period.sh` | esqueletos de carpetas desde `scaffolds/` |
| `new-presentation.sh` | diapositivas → `SNN/02_Clase/` (`academic-beamer`, 8 tipos) |
| `new-evaluacion.sh` | examen/práctica → `04_EVALUACIONES/` (`academic-exam`, 12 tipos, modos claves/soluciones) |
| `new-report.sh` | sílabo/calendario/nota-docente/rúbrica → carpeta 00–11 (`academic-report`) |
| `build.sh` | compila cualquier `.tex` con LuaLaTeX (2 pasadas, TEXINPUTS de todas las capas) |
| `validate.sh` · `stats.sh` | valida la estructura 00–11 · resumen del curso |
| `doctor.sh` · `clean.sh` | chequeo de entorno · limpiar auxiliares |

---

## Convenciones

- **LuaLaTeX** exclusivo (fontspec, Libertinus + Inconsolata, `unicode-math`,
  microtype con **protrusion + expansion**).
- **Nombres de carpeta ASCII** (portabilidad + scripts); **`.gitkeep`** en carpetas vacías.
- **Un solo punto de cambio visual:** `config/palette.tex` y `config/fonts.tex`.
- **El diseño vive en `styles/`+`classes/`**, nunca en los documentos ni en las plantillas.
- Tesis, monografías, ensayos y artículos tienen su propio framework
  (`Academic_Writing_Framework`); este repo cubre la **docencia**.

## Documentación

| Doc | Contenido |
|---|---|
| [`docs/00-arquitectura.md`](docs/00-arquitectura.md) | **Blueprint canónico**: capas, decisiones, árbol, roadmap |
| `docs/` (resto) | flujo de compilación, identidad visual, clases, tema Beamer, evaluaciones, plantillas |
