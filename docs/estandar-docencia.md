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
docencia/                       ← repo Academic_Class_Framework: tooling, clases, plantillas, scaffolds
├── docencia/                   ← UN submódulo: repo Academic_Class (todo el contenido docente)
│   ├── cursos/<slug>/          ← qué se enseña (uno por carpeta)
│   ├── dictados/<AAAA-ciclo>-<institucion>-<materia>/   ← cada vez que se dicta (manifiesto + producto)
│   ├── migracion/              ← ledger vivo del banco de exámenes; historico/ = mapas y migradores de M3–M6 (son el UNDO)
│   ├── README.md               ← puerta del repo de contenido (a mano; no hay generador)
│   └── CLAUDE.md               ← guía de orientación del asistente (apunta al framework)
└── registro/                   ← repo PRIVADO hermano, git-ignorado aquí; nunca con remote público
    ├── <clave-del-dictado>/    ← estudiantes, asistencia, calificaciones, evidencias
    └── _legado/                ← archivo cerrado (trabajos heredados)
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
  archivo a archivo está en `contenido/migracion/historico/mapa-m3.csv`.

`curso.yml` (claves `snake_case`, normativa §7; `scaffolds/curso/curso.yml` es la plantilla):

```yaml
# cursos/econometria-i/curso.yml — registro del curso econometria-i
id: econometria-i                 # = nombre de la carpeta
alias: [course_03_econometria_i]  # ids anteriores; los resuelven enlazar.py y las fichas de Calibre
titulo: "Econometría I"
estado: borrador                  # borrador | activo | archivado
temario: revisado                 # opcional: el temario se reconstruyó con C1 (decisiones.md, 2026-10-20)
tipo: asignatura                  # asignatura | herramienta | nivelacion | taller
area: [estadistica-econometria]  # vocabulario cerrado de config/areas.yml; el 1.º decide el pub, los demás son secundarios
malla: {plan: economia-unsch, ciclo: 5, orden: 13}
materia_web: econometria          # ficha de web/cursos/<materia>; varios cursos → una materia
prerrequisitos: [estadistica-para-economistas]
etiqueta: econometria
dominio_fuat: econometria         # dominio del learning-skill
unidades: [...]                   # id, titulo, temas[] {id, titulo, archivo: 02-contenido/1-1-tema.md | null, recursos[]}
bibliografia: [{calibre_id: 1234, titulo: …, autor: …, origen: …}]
banco_examenes: []                # enlazar.py examenes
datasets: [{clave: inei/enaho/2019/sumaria, uso: "s01 pobreza"}]   # catálogo de datafw
ajeno: [{ruta: 05-recursos/vendor/plantilla-sbs, descripcion: …}]
```

`validate.sh` exige `id` (= carpeta), `titulo`, `estado` y `tipo`. `temario-generar.sh`
genera de aquí el README del curso, la sección «Contenidos / Sílabo» de la ficha web, el
temario del learning-skill y la checklist de `tareas/temarios-cursos.md`; el doctor
avisa si el README de un curso se desfasó (`temario-generar.sh verificar` compara solo esa vista). `archivo:` de un tema es `null` hasta que la nota existe:
**no hay esqueletos**. Desde la fase 5 de la plataforma educativa (2026-10-20), `archivo:` puede apuntar también a la
lección del tema en su pub, como ruta relativa a `DOCS_ROOT` (`web/_pubs/<pub>/<sección>/<post>/index.qmd`): la nota
de `02-contenido/` se llevó al pub, que es su casa (`web/docs/plataforma-educativa.md` §4.2).

`temario: revisado` marca un curso cuyo temario se reconstruyó desde su mejor fuente (decisión C1, `decisiones.md`,
2026-10-20); un curso sin la clave tiene el temario sin revisar. Solo los cursos revisados entran en
`web/scripts/cursos.py`, que da a cada tema una lección en el pub del curso (la existente, declarada con `curso:` y
`tema:` en su frontmatter, o un esqueleto en borrador). El resto espera a que su temario se revise.

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
  `guion.md` (esquema `presentacion-clase` de `escritura/esquemas/`, alineamiento
  constructivo). Lo que antes iba en `01_Antes … 07_Notas` se fusionó ahí en M4.
