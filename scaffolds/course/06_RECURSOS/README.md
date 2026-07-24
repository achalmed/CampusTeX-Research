# 06_RECURSOS — Bibliografía y material de apoyo del curso

> **Responsabilidad única:** el material de **referencia del curso completo**
> (transversal, no de una unidad ni de una sesión): libros, artículos, datasets de
> apoyo, software, talleres, videos. También es el destino de los **manuales y guías**
> generados con `academic-report`.

## Subcarpetas

| Subcarpeta | Contiene |
|---|---|
| [`libros/`](libros/README.md) | libros de texto y de consulta (PDF/ePub) |
| [`articulos/`](articulos/README.md) | papers y artículos de referencia del curso |
| [`datasets/`](datasets/README.md) | bases de datos de apoyo a la enseñanza |
| [`software/`](software/README.md) | instaladores, scripts de instalación, guías de setup |
| [`talleres/`](talleres/README.md) | material de talleres y sesiones prácticas extra |
| [`videos/`](videos/README.md) | enlaces/archivos de video de referencia |

## Manuales y guías (academic-report)

```bash
./scripts/new-report.sh "$COURSE" manual "Manual de LaTeX"   # → 06_RECURSOS/manual.tex
./scripts/new-report.sh "$COURSE" guia   "Guía de Zotero"    # → 06_RECURSOS/guia.tex
```

## Qué NO va aquí

- Lecturas **de una unidad concreta** → `02_CONTENIDO/Unidad_NN/lecturas/`.
- Datasets usados para **resolver una evaluación** → `04_EVALUACIONES/.../code/data/`.
- Papers de **investigación del docente** → [`08_INVESTIGACION/`](../08_INVESTIGACION/README.md).

## Ejemplo — `_bibliografia.md`

```markdown
# Bibliografía del curso
- APA (2020). *Publication Manual* (7.ª ed.). → libros/apa7_manual.pdf
- Zotero. Guía de uso. → guia.pdf
```
