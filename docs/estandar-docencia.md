---
tipo: doc
titulo: "El estándar de docencia: cursos, sesiones y dictados en docencia/"
estado: activo
fecha: 2026-09-15
---
# El estándar de docencia: cursos, sesiones y dictados en `docencia/`

> Contrato de carpetas, archivos y registros del contenido docente. Es la forma que el
> diagnóstico `historial/DIAGNOSTICO_AREAS_2026-09.md` (§4 y §7) propuso y que las fases M0–M7 del
> 2026-09-15 dejaron en disco; sustituye al estándar 00–09 (2026-07 → 2026-09-15). El
> resumen vive en el `README.md`; la arquitectura editorial (capas LaTeX, `styles/`,
> clases, tema Beamer) en [`arquitectura.md`](arquitectura.md). Lo que aquí se
> declara lo exige `scripts/validate.sh` y lo vigila `scripts/doctor.sh`.

## 1. Dónde vive cada cosa

```
10 Class/                       ← repo Academic_Class_Framework: tooling, clases, plantillas, scaffolds
├── docencia/                   ← UN submódulo: repo Academic_Class (todo el contenido docente)
│   ├── cursos/<slug>/          ← qué se enseña (52 cursos)
│   ├── dictados/<AAAA-ciclo>-<institucion>-<materia>/   ← cada vez que se dicta (manifiesto + producto)
│   ├── migracion/              ← ledger vivo del banco de exámenes; historico/ = mapas y migradores de M3–M6 (son el UNDO)
│   └── README.md               ← puerta del repo de contenido (a mano; no hay generador)
└── registro/                   ← repo PRIVADO hermano, git-ignorado aquí; nunca con remote público
    └── <clave-del-dictado>/    ← estudiantes, asistencia, calificaciones, evidencias
```

Tres repos, tres responsabilidades: el framework produce y valida; `docencia/` es la
fuente del contenido y se versiona con un solo historial (los 23 repos de área se
fusionaron en él en M2, con `git filter-repo`, y quedan como tags
`<area>/pre-reorg-2026-09`); `registro/` guarda lo que tiene nombres de personas.

## 2. El curso: `cursos/<slug>/`

```
cursos/econometria-i/
├── curso.yml            ← registro del curso (sucesor de temario.yml): LA fuente del currículo
├── README.md            ← vista generada (temario-generar.sh); no se edita
├── 01-diseno/           ← sílabo, calendario, competencias, matriz de evaluación, rubricas/ (academic-report)
├── 02-contenido/        ← apuntes canónicos: 1-2-tema.md (solo los escritos), img/
├── 03-sesiones/         ← s01-<slug>/ … (§3)
├── 04-evaluaciones/     ← <sub>/AAAAMMDD_sig/ (.tex academic-exam + PDF + code/): estándar docs/estandar-evaluaciones.md
└── 05-recursos/         ← datasets/ (≤ 5 MB), talleres/, plantillas/, investigacion/, vendor/, curso.bib
```

- `curso.yml` y `README.md` son lo único obligatorio. Las cinco carpetas son una **lista
  cerrada** y **existen solo cuando tienen contenido**: una carpeta desconocida o vacía es
  error del validador; no hay `.gitkeep`.
- El slug es kebab-case sin número: el orden en la malla es un metadato (`malla.orden`),
  no parte de la ruta, y no cambia cuando cambia el plan de estudios.
- Correspondencia con el 00–09 (para leer material heredado): `00`+`01` → `01-diseno`;
  `02` → `02-contenido`; `03` → `03-sesiones`; `04` → `04-evaluaciones`; `05` →
  `registro/` (privado) o `04-evaluaciones/ejemplos/` (modelos anonimizados); `06`, `07`,
  `08` → `05-recursos/` (o junto al deck que los usa); `09` → `dictados/`. El mapa
  archivo a archivo está en `docencia/migracion/mapa-m3.csv`.

