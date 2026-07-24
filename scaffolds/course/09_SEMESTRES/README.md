# 09_SEMESTRES — Los dictados del curso (registro privado + publicación)

> **Responsabilidad única:** cada vez que se **dicta** el curso vive aquí, en un
> `<AAAA-ciclo>/` (un "semestre"). Esta carpeta **fusiona** lo que antes estaba
> disperso en tres (`09_PUBLICACION` + `10_ARCHIVO` + `11_SEMESTRES`): cada dictado
> guarda **junto** su **registro privado** (estudiantes, notas, cronograma,
> evaluaciones aplicadas, evidencias) **y su publicación** (el MOOC por sesión).
>
> **El dictado se congela poco a poco:** cada sesión que publicas queda **congelada**
> en el acto, sin esperar al final del semestre. Un semestre terminado es,
> simplemente, un dictado con **todo** congelado — no hace falta "archivarlo" aparte.

## Organización: un dictado por periodo

```
09_SEMESTRES/
├── README.md
├── 2026-I/            ← un dictado (registro privado + publicacion, se congela por sesión)
├── 2026-II/
└── 2025-II/           ← dictado pasado (todo congelado)
```

Cada `<AAAA-ciclo>/` tiene la estructura del esqueleto
[`scaffolds/period/`](../../period/README.md):

```
2026-I/
├── README.md
├── estudiantes/            ┐
├── calificaciones/         │  registro PRIVADO del dictado
├── cronograma/             │  (datos de la promoción; no publicar)
├── evaluaciones_aplicadas/ │
├── evidencias/             ┘  entregas/ · exposiciones/ · proyectos/
└── publicacion/            ← el MOOC de este dictado (se congela por sesión)
    ├── index.md            ·  landing del MOOC del dictado
    ├── S01_intro/          ·  módulo: slides/ evaluation/ practice/ homework/
    └── S02_…/
```

## Nomenclatura

- **`AAAA-ciclo`** con guion: `2026-I`, `2026-II`. Ordena cronológicamente.
- `new-period.sh` no sustituye placeholders: nombra los archivos internos a mano.

## Congelación gradual (publicar = congelar)

El flujo por sesión es: terminas la sesión → **publicas** su módulo en
`<periodo>/publicacion/S<NN>_<slug>/` → ese módulo queda **congelado** (no se vuelve a
tocar). Así el semestre se llena y se congela **sesión a sesión**. Detalle en
[`scaffolds/period/publicacion/`](../../period/publicacion/README.md).

## Crear un dictado

```bash
./scripts/new-period.sh "$COURSE" 2026-II     # → 09_SEMESTRES/2026-II/  (registro + publicacion)
```

## ⚠ Datos personales

El registro privado contiene datos de estudiantes reales (nombres, notas, evidencias).
No publicar; anonimizar si se comparte. La **reversibilidad es por git** (este árbol es
un repositorio; se inicializa si falta).

## Ejemplo — un dictado real

```
09_SEMESTRES/2026-I/
├── estudiantes/lista.csv
├── calificaciones/notas.xlsx
├── cronograma/cronograma_2026-I.md
├── evaluaciones_aplicadas/20260521_EP.pdf
├── evidencias/entregas/ · exposiciones/ · proyectos/
└── publicacion/
    ├── index.md
    ├── S01_introduccion/ slides/ evaluation/ practice/ homework/   (congelado)
    └── S02_estructura/   …                                          (congelado)
```
