---
tipo: readme
estado: activo
---
# scripts/ — la automatización del framework: crear, compilar, validar, generar y publicar

Dueña de todo lo que se ejecuta. Patrón fijo: el script de entrada **solo orquesta**; la lógica
compartida está en `lib/common.sh` y los parámetros ajustables, en `config/course.yml`. Ningún
script tiene rutas de máquina: `lib/common.sh` resuelve el repo desde su propia ubicación.

Todos los argumentos `CURSO` y `DICTADO` aceptan **slug o ruta** (`docencia/cursos/<slug>`,
`docencia/dictados/<clave>`) desde M5 (2026-09-15).

## Uso

```bash
cd ~/Documents/10\ Class
./scripts/doctor.sh                       # lo primero ante cualquier duda
./scripts/validate.sh --todos             # el estándar en los 52 cursos y los 2 dictados
bash -n scripts/<archivo>.sh              # comprobación de sintaxis: UN archivo por invocación
```

## Estructura

| Script | Qué hace | Uso |
|---|---|---|
| `lib/common.sh` | **la librería**: rutas (`FW_DIR`, `DOCENCIA_DIR`, `CURSOS_DIR`, `DICTADOS_DIR`, `INBOX_DIR`, `REGISTRO_DIR`), `yaml_get`, `config_get`, `slugify`, `latex_engine`, `compile_tex` y los resolutores `is_course`/`course_dir`/`dictado_dir`/`session_dir`/`list_*`/`session_artifact` | se carga con `source`; no se ejecuta |
| `new-course.sh` | crea un curso: solo `curso.yml` y `README.md` desde `scaffolds/curso/` | `./scripts/new-course.sh SLUG "Título" [--tipo asignatura\|herramienta\|nivelacion\|taller] [--area a,b] [--materia-web m]` |
| `new-session.sh` | crea una sesión: `sesion.yml`, `guion.md` y el artefacto que exige el tipo | `./scripts/new-session.sh CURSO NN "Título" [--tipo clase\|laboratorio\|taller\|evaluacion] [--quarto] [--artefacto NOMBRE]` |
| `new-dictado.sh` | crea un dictado: `dictado.yml` + la carpeta hermana en `registro/` | `./scripts/new-dictado.sh AAAA-ciclo INSTITUCION MATERIA "Título" [--web-edicion EDICION]` |
| `new-presentation.sh` | diapositivas `academic-beamer` (8 tipos) en la sesión; declara `artefacto` en `sesion.yml` | `./scripts/new-presentation.sh CURSO NN "Título" [--tipo TIPO]` |
| `new-evaluacion.sh` | evaluación `academic-exam` (12 plantillas) en `04-evaluaciones/<sub>/AAAAMMDD_sig.tex` | `./scripts/new-evaluacion.sh CURSO TIPO "Título" [--fecha AAAAMMDD]` |
| `new-report.sh` | documento de gestión `academic-report` en `01-diseno/` | `./scripts/new-report.sh CURSO silabo\|calendario\|nota-docente\|rubrica "Título"` |
| `build.sh` | compila **cualquier** `.tex` del framework con LuaLaTeX, en el modo pedido | `./scripts/build.sh ARCHIVO.tex [--modo examen\|claves\|soluciones\|todos] [--clean]` |
| `build-session.sh` | compila el artefacto declarado en `sesion.yml` (`.tex` o `.qmd`) | `./scripts/build-session.sh CURSO NN` |
| `build-course.sh` | compila un curso entero | `./scripts/build-course.sh CURSO [--solo-sesiones]` |
| `clean.sh` | borra auxiliares de LaTeX (y los PDF con `--pdf`) | `./scripts/clean.sh [--pdf] [DIR]` |
| `validate.sh` | invariantes del estándar: lista cerrada de carpetas, sin vacías, artefacto por tipo, `guion.md`, núcleo del registro | `./scripts/validate.sh CURSO\|DICTADO\|--todos` |
| `stats.sh` | resumen de un curso por sesión: tipo · estado · artefacto · PDF · guion | `./scripts/stats.sh CURSO` |
| `doctor.sh` | entorno (git, lualatex, quarto, compilador universal) + `validate --todos` + los tres verificadores + binarios > 5 MB + remoto de `registro/` + `core/archivos.py` | `./scripts/doctor.sh` |
| `temario-generar.sh` | fachada Bash de `temario.py` | `./scripts/temario-generar.sh migrar\|generar\|verificar [--aplicar] [--que readme,web,skill,resumen] [CURSO…]` |
| `temario.py` | el generador de vistas del currículo desde `curso.yml`: README del curso, ficha web, temario del learning-skill, checklist de `05 tasks` | ver `temario-generar.sh` |
| `enlazar.py` | enlaza el currículo con lo que ya existe: posts de `04 index/_pubs`, modelos de `simuladores/`, bancos de `04-evaluaciones/` | `python3 scripts/enlazar.py posts\|simuladores\|examenes\|verificar [--aplicar]` |
| `publish-session.sh` | congela una sesión: tag `dictado/<clave>/<sesion>` + producto en `publicacion/<web>/` (git-ignorado) | `./scripts/publish-session.sh DICTADO CURSO NN [--refrescar]` |
| `publish-web.sh` | fachada de `publicar-web.py` | `./scripts/publish-web.sh DICTADO [--aplicar]` |
| `publicar-web.py` | enlaza el producto de un dictado **por hardlink** en `04 index/cursos/<materia>/<edicion>/`; crea `index.qmd`/`_links.md` solo si faltan | `python3 scripts/publicar-web.py DICTADO [--aplicar]` |
| `normalizar-archivos.py` | normativa de archivos en el framework y el contenido: registros, nombres, cabeceras, frontmatter, artefactos, `vendor/` | `python3 scripts/normalizar-archivos.py todo\|registros\|cursos\|nombres\|cabeceras\|frontmatter\|artefactos\|vendor [--aplicar] [--bitacora DIR]` |
| `normalizar-notas.py` | las notas de `02-contenido/` al régimen del vault: kebab-case y frontmatter, reescribiendo wikilinks y `archivo:` | `python3 scripts/normalizar-notas.py [--aplicar] [--bitacora DIR] [CURSO…]` |
| `new-period.sh` | **retirado** en M5: imprime el sustituto y sale con 2 | `./scripts/new-dictado.sh` en su lugar |

## Límite honesto

- **Nada de esto es un test.** `validate.sh` comprueba forma, no contenido: que la sesión tenga su
  artefacto no significa que el artefacto esté bien.
- **Sin `--aplicar` todo simula** en `temario.py`, `enlazar.py`, `publicar-web.py` y los dos
  normalizadores. Los `new-*.sh` y los `build-*.sh` sí escriben directamente.
- **`compile_tex` prefiere el compilador universal del workspace** y ese compilador **borra el PDF**
  cuando la compilación falla; si el PDF estaba versionado, se recupera con `git checkout`.
- **`bash -n` comprueba un archivo por invocación**: con varios argumentos solo mira el primero.
- **En zsh y con rutas con espacios** (`10 Class`) se itera con `while read`, nunca con `for x in $(…)`.
- `__pycache__/` no se versiona; si aparece, se borra.
