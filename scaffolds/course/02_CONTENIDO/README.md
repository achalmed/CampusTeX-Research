# 02_CONTENIDO — El temario del curso (en Markdown)

> **Responsabilidad única:** el **conocimiento** del curso, escrito como notas
> Markdown enlazables (estilo vault de Obsidian), organizado por **unidades
> temáticas**. Es la materia prima de la que salen las diapositivas (`03_SESIONES`) y
> las evaluaciones (`04_EVALUACIONES`); no es la clase ni el examen, es el contenido.

## Organización: una carpeta por unidad

```
02_CONTENIDO/
├── Unidad_01/   1 1 tema.md · 1 2 tema.md … · figuras/ · lecturas/
├── Unidad_02/   2 1 tema.md · 2 2 tema.md …
├── Unidad_03/   …
└── Unidad_04/   …
```

- Una **`Unidad_NN/`** por unidad del sílabo. Crea tantas como necesites (el esqueleto
  trae 4; los cursos reales tienen las que hagan falta —el piloto APA tiene 6—).
- Cada unidad puede llevar [`figuras/`](Unidad_01/figuras/README.md) (imágenes del
  temario) y [`lecturas/`](Unidad_01/lecturas/README.md) (PDFs de lectura).
- La convención completa de un tema está en [`Unidad_01/`](Unidad_01/README.md).

## Nomenclatura de los archivos de tema (regla del vault)

- **`<unidad> <tema> titulo en minusculas.md`** — con **espacios**, sin tildes.
  Ejemplos reales: `1 1 sistema apa.md`, `3 6 cita de tres o mas autores.md`.
- El doble número `N M` = **unidad N, tema M**; ordena los temas dentro de la unidad.
- Cada `.md` abre con **frontmatter YAML** de etiquetas (para Dataview/Obsidian).

## Qué NO va aquí

- Las **diapositivas** que exponen este contenido → `03_SESIONES/SNN/02_Clase/`.
- Las **lecturas de referencia del curso entero** (no de una unidad) →
  [`06_RECURSOS/`](../06_RECURSOS/README.md).

## Ejemplo — `Unidad_01/1 1 sistema apa.md` (contenido de muestra)

```markdown
---
title: "Sistema APA"
tags:
  - apa
  - redaccion_academica
  - sistema_apa
---

# Sistema APA

El estilo APA (American Psychological Association) es un conjunto de normas para...

## Puntos clave
- Formato del documento
- Citación en el texto
- Lista de referencias

Ver también: [[1 2 que es el estilo apa]]
```