`curso.yml` (claves `snake_case`, normativa §7; `scaffolds/curso/curso.yml` es la plantilla):

```yaml
# cursos/econometria-i/curso.yml — registro del curso econometria-i
id: econometria-i                 # = nombre de la carpeta
alias: [course_03_econometria_i]  # ids anteriores; los resuelven enlazar.py y las fichas de Calibre
titulo: "Econometría I"
estado: borrador                  # borrador | activo | archivado
tipo: asignatura                  # asignatura | herramienta | nivelacion | taller
area: [estadistica, econometria]  # etiquetas, no carpetas; un curso puede tener varias
malla: {plan: economia-unsch, ciclo: 5, orden: 13}
materia_web: econometria          # ficha de 04 index/cursos/<materia>; varios cursos → una materia
prerrequisitos: [estadistica-para-economistas]
etiqueta: econometria
dominio_fuat: econometria         # dominio del learning-skill
unidades: [...]                   # id, titulo, temas[] {id, titulo, archivo: 02-contenido/1-1-tema.md | null, recursos[]}
bibliografia: [{calibre_id: 1234, titulo: …, autor: …, origen: …}]
banco_examenes: []                # enlazar.py examenes
datasets: [{clave: inei/enaho/2019/sumaria, uso: "s01 pobreza"}]   # catálogo de 02 analysis
ajeno: [{ruta: 05-recursos/vendor/plantilla-sbs, descripcion: …}]
```

`validate.sh` exige `id` (= carpeta), `titulo`, `estado` y `tipo`. `temario-generar.sh`
genera de aquí el README del curso, la sección «Contenidos / Sílabo» de la ficha web, el
temario del learning-skill y la checklist de `05 tasks/temarios-cursos.md`; el doctor
avisa si una vista se desfasó. `archivo:` de un tema es `null` hasta que la nota existe:
**no hay esqueletos**.

## 3. La sesión: tipada por archivo, no por subcarpeta

```
03-sesiones/s07-series-temporales/
├── sesion.yml           ← id · titulo · tipo · estado · artefacto · unidad · semana · duracion_min · modalidad
├── guion.md             ← plan de clase + notas del docente + retrospectiva (antes / durante / después)
├── deck.tex | deck.qmd  ← exigido si tipo: clase (assets hermanos: img/, logo local)
├── cuaderno.ipynb | script.do|.R|.py|.rmd | libro.ods|.xlsx   ← exigido si tipo: laboratorio | taller
├── evaluacion.tex       ← exigido si tipo: evaluacion (academic-exam)
├── practica.*           ← actividad (opcional)
└── datos/ img/ recursos/ ← opcionales
```

- `sNN-<slug>`: el número lo da la carpeta; `id` = carpeta. `tipo ∈ {clase, laboratorio,
  taller, evaluacion}`.
- El validador exige `sesion.yml` (`id/titulo/tipo/estado`), `guion.md` y el `artefacto`
  declarado, existente y con extensión coherente con el tipo (`clase` → `.tex`/`.qmd`;
  `laboratorio` → `.ipynb`/`.do`/`.py`/`.r`/`.rmd`/`.html`; `taller` → `.ods`/`.xlsx`/`.xlsm`;
  `evaluacion` → `.tex`). `revisar: <motivo>` en `sesion.yml` rebaja la incoherencia a
  aviso mientras se decide.
- No hay anatomía de subcarpetas: el arco antes/durante/después son secciones de
  `guion.md` (esquema `presentacion-clase` de `03 writing/esquemas/`, alineamiento
  constructivo). Lo que antes iba en `01_Antes … 07_Notas` se fusionó ahí en M4.
- Los decks Beamer siguen siendo autocontenidos (preámbulo propio + copia local del
  logo): al mover una sesión se mueve la carpeta completa.

## 4. El dictado y el registro

