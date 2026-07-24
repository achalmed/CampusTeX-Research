# period/ — Un dictado del curso (`09_SEMESTRES/<AAAA-ciclo>/`)

> **Esqueleto de un dictado.** Se copia con `new-period.sh` a
> `course_NN/09_SEMESTRES/<AAAA-ciclo>/` y guarda **todo lo de una promoción concreta**:
> su **registro privado** (estudiantes, notas, cronograma, evaluaciones aplicadas,
> evidencias) **y su publicación** (el MOOC por sesión, que se congela poco a poco).
>
> Contrapunto: las carpetas **00–08** del curso son el material **canónico y
> atemporal**; esto es la **ejecución real** de un semestre.

## Estructura del dictado

| Carpeta | Rol | Contiene |
|---|---|---|
| [`estudiantes/`](estudiantes/README.md) | privado | lista/matrícula de la promoción |
| [`calificaciones/`](calificaciones/README.md) | privado | notas y registro de evaluación |
| [`cronograma/`](cronograma/README.md) | privado | el calendario **real** de este dictado |
| [`evaluaciones_aplicadas/`](evaluaciones_aplicadas/README.md) | privado | los exámenes tal como se tomaron |
| [`evidencias/`](evidencias/README.md) | privado | trabajo real ([`entregas/`](evidencias/entregas/README.md), [`exposiciones/`](evidencias/exposiciones/README.md), [`proyectos/`](evidencias/proyectos/README.md)) |
| [`publicacion/`](publicacion/README.md) | **público** | el **MOOC** de este dictado, por sesión, congelado al publicar |

## Publicar = congelar (poco a poco)

La publicación **no** espera al final del semestre: cada vez que terminas y publicas una
sesión, su módulo en `publicacion/S<NN>_<slug>/` queda **congelado**. El dictado se
llena y se solidifica **sesión a sesión**.

## Nomenclatura

- Carpeta del periodo: **`AAAA-ciclo`** (`2026-I`). `new-period.sh` no sustituye
  placeholders: nombra los archivos internos a mano.

## ⚠ Datos personales · reversibilidad por git

El registro privado contiene datos reales de estudiantes. No publicar; anonimizar si se
comparte. El árbol `Academic_Class-*` es un **repositorio git** (se inicializa si falta):
la reversibilidad de cualquier reorganización es por git, no por copias de respaldo.

## Crear un dictado

```bash
./scripts/new-period.sh "$COURSE" 2026-II       # → 09_SEMESTRES/2026-II/
```

## Ejemplo — un periodo real

```
09_SEMESTRES/2026-I/
├── estudiantes/lista.csv · calificaciones/notas.xlsx · cronograma/…
├── evaluaciones_aplicadas/20260521_EP.pdf
├── evidencias/entregas/ · exposiciones/ · proyectos/
└── publicacion/index.md · S01_introduccion/ · S02_estructura/   (congelado por sesión)
```
