# scaffolds/ — Esqueletos de carpetas del estándar Academic_Class

> **Qué es esta carpeta.** Los tres **esqueletos de carpetas** (no compilables) que
> definen, al carácter, la estructura de **todos** los `Academic_Class-*` del
> workspace. No contienen documentos LaTeX (eso vive en `templates/`); contienen la
> **organización, la nomenclatura y la documentación** de cada carpeta del estándar.
>
> Esta carpeta es, además, **tu guía**: cada subcarpeta trae un `README.md` que
> explica qué va, qué no va, cómo se nombra y un **ejemplo inline en Markdown** de su
> contenido real (aunque el archivo real sea `.tex`, `.pdf`, `.csv`…). Léela como el
> manual del estándar.

---

## Los tres esqueletos

| Esqueleto | Se copia con | Se despliega como | Documenta |
|---|---|---|---|
| [`course/`](course/README.md)  | `scripts/new-course.sh`  | `Academic_Class-<Área>/course_NN_<slug>/` | el árbol **00–09** de un curso |
| [`session/`](session/README.md) | `scripts/new-session.sh` | `course_NN/03_SESIONES/SNN_<slug>/`       | la **anatomía de sesión** `01_Antes…07_Notas` |
| [`period/`](period/README.md)  | `scripts/new-period.sh`  | `course_NN/09_SEMESTRES/<AAAA-ciclo>/`    | un **dictado**: registro privado + publicación MOOC |

---

## Cómo se propaga esta documentación (importante)

Los scripts copian el esqueleto con `cp -a`, así que **los `README.md` por carpeta
viajan al curso real**: cada curso y cada sesión que crees queda **autodocumentado**
sin trabajo extra. Consecuencias de diseño que conviene conocer:

- **`README.md` reemplaza a `.gitkeep`.** Una carpeta con `README.md` ya no está
  vacía, así que Git la rastrea igual. En este árbol no hay `.gitkeep`: el README
  hace ese trabajo **y además** documenta.
- **`course/README.md` es solo guía.** `new-course.sh` **regenera** el `README.md`
  del curso tras copiar (con un heredoc corto), así que el `course/README.md`
  extenso de aquí **no** se filtra al curso real: sirve para que tú leas el estándar.
- **`session/README.md` sí se despliega** (con los `{{PLACEHOLDERS}}` sustituidos por
  `new-session.sh`): es la portada real de cada sesión.
- Los ejemplos van **dentro** de cada README (bloques de muestra), no como archivos
  sueltos, para no ensuciar los cursos reales con ficheros de ejemplo.

---

## Nomenclatura del estándar (reglas duras, válidas en todo el árbol)

- **Carpetas: ASCII, sin tildes ni ñ, sin espacios.** `04_EVALUACIONES`,
  `banco_preguntas`, `Unidad_01`. Portabilidad + los scripts las parsean.
- **Prefijo numérico de dos dígitos** donde hay orden: `00_…`, `01_…`, `Unidad_01`,
  `S01_…`. El cero a la izquierda mantiene el orden alfabético = orden lógico.
- **`snake_case`** para carpetas compuestas (`examen_parcial`, `evaluaciones_aplicadas`).
- **Archivos de contenido** (`02_CONTENIDO`): admiten espacios y numeración `N M`
  (`1 1 sistema apa.md`); ver [`course/02_CONTENIDO/`](course/02_CONTENIDO/README.md).
- **Documentos LaTeX generados** por los scripts: nombre fijo según el script
  (`diapositivas.tex`, `silabo.tex`) o `AAAAMMDD_SIGLA.tex` para evaluaciones
  (ver [`course/04_EVALUACIONES/`](course/04_EVALUACIONES/README.md)).
- **Slug de curso/sesión:** minúsculas, sin tildes, `_` por separador
  (lo genera `slugify()` en `scripts/lib/common.sh`).

---

## Qué NO va en `scaffolds/`

- **Documentos compilables** (`.tex` de examen, diapositivas): van en `templates/`.
  Aquí solo hay esqueletos de carpetas + su documentación.
- **Contenido real** de un curso concreto: va en el `Academic_Class-<Área>/`
  correspondiente, nunca en el framework.
- **Diseño** (colores, fuentes): vive en `styles/` + `config/`.

> Fuente de verdad arquitectónica: [`../docs/00-arquitectura.md`](../docs/00-arquitectura.md).
> Estándar 00–09 en detalle: [`course/README.md`](course/README.md).
