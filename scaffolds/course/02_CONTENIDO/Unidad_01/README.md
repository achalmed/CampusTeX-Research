# Unidad_01 — Una unidad temática (plantilla de referencia)

> Esqueleto de **una unidad** del temario. Documenta la convención que siguen
> **todas** las unidades (`Unidad_02`, `Unidad_03`, …). Copia esta carpeta para crear
> una unidad nueva.

## Contenido

| Elemento | Qué es |
|---|---|
| `N M titulo.md` | un archivo por **tema** de la unidad (con frontmatter YAML) |
| [`figuras/`](figuras/README.md) | imágenes que citan los `.md` de esta unidad |
| [`lecturas/`](lecturas/README.md) | PDFs de lectura obligatoria/complementaria de la unidad |

## Nomenclatura de los temas

- `<N> <M> titulo en minusculas sin tildes.md` → `1 1 sistema apa.md`,
  `1 6 integridad academica y plagio.md`.
- `N` = número de la unidad (coincide con `Unidad_0N`); `M` = orden del tema.
- Frontmatter obligatorio con `title` y `tags` (dos etiquetas de curso + una del tema
  en `snake_case`).

## Enlaces entre temas

Se enlazan con la sintaxis de wiki-links de Obsidian: `[[1 2 que es el estilo apa]]`.
Así el temario es navegable como grafo dentro del vault.

## Ejemplo — `1 2 que es el estilo apa.md`

```markdown
---
title: "Qué es el Estilo APA"
tags:
  - apa
  - redaccion_academica
  - estilo_apa
---

# Qué es el Estilo APA

Definición, alcance y por qué se usa en las ciencias sociales...

![Portada APA 7](figuras/portada_apa7.png)

Lectura: `lecturas/manual_apa7_cap1.pdf`
```
