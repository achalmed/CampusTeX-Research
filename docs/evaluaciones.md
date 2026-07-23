# Sistema de evaluaciones

El framework administra dos productos LaTeX por curso: **diapositivas** de clase
(Beamer, en `03_SESIONES/SNN/02_Clase/`) y **evaluaciones** (exámenes/prácticas,
en `04_EVALUACIONES/`). Este documento cubre el segundo. Referencia completa de
comandos y plantillas: [`evaluaciones/README.md`](../evaluaciones/README.md).

## Arquitectura

Igual que en el `Academic_Writing_Framework`, **todo el diseño vive en una sola
clase** y los documentos solo seleccionan y rellenan:

```
evaluaciones/
├── evaluacion.cls     ← la clase: identidad visual, entornos, puntaje automático
├── plantillas/        ← 12 puntos de partida (uno por tipo de evaluación)
├── muestras/          ← PDF de ejemplo de cada plantilla
└── README.md          ← especificación y referencia de comandos
```

- **Motor:** pdfLaTeX (2 pasadas por los totales vía `.aux`). Es independiente
  del motor de las diapositivas (Beamer/Quarto).
- **Localización de la clase:** `build-evaluacion.sh` exporta
  `TEXINPUTS="$FW/evaluaciones:"`, así el `.tex` de un curso encuentra
  `evaluacion.cls` sin copiarla.
- **Un archivo, tres salidas:** el mismo `.tex` produce examen, hoja de claves y
  solucionario según la opción de clase (`\PassOptionsToClass`, aplicada por
  `--modo` sin editar el archivo).

## Dónde viven las evaluaciones: `04_EVALUACIONES/`

Cada evaluación se crea dentro de la carpeta `04_EVALUACIONES/` del curso, en la
subcarpeta que le corresponde. `new-evaluacion.sh` hace el mapeo automático:

| Tipo de plantilla | Subcarpeta | Sigla (nombre `AAAAMMDD_SIGLA.tex`) |
|---|---|---|
| examen-desarrollo / objetivo / problemas | `examen_parcial` | EP |
| practica-calificada / practica-dirigida | `practicas` | PC / PD |
| laboratorio | `laboratorios` | LAB |
| control-de-lectura / tarea | `tareas` | CL / TAR |
| examen-oral | `examen_final` | EO |
| caso-estudio | `proyectos` | CASO |
| banco-de-preguntas | `banco_preguntas` | BP |
| solucionario | `soluciones` | SOL |

Aquí es donde se irán **migrando los exámenes reales** de cada curso (fase
posterior). Por ahora quedan la clase, las plantillas y el tooling listos.

## Comandos

```bash
FW=~/Documents/Academic_Class_Framework
C=~/Documents/Academic_Class-<Area>/course_NN_<slug>

./scripts/new-evaluacion.sh  "$C" <tipo|01-12> "Título de la evaluación" [--fecha AAAAMMDD]
./scripts/build-evaluacion.sh "$C/04_EVALUACIONES/.../AAAAMMDD_SIG.tex" --modo examen|claves|soluciones|todos
./scripts/build-evaluacion.sh "…tex" --clean       # borra auxiliares
```

## Mantenimiento

- Los cambios de diseño se hacen **solo** en `evaluaciones/evaluacion.cls`.
- Las muestras se regeneran compilando las plantillas; no editar los PDF a mano.
- Requiere TeX Live con `tcolorbox`, `tasks`, `libertinus-type1`, `fontawesome5`
  (el `.claude/settings.local.json` del framework autoriza los `kpsewhich`).
