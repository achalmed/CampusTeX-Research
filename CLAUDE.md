---
tipo: guia_ia
estado: activo
---
# CLAUDE.md — 10 Class (repo `Academic_Class_Framework`, remoto `CampusTeX-Research`)

Guía para el asistente. En español, como todo el ecosistema. `AGENTS.md` es un enlace a este archivo.
Léase antes: `README.md` (qué es y cómo se usa), `docs/README.md` (índice), `config/course.yml`,
`docs/estandar-docencia.md` (el estándar de contenido, fuente única) y `docs/estandar-evaluaciones.md`.

El framework define el estándar, aloja lo compartido y produce los PDF; el contenido vive en el
submódulo `docencia/` (repo `Academic_Class`) y lo privado en `registro/` (repo hermano, sin remoto).

## Reglas que no se negocian

- **Dónde va cada cosa nueva** (`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §15.11). En la raíz solo `README.md`,
  `CLAUDE.md`, `AGENTS.md`, `estado.md`, `LICENSE` y los archivos de entorno (`.gitignore`, `.gitattributes`, `.gitmodules`).

  | lo que apareció | va a | nunca a |
  |---|---|---|
  | cómo se usa un script o se crea un curso, una sesión, un documento | `README.md` §Uso o `scripts/README.md` | un `GUIA_*.md` |
  | una regla del contenido (curso, sesión, dictado, evaluación) | `docs/estandar-docencia.md` o `docs/estandar-evaluaciones.md` (sin renumerar §) | este archivo |
  | cómo está hecha la plataforma LaTeX | `docs/arquitectura.md` | un documento nuevo junto a él |
  | quién actualiza qué, qué se regenera | `docs/como-se-mantiene.md` | una nota suelta |
  | por qué se decidió algo | `docs/decisiones.md` | un `CHANGELOG.md` |
  | un pendiente (con fecha y dueño) | `estado.md` §Por hacer (el del contenido, `docencia/estado.md`) | un `TODO.md`, `docs/decisiones.md` |
  | una vista de `curso.yml` (README de curso, ficha web, temario, checklist) | se regenera con `scripts/temario-generar.sh` | se edita a mano |

  Lo que hiciste en esta sesión va al mensaje de commit, no a un archivo. Si nada encaja, pregunta
  antes de crear un documento.
- **El estándar se cuenta una sola vez**, en `docs/estandar-docencia.md` (evaluaciones:
  `docs/estandar-evaluaciones.md`). Este archivo, el `README.md` y `docencia/README.md` **apuntan**;
  nunca lo reescriben. Un cambio del estándar se hace allí y se propaga según `docs/como-se-mantiene.md`.
- **`curso.yml` es la única fuente del currículo**: README del curso, ficha web, temario del
  learning-skill y checklist de `05 tasks` son vistas generadas (`scripts/temario-generar.sh`).
  Edita el registro, no las vistas; el doctor avisa si un README se desfasó.
- **El documento depende del framework, nunca al revés.** El diseño vive una vez en `styles/` +
  `classes/`; un documento solo elige clase y rellena contenido. Ni plantillas ni documentos fijan estilo.
- **Motor LuaLaTeX exclusivo** (fontspec, Libertinus + Inconsolata, `unicode-math`, microtype con
  protrusion **y** expansion). No se introducen dependencias de pdfLaTeX ni XeLaTeX.
- **El color se cambia en `sistema-editorial/temas/docencia.yml`**, no aquí: `config/palette.tex` es un
  archivo GENERADO y espejado (órdenes en `sistema-editorial/docs/consumidores.md` §2 y §4).
  Las tipografías, en `styles/academic-fonts.sty`.
- **`registro/` nunca tiene remoto** (datos de estudiantes). Lo comprueba `scripts/doctor.sh`; su
  política está en `registro/CLAUDE.md`.
- **Lista cerrada de carpetas de curso** (`01-diseno · 02-contenido · 03-sesiones · 04-evaluaciones ·
  05-recursos`), que existen solo con contenido; **sin carpetas vacías y sin `.gitkeep`**: es error del
  validador. Fuera de norma solo `vendor/` (ajeno).
- **kebab-case ASCII** en carpetas y archivos, claves `snake_case`, períodos `AAAA-i`/`AAAA-ii`,
  español con tildes en todo (código, comentarios, mensajes y docs).
- **Homogeneidad total**: al estandarizar se convierte todo al estándar; si un deck deja de compilar,
  se reconstruye, no se conserva la excepción.
- **Lo externo no se copia**: libros por `calibre_id` en `curso.yml.bibliografia`, datasets por clave de
  `datafw`, logo y plantillas desde el framework. En `05-recursos` solo material propio y muestras
  ≤ 5 MB. Subir no es catalogar: antes de añadir, se busca en Calibre.
- **Flujo de submódulo**: commit dentro de `docencia/` → `git add docencia` + commit aquí (mueve el
  puntero). Clon nuevo: `git clone --recurse-submodules`.
- **Toda reorganización sigue el ciclo** (auditoría → propuesta → aprobación → tag → cambio con
  dry-run → validate → doctor → commit), deja su mapa de rutas en `contenido/migracion/`, el porqué en
  `docs/decisiones.md` y el asiento de la fase en `meta/docs/historial/progreso-2026.md`.

## Cómo se verifica un cambio

No hay suite de tests: se valida, se compila y se mira el PDF.

```bash
cd ~/Documents/10\ Class
./scripts/validate.sh CURSO|DICTADO|--todos     # invariantes del estándar (CURSO acepta slug o ruta)
./scripts/build-session.sh CURSO NN             # compila el artefacto declarado en sesion.yml
./scripts/build.sh ARCHIVO.tex [--modo examen|claves|soluciones|todos]
./scripts/temario-generar.sh verificar          # ningún README de curso desfasado de su curso.yml
python3 scripts/enlazar.py verificar            # enlaces a posts, simuladores y bancos
./scripts/doctor.sh                             # entorno + validate --todos + verificadores + normativa
bash -n scripts/<archivo>.sh                    # un archivo por invocación

cd ~/Documents
python3 core/archivos.py validar "10 Class"     # normativa de archivos (meta/docs/historial/NORMATIVA_ARCHIVOS.md)
python3 core/docs.py verificar "10 Class"       # el índice de docs/ al día
```

## Detalles que cuesta redescubrir

- **Orden de carga en `styles/`**: `mathtools` (amsmath) **antes** de `unicode-math`; si no,
  `\underbrace`/`\overbrace` salen como bloques negros.
- **Bajo `unicode-math` no existe amssymb**: `\blacksquare` es `\mdlgblksquare`. `\nota{}` como comando
  ya no existe: es `\interpreta{}`.
- **Bloques**: en texto van sin caja, líneas ni iconos (lavado `fondobloque`, rótulo en versalitas);
  en Beamer conservan caja, filete e icono. Es directriz visual, no descuido.
- **Salida en blanco y negro**: `\documentclass[bn]{academic-exam}` (o `salida=bn`) llama `\academicbn`,
  que pasa los once nombres `academic*` a gris por luminancia; también en `academic-beamer` (el tema
  resuelve los nombres al usarlos: basta redefinirlos tras `\usetheme`) y en `academic-report`.
- **El tema Beamer se llama `academic` en minúsculas** (`\usetheme{academic}`).
- **`config/course.yml` es YAML plano**: los scripts lo parsean con grep/sed. No anidar las claves
  marcadas `[script]`. Todo parámetro nuevo va a este archivo, nunca al código de `scripts/lib/`.
- **`compile_tex` envía los `academic-*` a `scripts/build.sh`**; el resto, al compilador universal
  del workspace (`compilador` de `config/course.yml`, con `-s`; contrato en
  `scripts-latex/docs/arquitectura.md` §Consumidores) y, si no existe, a `latex_engine()`
  dos veces. Los dos eligen el motor igual: el `%!TEX program` de las primeras líneas o lualatex.
  Si la compilación falla, el compilador sale con 1, muestra el error y deja el PDF anterior y los
  auxiliares en su sitio.
- **Los decks Beamer son autocontenidos** (preámbulo propio + copia local del logo): al mover una
  sesión hay que mover su carpeta completa, porque los assets son hermanos del `.tex`. El `deck.tex`
  de `new-session.sh --tipo clase` (`scaffolds/sesion/deck.tex`) usa `beamer` con `tema_beamer` de
  `config/course.yml`, no `academic-beamer`; el deck del framework lo crea `new-presentation.sh`.
- **Algunos decks heredados no compilan** y es pendiente del docente, no del framework: esperan un
  `cau-logo.png` **hermano del `.tex`** que no se copió (desde la ola 5 ninguno declara pdfLaTeX ni
  XeLaTeX). El logo canónico está en `assets/branding/cau-logo.png` (ver `assets/README.md`); se reconstruyen al usarlos.
- **`revisar: <motivo>` en `sesion.yml`** rebaja a aviso una incoherencia tipo/artefacto;
  `archivo: null` en `curso.yml` significa «la nota aún no existe» (sin esqueletos).
- **En zsh y con rutas con espacios** (`10 Class`): iterar con `while read`, nunca con `for x in $(…)`.
- **`*.sdr/`** son metadatos de KOReader: se ignoran.
- **`temario.py` toma rutas, no slugs** (`contenido/cursos/<slug>`), y sin `--que` escribe también en
  `04 index`, `prompts` y `05 tasks`: para un solo README, `--que readme docencia/cursos/<slug>`.
- **Antes de cerrar un expediente de evaluación**, el log no debe traer `Overfull \hbox` mayores de
  20 pt (los `\aplica{}` han de caber en una línea); lo cierra `contenido/migracion/cerrar-expediente.sh`.
- **`scripts/new-period.sh` está retirado**: los dictados viven en `contenido/dictados/<clave>/`.

## Dónde está cada cosa

| Necesitas | Ve a |
|---|---|
| El estándar de contenido (curso · sesión · dictado · nomenclatura) | `docs/estandar-docencia.md` |
| El estándar de evaluaciones (tipos, siglas, expediente, `code/`, ficha) | `docs/estandar-evaluaciones.md` |
| La arquitectura de la plataforma editorial (capas, decisiones) | `docs/arquitectura.md` |
| Quién actualiza qué cuando cambia el estándar | `docs/como-se-mantiene.md` |
| Por qué se decidió cada cosa | `docs/decisiones.md` |
| Dónde está el repo y lo pendiente | `estado.md` (el contenido: `docencia/estado.md`) |
| Diagnósticos y bitácoras cerradas | `docs/historial/README.md` |
| Quién consume lo que produce este repo | `docs/estandar-docencia.md` §9 |
| Qué hace cada script | `scripts/README.md` |
| El laboratorio computacional (motor, macro, estadística) | `simuladores/CLAUDE.md` |
| El contenido docente y sus carpetas | `docencia/README.md` |
| Datos de estudiantes: qué se puede y qué no | `registro/CLAUDE.md` |
| El ciclo de trabajo del ecosistema | `prompts/00 metodo/CICLO.md` |
| La taxonomía documental (docencia = tipo 22) | `prompts/00 metodo/ARQUITECTURA_DOCUMENTAL.md` |
| El contrato con los apuntes de estudio y la web | `prompts/docs/dominios/aprendizaje.md` |
| La normativa de archivos del ecosistema | `meta/docs/historial/NORMATIVA_ARCHIVOS.md` |

Si un documento, prompt o script habla de `areas/Academic_Class-<Área>/course_NN_<slug>/0N_…`, es
histórico: léelo como `contenido/cursos/<slug>/0N-…` (mapas en `contenido/migracion/historico/`).