- Los decks Beamer siguen siendo autocontenidos (preámbulo propio + copia local del
  logo): al mover una sesión se mueve la carpeta completa. El `deck.tex` que crea
  `new-session.sh --tipo clase` (`scaffolds/sesion/deck.tex`) usa `beamer` con el tema de
  `config/course.yml` (`tema_beamer`); el deck sobre `academic-beamer` lo crea `new-presentation.sh`.

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
- **Congelar = etiquetar**: `publish-session.sh` deposita el producto (la versión del estudiante, §10.7)
  en `publicacion/<web>/` (con `_PUBLICADO.md`) y pone el tag
  `dictado/<clave>/<sesion>` sobre el commit de las fuentes. No se copia nada al repo. `--simular` dice qué
  publicaría sin escribir ni etiquetar.
- Un dictado con datos que solo sabe el docente lleva `estado: borrador` y la lista `por_confirmar:`; al
  confirmarlos se borra la lista y pasa a `activo` (ejemplo: `dictados/2026-ii-unsch-econometria/`).
- `publish-web.sh DICTADO --aplicar` enlaza el producto **por hardlink** (un solo inodo)
  en `web/_pubs/<pub>/_ediciones/<dictado>/<web>/` (el pub del curso; hasta la fase 7, `web/cursos/…`). La web nunca es fuente; el doctor avisa
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
  (`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §2.1); línea 1 de identidad en cada registro.
- Períodos `AAAA-i` / `AAAA-ii`.
- Fuera de norma solo `vendor/` (ajeno, declarado en `ajeno:`):
  el validador no entra en ellos. Los adjuntos heredados con espacios que lee código
  (`.do`, `.rmd`, `.ipynb`) se conservan; la normativa los admite (§4).

## 6. Relación con el ecosistema

| Necesidad | Dónde vive | Cómo la cita el curso |
|---|---|---|
| Libros y artículos | Calibre (`biblioteca/`) | `bibliografia[].calibre_id` (`biblioteca-studio/ingesta_cursos` lo escribe) |
| Datasets oficiales (ENAHO, INEI, Damodaran…) | catálogo de `datafw` (`data/raw/…`) | `datasets[].clave`; el curso conserva solo muestras ≤ 5 MB |
| Series para el `code/` de una evaluación o para un modelo del laboratorio | paquetes de resultados y datos de `datafw`, leídos por nombre (`core/env.py`) | el código del expediente o del modelo; contrato del proveedor en `datafw/docs/integracion-ecosistema.md` |
| Logo, fuentes, plantillas, clases | `assets/`, `styles/`, `templates/`, `classes/` del framework | `\documentclass{academic-*}`; el deck lleva **una** copia local del logo |
| Apuntes de Edison como alumno | `notas/40-cursos-y-formacion/<curso>/` | enlazan al tema de `02-contenido/`; nunca escriben en `docencia/` |
| Curso y ediciones en la web | el pub del área (`config/areas.yml`): la vitrina `web/_aula` genera `/cursos/<curso>/` y `/ediciones/<dictado>/` | `curso.yml` y `dictado.yml`; `materia_web` solo para las fichas heredadas del hub |
| Temario del learning-skill | `prompts/skills/learning/2 domains/_temarios/` | generado desde `curso.yml`; `dominio_fuat` |
| Posts, simuladores, bancos de exámenes | `web/_pubs`, el repo `simuladores` (`SIMULADORES_DIR`; su `catalogo.json`), `contenido/cursos/*/04-evaluaciones/banco` | `enlazar.py` (los ids antiguos se resuelven por `alias`) |

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
6. **Nada externo se copia.** Libros por `calibre_id`; datasets por clave de `datafw`;
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
   archivo del vault (`archivo/`), como se hizo con `_inbox/` el 2026-09-20.
12. **Cambios estructurales por el ciclo**: auditoría → propuesta → aprobación → tag →
    cambio con dry-run → `validate.sh --todos` → `doctor.sh` → commit; mapa de rutas
    versionado en `contenido/migracion/` como UNDO.
13. **Un repo de contenido, un commit por cambio.** No se crean repos por área ni por
    curso; si un curso debe publicarse aparte, se exporta (subtree), no se separa.
14. **Todo curso declara `tipo`, `area[]`, `materia_web` y, si aplica, `malla`**
    (paralelo a «todo documento declara su esquema», 2026-09-11). `validate.sh` exige
    `tipo` y que cada `area` pertenezca al vocabulario cerrado de `config/areas.yml`
    (2026-10-20): el primer valor es el área principal y decide en qué pub vive el curso
    (`scripts/areas.py pub CURSO`); los siguientes lo listan también en otros pubs. El vínculo
    área ↔ pub se escribe solo en `config/areas.yml`, nunca en el `curso.yml`.

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

## 9. Consumidores

Lo que este estándar produce lo leen o lo reciben otros repos del ecosistema. Las órdenes que
regeneran cada vista están en [`como-se-mantiene.md`](como-se-mantiene.md) §2; aquí, quién depende
de qué.

| consumidor | qué recibe o lee | cómo llega | qué no debe hacer |
|---|---|---|---|
| `web` | la sección «Contenidos / Sílabo» de `cursos/<materia>/index.qmd`, entre las marcas `temario:inicio`/`temario:fin` | `scripts/temario.py` (`--que web`) | editar entre las marcas |
| `web` | el producto de cada dictado en `cursos/<materia>/<edicion>/` | `scripts/publish-web.sh` (hardlinks desde `contenido/dictados/<clave>/publicacion/`) | copiar en vez de enlazar |
| `prompts` (learning-skill) | `skills/learning/2 domains/_temarios/<dominio>.md` y un puntero en `## Temario` del dominio | `scripts/temario.py` (`--que skill`), por `dominio_fuat` | editar el temario generado |
| `tareas` | `temarios-cursos.md`, la checklist por curso, unidad y tema | `scripts/temario.py` (`--que resumen`) | editarla a mano |
| `web/_aula` (vitrina de los pubs) | `curso.yml` (temario, `alineamiento`, `politica_ia`), las rúbricas de `01-diseno/rubricas/`, `sesion.yml` y `recuperacion.yml` de cada sesión, `dictado.yml` y su `publicacion/` | lectura directa en cada build (`web/_aula/src/lib/fuentes.mjs`); el banco, sin `respuesta` ni `explicacion` | escribir en el contenido |
| `biblioteca-studio` (`ingesta_cursos`) | lee `contenido/cursos/*/05-recursos/` y escribe `bibliografia[].calibre_id` en el `curso.yml` | su suite (`biblioteca-studio/ingesta/README.md`) | cambiar otras claves del registro |

Un cambio en `curso.yml` (claves, `materia_web`, `dominio_fuat`) o en la lista cerrada de carpetas
afecta a estos consumidores: se regeneran las vistas y se avisa al dueño del consumidor.

## 10. Alineamiento, recuperación, rúbricas y uso de IA

> Desde el 2026-11-18. Implementa el campo 10 (y C11.3, C12.4) de la norma
> `prompts/00 metodo/FLUJO_DE_CONOCIMIENTO.md`; cada regla cita la obra que la funda, tal como está en su fundamento.
> Lo verifica `scripts/alineamiento.py verificar`, que `validate.sh` llama en cada curso que declara `alineamiento:`
> o tiene sesiones con `dinamica:`. Cada error lleva su línea «por qué · fuente». Aplicado en `econometria-i`.

### 10.1 Matriz de alineamiento (`curso.yml` → `alineamiento`)

Resultado → evidencia → actividad: cada **resultado** se evidencia en al menos una **evaluación** y se trabaja en al
menos una **sesión**; cada evaluación declara los resultados que mide (Biggs, 1996; Wiggins y McTighe, 2005).

```yaml
alineamiento:
  fuente: Biggs (1996); Wiggins y McTighe (2005)
  alcance: <qué parte del temario cubre, si no es todo>
  resultados:                   # nivel: taxonomía SOLO (uniestructural, multiestructural, relacional, abstracto_ampliado)
  - {id: ra1, nivel: relacional, enunciado: …}
  evaluaciones:                 # tipo: formativa | sumativa; las sumativas suman peso 100
  - {id: ev-x, titulo: …, tipo: sumativa, peso: 40, resultados: [ra1], rubrica: 01-diseno/rubricas/x.yml,
     consigna: 03-sesiones/sNN-…/consigna.tex, sesion: sNN-…, politica_ia: asistida}
  evaluacion_curso: {resultados: [ra1, ra2], descripcion: …, fuente: …}   # §10.6
```

La **actividad** es la sesión: `sesion.yml` declara `resultados_aprendizaje: [ra1, …]` con los `id` del curso. Son
error: un resultado sin evaluación o sin sesión, una evaluación sin resultado o con uno inexistente, pesos sumativos
que no suman 100, una sesión con un resultado no declarado y un criterio de rúbrica que mide un resultado que su
evaluación no declara. Una sumativa sin rúbrica (ni `instrumento: prueba`) y un resultado solo con evaluación
formativa son aviso. La matriz se imprime con `alineamiento.py matriz CURSO [--formato md|tex]`.

### 10.2 Banco de recuperación por sesión (`03-sesiones/sNN-…/recuperacion.yml`)

`{sesion, fuente, preguntas: [{id, resultado, tipo: abierta|opcion|numerica, enunciado, opciones?, respuesta,
explicacion?}]}`. Mínimo tres preguntas por sesión con resultados; `id` únicos en el curso; cada pregunta recupera
un resultado declarado. `alineamiento.py banco CURSO sNN` arma el cuestionario de una clase: las preguntas de la
sesión y un repaso intercalado de las sesiones a 1, 2, 4 y 8 de distancia (`--examen`: muestra de todas las
anteriores). Se responde sin apuntes (Roediger y Karpicke, 2006); el espaciado multiplica el efecto (Cepeda et al.,
2006). Las distancias exactas son decisión de diseño (`decisiones.md`), no de la obra. Para repasar fuera de clase,
`alineamiento.py mazo CURSO [sNN…] [--formato anki|csv] [--salida RUTA]` exporta los bancos (todas las sesiones, si no
se eligen) como mazo: la pregunta al frente y la respuesta de la puesta en común al reverso, con las etiquetas
`<curso>::sNN` y `<curso>::raN` y un identificador estable por pregunta (reimportar actualiza, no duplica). `anki` es un
TSV con las cabeceras de importación de Anki (2.1.55 o posterior); `csv`, el mismo contenido en texto plano. Solo viajan
el enunciado, las opciones, la respuesta y la explicación.

### 10.3 Rúbricas analíticas (`01-diseno/rubricas/<clave>.yml`)

Cumplen el **formato común del ecosistema**, `escritura/config/entrega/rubrica.schema.yml`, sin claves propias:
`{clave, titulo, fuente, curso, criterios: [{clave, nombre, peso, niveles: [{puntaje, nombre, descriptor}]}]}`
(opcionales del esquema: `descripcion`, `aprobatorio`, `para`; por criterio, `descripcion` y `veto`). Así LaTeX Studio
las lee para la autoevaluación del estudiante («Antes de entregar», con `rubrica:` de su `registro/entrega.yml`
apuntando al YAML del curso). Lo comprueba `alineamiento.py verificar` en **todo** YAML de `01-diseno/rubricas/` de
cualquier curso, con el validador de escritura (`$WRITING_DIR/scripts/entrega/rubrica.py`, sin copiarlo), más la regla
del curso: los pesos suman 100. El nombre de cada nivel (Destacado, Logrado…) va en `nombre` del nivel. Lo que el
esquema no guarda se declara en `curso.yml`: el **resultado que mide cada criterio**, en
`alineamiento.rubricas: {<clave de la rúbrica>: {<criterio>: raN}}` (error si el criterio o el resultado no existen,
o si la evaluación que usa la rúbrica no declara ese resultado; aviso si un criterio queda sin resultado). La
**nota**: el esquema da la ponderada sobre 100 (Σ (puntaje ÷ máximo del criterio) × peso ÷ Σ peso); la vigesimal del
registro se deriva, nota sobre 100 × 20 ÷ 100, sin redondeo intermedio: `alineamiento.py calificar RUBRICA.yml
PUNTAJES.csv` da las columnas `codigo`, `nota` (vigesimal), `nota_100` y `vetos` desde una tabla que vive en `registro/`. La rúbrica se
**publica con la consigna**: `generar` escribe la tabla `<clave>.tex` (generada, no se edita) y la consigna la
incluye con `\input`; en el anexo del sílabo cada rúbrica sale una vez, con las evaluaciones que la usan. Las
rúbricas ayudan cuando se comparten antes y se usan para formar (Jonsson y Svingby, 2007; Panadero y Jonsson, 2013).

### 10.4 Sesión de aprendizaje activo (`dinamica: aprendizaje_activo`)

En `sesion.yml`, con cualquier `tipo`. Su `guion.md` tiene `## Problema`, `## Trabajo en parejas` y
`## Puesta en común`, cada uno con su tiempo `(NN min)` (sin tiempo, aviso). `new-session.sh … --activo` la crea
desde `scaffolds/sesion/guion-activo.md` (Freeman et al., 2014; Allgood et al., 2015).

### 10.5 Política de IA por curso y por evaluación

`curso.yml` → `politica_ia: {regla, declaracion, datos, fuente}`; cada evaluación declara `politica_ia` de un
vocabulario cerrado: `prohibida`, `apoyo` (ideas, dudas y lenguaje, declarado), `asistida` (código o borrador
verificado, declarado) y `libre` (todo uso, declarado y verificado). Va **en el sílabo**: `generar` escribe
`01-diseno/politica-ia.tex` (regla, uso permitido en cada evaluación, cómo se declara, datos vedados y fuente) y la
plantilla `templates/report/silabo/` lo incluye en su sección «Uso de la inteligencia artificial»
(`\InputIfFileExists`; sin el fragmento, la sección dice cómo llenarla); el anexo del sílabo incluye el mismo
fragmento (Comisión Europea, 2025; CONCYTEC, 2024). Ningún dato de estudiantes ni de `registro/` va a una herramienta
externa.

### 10.6 Evaluación del propio curso

`alineamiento.evaluacion_curso` elige dos o tres resultados clave, cada uno con al menos dos preguntas en los bancos;
`alineamiento.py pre-post CURSO` imprime la prueba que se toma al iniciar y al cerrar. Los resultados por pregunta se
anotan en `registro/<dictado>/`, nunca aquí (Black y Wiliam, 1998; Allgood et al., 2015).

### 10.7 Vistas y plantillas

`alineamiento.py generar CURSO [--aplicar]` (simula sin `--aplicar`) escribe el fragmento de la política de IA
(`01-diseno/politica-ia.tex`, en todo curso que la declare), el anexo del sílabo del curso
(ejemplo: `contenido/cursos/econometria-i/01-diseno/alineamiento/alineamiento.tex`; anexo: matriz, evaluaciones con su política de IA, medición del curso y rúbricas) y la tabla `.tex` de
cada rúbrica; `verificar` falla si una vista se desfasó. Plantillas del framework (`templates/report/`): `cornell`
(C3.5), `ronda-de-pares` (C11.3), `prueba-de-comprension` (C9.4). Material de Metodología:
`contenido/cursos/seminario-de-investigacion/01-diseno/guia-de-tesis/` (C7.5) y
`contenido/cursos/seminario-de-investigacion/05-recursos/talleres/` (matrices comentadas C1.4, lectura lateral C2.6,
reescritura C6.4).

**Lo que llega al estudiante.** `publish-session.sh` publica, además de los documentos de la sesión, el banco de
recuperación sin claves (`evaluation/recuperacion.md`, de `alineamiento.py banco CURSO sNN --estudiante`), el mismo
banco como mazo para Anki (`mazo.tsv` en practice, de `alineamiento.py mazo CURSO sNN`), la hoja Cornell para la web
(`practice/cornell.md`, en los cursos con `alineamiento`) y toda `plantilla*.md` de la raíz de la sesión
(`practice/`). La clave, el solucionario y la nota para el docente de un taller o una guía (`academic-report`) van
dentro de `\begin{paradocente}…\end{paradocente}`; `build.sh X.tex --modo estudiante` compila `X-estudiante.pdf` sin
ellos (y `\versionestudiante{texto del estudiante}{texto del docente}` adapta una consigna), y la publicación toma esa
versión con el nombre `X.pdf`. Nunca se publican `*-claves.pdf`, `*-soluciones.pdf` ni `*-docente.pdf`. Una sesión de
laboratorio cuyo artefacto es código que resuelve el laboratorio (`laboratorio.py`) no lo publica: lleva una hoja del
estudiante, `practica-laboratorio.tex` (`academic-report`: enunciado, pasos y preguntas; las cifras esperadas en
`paradocente`), que se publica en practice como `practica-laboratorio.pdf`. El aula (`web/_aula`) muestra en la página
del curso los resultados con su evidencia, la evaluación con su uso de IA, las rúbricas y, por sesión, el banco sin
claves con el enlace a su mazo publicado (`web/_aula/docs/decisiones.md` §1.23).