```
dictados/2026-i-cau-unsch-metodologia/
├── dictado.yml          ← id · periodo (AAAA-i | AAAA-ii) · institucion · titulo · estado · cursos[]
│                          · sesiones[] {orden, curso, sesion, web} · web {materia, edicion} · registro · legado
├── cronograma.md        ← opcional
└── publicacion/<web>/   ← PRODUCTO de publish-session.sh: git-ignorado; la web lo enlaza por hardlink
```

- Un dictado puede tomar sesiones de **varios cursos** (Metodología 2026-I cruza cuatro)
  y por eso vive fuera del curso, con clave `<AAAA-ciclo>-<institucion>-<materia>`.
- **Congelar = etiquetar**: `publish-session.sh` compila el artefacto, deposita el producto
  en `publicacion/<web>/` (con `_PUBLICADO.md`) y pone el tag
  `dictado/<clave>/<sesion>` sobre el commit de las fuentes. No se copia nada al repo.
- `publish-web.sh DICTADO --aplicar` enlaza el producto **por hardlink** (un solo inodo)
  en `04 index/cursos/<materia>/<edicion>/<web>/`. La web nunca es fuente; el doctor avisa
  de copias y huérfanos. `legado: true` marca dictados anteriores al estándar que no se
  republican (2025-I).
- `registro/<clave>/` (repo privado) guarda estudiantes, asistencia, calificaciones,
  evaluaciones aplicadas y evidencias. **Nada con nombres de estudiantes entra en
  `docencia/`**; el doctor comprueba que `registro/` no tenga remote público.

## 5. Nomenclatura única

- Carpetas y archivos en **kebab-case ASCII minúsculas**: `cursos/econometria-i/`,
  `s07-series-temporales/`, `1-2-medicion-del-pib.md`, `deck.tex`.
- Prefijo numérico solo en las cinco carpetas fijas (`01-…05-`) y en las sesiones (`sNN-`).
- Claves YAML `snake_case`; `id` = slug de la carpeta; `estado` del ciclo de vida
  (`meta/NORMATIVA_ARCHIVOS.md` §2.1); línea 1 de identidad en cada registro.
- Períodos `AAAA-i` / `AAAA-ii`.
- Fuera de norma solo `vendor/` (ajeno, declarado en `ajeno:`):
  el validador no entra en ellos. Los adjuntos heredados con espacios que lee código
  (`.do`, `.rmd`, `.ipynb`) se conservan; la normativa los admite (§4).

## 6. Relación con el ecosistema

| Necesidad | Dónde vive | Cómo la cita el curso |
|---|---|---|
| Libros y artículos | Calibre (`biblioteca/`) | `bibliografia[].calibre_id` (`scripts_for_fuentes/ingesta_cursos` lo escribe) |
| Datasets oficiales (ENAHO, INEI, Damodaran…) | catálogo de `02 analysis` (`data/raw/…`) | `datasets[].clave`; el curso conserva solo muestras ≤ 5 MB |
| Logo, fuentes, plantillas, clases | `assets/`, `styles/`, `templates/`, `classes/` del framework | `\documentclass{academic-*}`; el deck lleva **una** copia local del logo |
| Apuntes de Edison como alumno | `01 notes/40-cursos-y-formacion/<curso>/` | enlazan al tema de `02-contenido/`; nunca escriben en `docencia/` |
| Ficha web | `04 index/cursos/<materia>/` | `materia_web` (n cursos → 1 materia); ediciones por dictado |
| Temario del learning-skill | `prompts/skills/learning/2 domains/_temarios/` | generado desde `curso.yml`; `dominio_fuat` |
| Posts, simuladores, bancos de exámenes | `04 index/_pubs`, `04 index/simuladores`, `docencia/cursos/*/04-evaluaciones/banco` | `enlazar.py` (los ids antiguos se resuelven por `alias`) |

## 7. Reglas de mantenimiento

1. **Un curso = `cursos/<slug>/curso.yml`.** Se crea con `new-course.sh SLUG "Título"`; el
   script no crea carpetas, solo el registro y el README generado.
