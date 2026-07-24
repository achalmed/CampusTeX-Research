# evaluation — Examen propuesto + su solución

> La **evaluación publicable** de la sesión: el examen/práctica **propuesto** y **su
> solucionario**, ambos en PDF final. Es la autoevaluación que ofrece el MOOC.

- **Fuente:** `04_EVALUACIONES/…` de la sesión (un `.tex` genera examen **y** solución).
- **Publicar (hardlink):**
  ```bash
  ln 04_EVALUACIONES/tareas/20260502_CL.pdf \
     09_SEMESTRES/2026-I/publicacion/S05_citas/evaluation/20260502_CL.pdf
  ln 04_EVALUACIONES/tareas/20260502_CL-soluciones.pdf \
     09_SEMESTRES/2026-I/publicacion/S05_citas/evaluation/20260502_CL-soluciones.pdf
  ```
- **Regla:** publica **examen + solución juntos**. Si no quieres exponer la solución,
  omite el `-soluciones.pdf`.

## Ejemplo

```
evaluation/
├── 20260502_CL.pdf              ← examen propuesto (en blanco)
└── 20260502_CL-soluciones.pdf   ← solucionario
```
