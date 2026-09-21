---
tipo: doc
titulo: "Cómo se mantiene este framework: ciclo de vida documental y propagación"
estado: activo
fecha: 2026-09-20
---
# Cómo se mantiene este framework

Responde a la pregunta que ningún otro documento respondía: **quién actualiza qué, cuándo y con qué
comprobación**. Nace en DOC4 (2026-09-20) porque el `CLAUDE.md` lo suplía de facto y por eso crecía.

## 1. Las cuatro fuentes de verdad

Cada cosa se escribe **una sola vez**, en su dueño. Todo lo demás apunta o se genera.

| Qué | Fuente única | Quién la consume |
|---|---|---|
| El estándar de contenido (curso · sesión · dictado · nomenclatura) | `docs/estandar-docencia.md` | `README.md`, `CLAUDE.md`, `docencia/README.md`, `scripts/validate.sh`, `prompts/00 metodo/ARQUITECTURA_DOCUMENTAL.md` (tipo 22), `prompts/05 docencia/` |
| El estándar de evaluaciones | `docs/estandar-evaluaciones.md` | `scripts/new-evaluacion.sh`, `docencia/migracion/cerrar-expediente.sh`, el prompt maestro de resolución de exámenes |
| La arquitectura editorial (capas, clases, tema) | `docs/arquitectura.md` | `styles/`, `classes/`, `themes/`, `templates/` |
| El currículo de un curso | `docencia/cursos/<slug>/curso.yml` | README del curso, ficha web, temario del learning-skill, checklist de `05 tasks` |

Fuera del repo hay una quinta: **el color**, que vive en `sistema-editorial/temas/docencia.yml` y
llega aquí como `config/palette.tex` generado.

## 2. Qué se genera y con qué

| Derivado | Desde | Herramienta |
|---|---|---|
| `docencia/cursos/<slug>/README.md` (×52) | `curso.yml` | `./scripts/temario-generar.sh generar --que readme --aplicar` |
| Sección «Contenidos / Sílabo» de `04 index/cursos/<materia>/index.qmd` | `curso.yml` | `temario-generar.sh generar --que web --aplicar` (entre marcadores) |
| `prompts/skills/learning/2 domains/_temarios/<dominio>.md` | `curso.yml` | `temario-generar.sh generar --que skill --aplicar` |
| `05 tasks/temarios-cursos.md` | todos los `curso.yml` | `temario-generar.sh generar --que resumen --aplicar` |
| `curso.yml.banco_examenes`, recursos de tipo post y simulador | disco y `04 index/_pubs` | `python3 scripts/enlazar.py examenes\|posts\|simuladores --aplicar` |
| `config/palette.tex` | `sistema-editorial/temas/docencia.yml` | `python3 generador.py generar --aplicar --espejo` (en `sistema-editorial`) |
| `docs/README.md` | frontmatter de `docs/*.md` | `python3 core/docs.py indice "10 Class" --aplicar` |
| `04 index/cursos/<materia>/<edicion>/` | `dictado.yml` | `./scripts/publish-session.sh` + `./scripts/publish-web.sh --aplicar` (hardlinks) |

Un derivado **no se edita a mano**: lleva su marca `GENERADO por … ; no editar` o vive entre
marcadores. Lo escrito fuera de los marcadores se conserva al regenerar.

## 3. Cuándo cambia el estándar de docencia

Orden obligatorio, de la regla al código y del código a las vistas:

1. **Escribir la regla** en `docs/estandar-docencia.md` (o `estandar-evaluaciones.md`), con su fecha.
2. **Hacerla exigible**: `scripts/validate.sh` la comprueba; si no puede, la regla es una convención y
   se dice así en el documento.
3. **Hacerla vigilable**: `scripts/doctor.sh` la incorpora si es un estado que se degrada con el tiempo.
4. **Actualizar los scaffolds y las plantillas** (`scaffolds/`, `templates/`) y los scripts `new-*`.
5. **Regenerar las vistas** (§2) y correr `./scripts/validate.sh --todos`.
6. **Actualizar los punteros**, nunca copias: `README.md`, `CLAUDE.md`, `docencia/README.md`,
   `prompts/05 docencia/`, `prompts/ECOSISTEMA_APRENDIZAJE.md` y `meta/workspace.yml` (`verdad:`).
7. **Anotar el cambio** en `CHANGELOG.md`; si fue una decisión con alternativas descartadas, también en
   la bitácora de la fase (`meta/reparaciones/<fase>/`).

Si el cambio afecta a los apuntes de estudio, pasa además por la checklist de propagación de
`prompts/ECOSISTEMA_APRENDIZAJE.md`.

## 4. Cuándo cambia la plataforma editorial

El diseño se toca en `styles/` (identidad) o `classes/` (clase delgada), nunca en un documento ni en
una plantilla. Después: compilar **un deck, una evaluación y un sílabo** y mirarlos; si el cambio
afecta al color, hacerlo en `sistema-editorial` y espejarlo, no editar `config/palette.tex`.
Un parámetro nuevo del docente va a `config/course.yml` (YAML plano), nunca al código de `scripts/lib/`.

## 5. Ciclo de vida de un documento de este repo

| Cuándo | Qué se hace |
|---|---|
| un diagnóstico o plan aplica su última fase | `estado: hecho` y se mueve a `docs/historial/` en el mismo commit |
| un documento es absorbido por otro | línea 1 del cuerpo `> Superado por <ruta> (<fecha>).`, `estado: archivado`; se elimina en la siguiente higiene |
| una regla se retira | se tacha en su documento con la fecha; no se borra el porqué |
| se escribe un pendiente | con fecha y dueño (`meta/NORMATIVA_ARCHIVOS.md` §9.4) |
| se cita una ruta entre backticks | tiene que existir; las rutas históricas solo en `docs/historial/` |

`CLAUDE.md` no lleva historial (≤ 150 líneas, ≤ 5 fechas ISO): lo que envejece se muda a
`docs/historial/` y el `CLAUDE.md` lo enlaza.

## 6. Comprobación periódica

```bash
./scripts/validate.sh --todos                  # el estándar, curso a curso y dictado a dictado
./scripts/temario-generar.sh verificar         # ningún README de curso desfasado
python3 scripts/enlazar.py verificar           # enlaces del currículo
python3 core/docs.py verificar "10 Class"      # el índice de docs/ al día
python3 core/archivos.py validar "10 Class"    # normativa de archivos (D01–D12 incluidas)
./scripts/doctor.sh                            # todo lo anterior + entorno + binarios + _inbox
```

El doctor devuelve 1 con avisos (no es un fallo) y 2 con fallos.

## 7. Límite honesto

- Este documento describe el mantenimiento **documental y del estándar**; el mantenimiento pedagógico
  (qué se enseña y cómo) es el `guion.md` de cada sesión y el ciclo de `prompts/00 metodo/CICLO.md`.
- No fija una cadencia de revisión: la revisión la dispara un cambio, no el calendario. La única fecha
  comprometida hoy es el plazo **2026-10-31** de `docencia/_inbox/` y `registro/_legado/` (D10).
- No cubre el laboratorio `simuladores/`, que tiene su propia doctrina en `simuladores/CLAUDE.md`.
