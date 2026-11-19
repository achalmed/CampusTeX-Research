---
tipo: readme
estado: activo
---
# templates/ — documentos vacíos, sin diseño

Cada plantilla es un `.tex` que solo declara `\documentclass{academic-*}` y estructura el contenido.
**No fija estilo**: el diseño vive una vez en `styles/` + `classes/`. Son lo que copian los scripts
`new-*`, nunca lo que se compila en su sitio.

## Uso

```bash
./scripts/new-evaluacion.sh   CURSO examen-desarrollo "Parcial" [--fecha AAAAMMDD]
./scripts/new-presentation.sh CURSO NN "Título" [--tipo clase]
./scripts/new-report.sh       CURSO silabo "Sílabo 2026-II"
```

## Estructura

| Carpeta | Qué es | Tipos |
|---|---|---|
| `exam/` | evaluaciones (`academic-exam`), una carpeta por tipo con su `.tex` | 12: `banco-de-preguntas`, `caso-estudio`, `control-de-lectura`, `examen-desarrollo`, `examen-objetivo`, `examen-oral`, `examen-problemas`, `laboratorio`, `practica-calificada`, `practica-dirigida`, `solucionario`, `tarea` |
| `presentation/` | diapositivas (`academic-beamer`) | 8: `clase`, `conferencia`, `defensa-tesis`, `institucional`, `masterclass`, `ponencia`, `seminario`, `workshop` |
| `report/` | documentos de gestión docente (`academic-report`) | 7: `silabo` (su sección «Uso de la inteligencia artificial» incluye `01-diseno/politica-ia.tex`, que genera `alineamiento.py generar` desde `politica_ia` del `curso.yml`), `calendario`, `nota-docente`, `rubrica`, `cornell` (hoja de apuntes, también en `.md` para la web), `ronda-de-pares` (guía y formularios), `prueba-de-comprension` (exposiciones) |

La lista de tipos de evaluación y sus siglas es normativa y vive en `docs/estandar-evaluaciones.md`;
aquí solo está su plantilla.

Las rúbricas de un curso concreto no se copian de `report/rubrica/`: se declaran en YAML en la carpeta
01-diseno/rubricas del curso (ejemplo: `contenido/cursos/econometria-i/01-diseno/rubricas/`) y su tabla la genera `scripts/alineamiento.py` (`docs/estandar-docencia.md` §10.3). Las
plantillas `cornell`, `ronda-de-pares` y `prueba-de-comprension` citan su fuente (norma FLUJO_DE_CONOCIMIENTO,
mejoras C3.5, C11.3 y C9.4).

## Límite honesto

- **Una plantilla no es un ejemplo compilado**: no se garantiza que cada una tenga un PDF de muestra.
- **Añadir un tipo de evaluación no basta con crear la carpeta**: hay que declararlo en
  `docs/estandar-evaluaciones.md` (tipo, sigla, subcarpeta) y en `scripts/new-evaluacion.sh`.
- Los registros mínimos (`curso.yml`, `sesion.yml`, `dictado.yml`) no están aquí: están en
  `scaffolds/`, que es otra cosa.
