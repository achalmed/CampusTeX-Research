# publicacion — El MOOC de este dictado (se congela por sesión)

> **Responsabilidad única:** la **publicación** de este dictado, organizada **como un
> MOOC**: un módulo por sesión y, dentro, solo `slides · evaluation · practice ·
> homework`. **Una sola estructura**, agnóstica de plataforma, que alimenta a todos los
> canales (sitio `pub_*`, Moodle, Classroom…) por **hardlink**.
>
> **Publicar una sesión = congelarla.** Cuando terminas una sesión y la publicas aquí,
> su módulo queda **congelado** (no se vuelve a editar). El MOOC del dictado se arma
> **sesión a sesión**.

## Por qué NO hay carpetas por plataforma

Una sola copia por entregable; cada canal **enlaza** (idealmente **hardlink**, mismo
inodo) a este staging. Publicar en 3 plataformas = 0 duplicados; corregir un PDF =
corregido en todas.

## Estructura: un módulo por sesión

```
publicacion/
├── README.md
├── index.md                 ← landing del MOOC de ESTE dictado (índice de módulos)
├── _plantilla_modulo/       ← plantilla: copiar como S01_<slug>/, S02_<slug>/ …
│   ├── index.md  ·  slides/  evaluation/  practice/  homework/
├── S01_introduccion/        ← un módulo real (congelado al publicarse)
└── S02_estructura/
```

Los módulos se nombran **igual que las sesiones** (`S<NN>_<slug>`, como en
`03_SESIONES/`).

## Qué va en cada carpeta del módulo (fuente → publicado)

| Carpeta MOOC | Fuente en el curso | Qué se publica |
|---|---|---|
| `slides/` | `03_SESIONES/SNN/02_Clase/diapositivas.pdf` | el deck **final** (PDF; o HTML si Quarto) |
| `evaluation/` | `04_EVALUACIONES/…` de esa sesión | examen **propuesto + su solución** (PDF) |
| `practice/` | `03_SESIONES/SNN/03_Actividad/` · `04_EVALUACIONES/practicas/` | práctica final (PDF) |
| `homework/` | `03_SESIONES/SNN/05_Despues/` · `04_EVALUACIONES/tareas/` | tarea final (PDF) |

Solo archivos **finales** (PDF/HTML), no las fuentes `.tex`/`.qmd`.

## Enlace por hardlink al ecosistema `pub_*`

```bash
# Publicar (y congelar) el deck final de la sesión 01 de este dictado
ln 03_SESIONES/S01_introduccion/02_Clase/diapositivas.pdf \
   09_SEMESTRES/2026-I/publicacion/S01_introduccion/slides/diapositivas.pdf

# El sitio pub_* enlaza (hardlink) desde este staging a su carpeta de contenidos
ln 09_SEMESTRES/2026-I/publicacion/S01_introduccion/slides/diapositivas.pdf \
   ~/Documents/pub_<blog>/posts/…/diapositivas.pdf
```

- **Hardlink** ⇒ una sola copia física; requisito: mismo sistema de archivos.
- Una vez publicado, el módulo **no se edita** (está congelado): si necesitas cambiarlo,
  publicas una corrección fechada, no reescribes lo ya entregado.

## Crear un módulo (por sesión)

```bash
cp -a _plantilla_modulo S01_introduccion      # mismo nombre que 03_SESIONES/S01_introduccion
# enlaza los PDF finales y edita S01_introduccion/index.md
```

## Ejemplo — un módulo publicado

```
publicacion/S05_citas/
├── index.md
├── slides/diapositivas.pdf
├── evaluation/20260502_CL.pdf · 20260502_CL-soluciones.pdf
├── practice/practica_citas.pdf
└── homework/tarea_05.pdf
```