2. **Carpetas cerradas y no vacías.** Solo `01-diseno 02-contenido 03-sesiones
   04-evaluaciones 05-recursos`; existen cuando tienen contenido. Sin `.gitkeep`.
3. **Sesión = `sNN-<slug>/sesion.yml` con `tipo`.** El tipo fija el artefacto obligatorio;
   `guion.md` siempre; sin subcarpetas fijas; el número lo da la carpeta.
4. **Nombres**: kebab-case ASCII para carpetas y archivos; `snake_case` para claves;
   `id` = carpeta; `estado` del ciclo. Excepción solo `vendor/`.
5. **Edita la fuente, no la vista.** README, ficha web, temarios del skill y checklists se
   regeneran con `temario-generar.sh`; nunca a mano.
6. **Nada externo se copia.** Libros por `calibre_id`; datasets por clave de `02 analysis`;
   plantillas, logo y fuentes desde el framework. Dentro del curso solo material propio y
   muestras ≤ 5 MB; el doctor avisa de binarios mayores.
7. **Sin esqueletos.** Una nota existe cuando está escrita; `estado: activo` significa
   contenido real. `temario.py` no crea archivos vacíos.
8. **Producto ≠ fuente.** PDF, `publicacion/`, `.build/` y auxiliares LaTeX no se
   versionan; congelar = tag `dictado/<clave>/<sesion>`. La web recibe hardlinks.
9. **Datos de personas solo en `registro/`**, con la clave del dictado.
10. **Un dictado = `dictados/<AAAA-ciclo>-<institucion>-<materia>/dictado.yml`**, aunque
    tome sesiones de varios cursos.
11. **Nada queda sin clasificar dentro del repo.** Lo que llegue fuera del estándar se clasifica en su curso o sale al
   archivo del vault (`06 archives/`), como se hizo con `_inbox/` el 2026-09-20.
12. **Cambios estructurales por el ciclo**: auditoría → propuesta → aprobación → tag →
    cambio con dry-run → `validate.sh --todos` → `doctor.sh` → commit; mapa de rutas
    versionado en `docencia/migracion/` como UNDO.
13. **Un repo de contenido, un commit por cambio.** No se crean repos por área ni por
    curso; si un curso debe publicarse aparte, se exporta (subtree), no se separa.
14. **Todo curso declara `tipo`, `area[]`, `materia_web` y, si aplica, `malla`**
    (paralelo a «todo documento declara su esquema», 2026-09-11). `validate.sh` exige hoy
    `tipo`; `area`/`materia_web` los rellena `new-course.sh` y los lee la web.

## 8. Herramientas del estándar

| Script | Qué hace |
|---|---|
| `new-course.sh` · `new-session.sh` · `new-dictado.sh` | crean solo el registro (y el artefacto del tipo) desde `scaffolds/{curso,sesion,dictado}/` |
| `new-presentation.sh` · `new-evaluacion.sh` · `new-report.sh` | documentos LaTeX desde `templates/` (declaran el artefacto en `sesion.yml`, van a `04-evaluaciones/` y `01-diseno/`) |
| `build.sh` · `build-session.sh` · `build-course.sh` | compilan con LuaLaTeX (o Quarto) el `.tex` dado, el artefacto de una sesión, o todo un curso |
| `validate.sh CURSO\|DICTADO\|--todos` · `stats.sh` | invariantes de §2–§4 (exit ≠ 0 si algo falla) · resumen por sesión |
| `temario-generar.sh` · `enlazar.py` · `normalizar-*.py` | vistas desde `curso.yml` · enlaces posts/simuladores/exámenes · normativa de archivos |
| `publish-session.sh` · `publish-web.sh` | congelar por tag + producto en `publicacion/` · hardlinks a la web |
| `doctor.sh` | entorno + `validate --todos` + verificadores + binarios + remote de `registro/` + normativa |

`new-period.sh` queda como aviso de retiro (exit 2): el dictado ya no vive en el curso.
