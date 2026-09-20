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
  archivo GENERADO y espejado (`python3 generador.py generar --aplicar --espejo`; `verificar` avisa si
  diverge). Las tipografías, en `styles/academic-fonts.sty`.
- **`registro/` nunca tiene remoto** (datos de estudiantes). Lo comprueba `scripts/doctor.sh`; su
  política está en `registro/CLAUDE.md`.
- **Lista cerrada de carpetas de curso** (`01-diseno · 02-contenido · 03-sesiones · 04-evaluaciones ·
  05-recursos`), que existen solo con contenido; **sin carpetas vacías y sin `.gitkeep`**: es error del
  validador. Fuera de norma solo `vendor/` (ajeno) y `_inbox/` (legado).
- **kebab-case ASCII** en carpetas y archivos, claves `snake_case`, períodos `AAAA-i`/`AAAA-ii`,
  español con tildes en todo (código, comentarios, mensajes y docs).
- **Homogeneidad total**: al estandarizar se convierte todo al estándar; si un deck deja de compilar,
  se reconstruye, no se conserva la excepción.
- **Lo externo no se copia**: libros por `calibre_id` en `curso.yml.bibliografia`, datasets por clave de
  `02 analysis`, logo y plantillas desde el framework. En `05-recursos` solo material propio y muestras
  ≤ 5 MB. Subir no es catalogar: antes de añadir, se busca en Calibre.
- **Flujo de submódulo**: commit dentro de `docencia/` → `git add docencia` + commit aquí (mueve el
  puntero). Clon nuevo: `git clone --recurse-submodules`.
- **Toda reorganización sigue el ciclo** (auditoría → propuesta → aprobación → tag → cambio con
  dry-run → validate → doctor → commit) y deja su mapa en `docencia/migracion/` y su bitácora con
  `UNDO.sh` en `meta/reparaciones/`.

## Cómo se verifica un cambio

No hay suite de tests: se valida, se compila y se mira el PDF.

```bash
./scripts/validate.sh CURSO|DICTADO|--todos     # invariantes del estándar (CURSO acepta slug o ruta)
./scripts/build-session.sh CURSO NN             # compila el artefacto declarado en sesion.yml
./scripts/build.sh ARCHIVO.tex [--modo examen|claves|soluciones|todos]
./scripts/temario-generar.sh verificar          # ningún README de curso desfasado de su curso.yml
python3 scripts/enlazar.py verificar            # enlaces a posts, simuladores y bancos
./scripts/doctor.sh                             # entorno + validate --todos + verificadores + normativa
python3 core/archivos.py validar "10 Class"     # normativa de archivos (meta/NORMATIVA_ARCHIVOS.md)
bash -n scripts/<archivo>.sh                    # un archivo por invocación
```

## Detalles que cuesta redescubrir

- **Orden de carga en `styles/`**: `mathtools` (amsmath) **antes** de `unicode-math`; si no,
  `\underbrace`/`\overbrace` salen como bloques negros (R9, 2026-09-15).
- **Bajo `unicode-math` no existe amssymb**: `\blacksquare` es `\mdlgblksquare`. `\nota{}` como comando
  ya no existe: es `\interpreta{}`.
- **Bloques**: en texto van sin caja, líneas ni iconos (lavado `fondobloque`, rótulo en versalitas);
  en Beamer conservan caja, filete e icono. Es directriz visual, no descuido.
- **Salida en blanco y negro**: `\documentclass[bn]{academic-exam}` (o `salida=bn`) llama `\academicbn`,
  que pasa los once nombres `academic*` a gris por luminancia; también en `academic-beamer` (el tema
  resuelve los nombres al usarlos: basta redefinirlos tras `\usetheme`) y en `academic-report`.
- **El tema Beamer se llama `academic` en minúsculas** (`\usetheme{academic}`) desde M7 (2026-09-15).
- **`config/course.yml` es YAML plano**: los scripts lo parsean con grep/sed. No anidar las claves
  marcadas `[script]`. Todo parámetro nuevo va a este archivo, nunca al código de `scripts/lib/`.
- **`compile_tex` prefiere el compilador universal del workspace**
  (`scripts_for_latex/script_compilar_latex/main.sh`, autodetecta motor); si no existe, usa el motor de
  `latex_engine()` (comentario `%!TEX`, clase `yaac-*`, `fontspec`) dos veces. Ojo: **ese compilador
  borra el PDF cuando la compilación falla**; si es un PDF versionado, se recupera con `git checkout`.
- **Los decks Beamer son autocontenidos** (preámbulo propio + copia local del logo): al mover una
  sesión hay que mover su carpeta completa, porque los assets son hermanos del `.tex`.
- **5 decks heredados no compilan** y es pendiente del docente, no del framework: esperan un
  `cau-logo.png` **hermano del `.tex`** que no se copió, o declaran `%!TEX program = xelatex`. El logo
  canónico está en `assets/branding/cau-logo.png` (ver `assets/README.md`); se reconstruyen al usarlos.
- **`revisar: <motivo>` en `sesion.yml`** rebaja a aviso una incoherencia tipo/artefacto;
  `archivo: null` en `curso.yml` significa «la nota aún no existe» (sin esqueletos).
- **En zsh y con rutas con espacios** (`10 Class`): iterar con `while read`, nunca con `for x in $(…)`.
- **`*.sdr/`** son metadatos de KOReader: se ignoran.
- **Antes de cerrar un expediente de evaluación**, el log no debe traer `Overfull \hbox` mayores de
  20 pt (los `\aplica{}` han de caber en una línea); lo cierra `docencia/migracion/cerrar-expediente.sh`.
- **`scripts/new-period.sh` está retirado** (M5): los dictados viven en `docencia/dictados/<clave>/`.

## Dónde está cada cosa

| Necesitas | Ve a |
|---|---|
| El estándar de contenido (curso · sesión · dictado · nomenclatura) | `docs/estandar-docencia.md` |
| El estándar de evaluaciones (tipos, siglas, expediente, `code/`, ficha) | `docs/estandar-evaluaciones.md` |
| La arquitectura de la plataforma editorial (capas, decisiones) | `docs/arquitectura.md` |
| Quién actualiza qué cuando cambia el estándar | `docs/como-se-mantiene.md` |
| Por qué el repo es así (diagnósticos y bitácoras cerradas) | `docs/historial/README.md` |
| Qué cambió y cuándo | `CHANGELOG.md` |
| Qué hace cada script | `scripts/README.md` |
| El laboratorio computacional (motor, macro, estadística) | `simuladores/CLAUDE.md` |
| El contenido docente y sus carpetas | `docencia/README.md` |
| Datos de estudiantes: qué se puede y qué no | `registro/CLAUDE.md` |
| El ciclo de trabajo del ecosistema | `prompts/00 metodo/CICLO.md` |
| La taxonomía documental (docencia = tipo 22) | `prompts/00 metodo/ARQUITECTURA_DOCUMENTAL.md` |
| El contrato con los apuntes de estudio y la web | `prompts/ECOSISTEMA_APRENDIZAJE.md` |
| La normativa de archivos del ecosistema | `meta/NORMATIVA_ARCHIVOS.md` |

Si un documento, prompt o script habla de `areas/Academic_Class-<Área>/course_NN_<slug>/0N_…`, es
histórico: léelo como `docencia/cursos/<slug>/0N-…` (mapas en `docencia/migracion/historico/`).
