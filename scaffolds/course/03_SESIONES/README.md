# 03_SESIONES — Las clases del curso

> **Responsabilidad única:** una carpeta **`SNN_<slug>/`** por cada **sesión de
> clase**, con la anatomía interna `01_Antes … 07_Notas`. Aquí vive la **docencia en
> vivo**: el deck de diapositivas, el plan de clase, la actividad, el guion del
> docente. El contenido teórico está en `02_CONTENIDO`; aquí se **enseña**.

## Organización

```
03_SESIONES/
├── S01_introduccion/
│   ├── metadata.yml          ← ficha de la sesión (validate.sh la lee)
│   ├── README.md             ← portada de la sesión
│   ├── 01_Antes/             ← plan de clase, preparación
│   ├── 02_Clase/             ← EL DECK (.tex/.qmd) + logo  ← lo esencial
│   ├── 03_Actividad/         ← ejercicios en clase
│   ├── 04_Evaluacion/        ← quiz/salida de la sesión
│   ├── 05_Despues/           ← tarea, cierre
│   ├── 06_Recursos/          ← links, datasets de la sesión
│   └── 07_Notas/             ← guion del docente, retrospectiva
├── S02_estructura/
└── …
```

La anatomía completa `01_Antes…07_Notas` está documentada en el esqueleto
[`scaffolds/session/`](../../session/README.md).

## Nomenclatura

- **`S<NN>_<slug>`**: `S` mayúscula + número de dos dígitos + `_` + slug ASCII.
  `S01_introduccion`, `S06_referencias`. El `NN` fija el orden de las sesiones.
- El **deck** vive en `02_Clase/` (`diapositivas.tex` o `.qmd`); es autocontenido
  (preámbulo propio + copia local del logo). Al mover una sesión, mueve la carpeta
  **completa**.

## Cómo se crea una sesión y su deck

```bash
./scripts/new-session.sh      "$COURSE" 07 "Marco Teórico"            # crea S07_marco_teorico/ (anatomía)
./scripts/new-presentation.sh "$COURSE" 07 "Marco Teórico" --tipo clase   # deck → S07/02_Clase/diapositivas.tex
./scripts/build-session.sh    "$COURSE" 07                             # compila el deck
```

`new-session.sh` copia `scaffolds/session/` y sustituye los `{{PLACEHOLDERS}}` con los
datos de `config/course.yml`. Con `--quarto`, el deck es RevealJS en vez de Beamer.

## Qué NO va aquí

- Exámenes y prácticas → [`04_EVALUACIONES/`](../04_EVALUACIONES/README.md) (aunque la
  **evaluación de salida** breve de la propia sesión sí va en `SNN/04_Evaluacion/`).
- El temario teórico → [`02_CONTENIDO/`](../02_CONTENIDO/README.md).

## Ejemplo — `metadata.yml` de una sesión (extracto)

```yaml
numero: 01
titulo: "Introducción a APA"
slug: introduccion
unidad: 1
semana: 01
duracion_minutos: 180
modalidad: presencial
formato_slides: latex-beamer
estado: impartida        # en_preparacion | lista | impartida
```
