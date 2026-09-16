---
tipo: doc
titulo: 'Estándar de evaluaciones: tipos, siglas, carpetas, expediente, código y migración'
estado: activo
---
# 10 — Estándar de evaluaciones (`04-evaluaciones/`)

Consolida en un solo lugar lo que ya estaba acordado en tres sitios —el prompt maestro
`prompts/05 docencia/prompt_resolucion_examenes_plantillas.md` (2026-07-23), el estándar de
docencia `docs/09-estandar-docencia.md` §2 y el script `scripts/new-evaluacion.sh`— y fija las
decisiones que faltaban (2026-09-15, R10/R11). Donde el prompt y la normativa de archivos
(`meta/NORMATIVA_ARCHIVOS.md`, 2026-09-13) discrepaban, manda la normativa y el prompt se
actualizó. **Este documento es la fuente; el prompt maestro remite aquí.**

## 1. Qué es una evaluación en el framework

Un **examen es un `.tex` de la clase `academic-exam`**, no un PDF, un `.docx` ni una foto. El
mismo `.tex` produce el examen en blanco, la hoja de claves y el solucionario
(`scripts/build.sh ARCHIVO.tex --modo examen|claves|soluciones|todos`). Un PDF o documento
ofimático es solo una **fuente**: existe mientras no se haya transformado y se elimina al validar
la transformación. **Migrar = transformar**, nunca mover:

> identificar → clasificar → transformar al `.tex` → crear/convertir solucionario y auxiliares →
> aplicar nomenclatura y estructura → compilar y validar → verificar → eliminar el original.

## 2. Tipos de evaluación, siglas, plantillas y subcarpetas

| Tipo | Sigla | Plantilla (`templates/exam/`) | Subcarpeta |
|---|---|---|---|
| Examen (genérico) | `ex` | 01/02/03 según el contenido | `examen_parcial` |
| Examen parcial | `ep` | 01 desarrollo · 02 objetivo · 03 problemas | `examen_parcial` |
| Examen virtual / test | `ev` | 02 objetivo | `examen_parcial` |
| Examen diagnóstico · de suficiencia | `ed` · `eu` | 01/02/03 | `examen_parcial` |
| Examen final | `ef` | 01/02/03 | `examen_final` |
| Examen sustitutorio | `es` | 01/02/03 | `examen_final` |
| Examen de aplazados | `ea` | 01/02/03 | `examen_final` |
| Examen oral / sustentación | `or` | 08 examen-oral | `examen_final` |
| Práctica calificada | `pc` | 04 practica-calificada | `practicas` |
| Práctica dirigida | `pd` | 05 practica-dirigida | `practicas` |
| Práctica (genérica) · ejercicios | `pr` | 04/05 | `practicas` |
| Laboratorio | `lb` | 06 laboratorio | `laboratorios` |
| Control de lectura | `cl` | 07 control-de-lectura | `tareas` |
| Tarea | `ta` | 10 tarea | `tareas` |
| Caso de estudio | `caso` | 09 caso-estudio | `proyectos` |
| Banco de preguntas | `bp` | 11 banco-de-preguntas | `banco` |
| Solucionario formal con portada | `sol` | 12 solucionario | `soluciones` |

- La **sigla va en minúsculas** (normativa §4; así la escribe `new-evaluacion.sh` desde M7).
  El prompt maestro decía mayúsculas: queda corregido.
- El **momento** (parcial, final, sustitutorio, aplazados…) va en `\tipoevaluacion{}` y en la
  sigla; la **forma** (individual/grupal, presencial/virtual) en `\modalidad{}`.
- `banco/` **no es destino final**: guarda bancos de preguntas (`bp`) y, transitoriamente, los
  PDF sueltos aún no transformados. Al transformarse, cada uno pasa a su subcarpeta de tipo.

## 3. Nombre del examen: `AAAAMMDD_sig[_nn]`

Fecha más completa conocida (`AAAAMMDD` · `AAAAMM` · `AAAA` · `sinfecha`) + `_` + sigla; si hay
dos del mismo tipo el mismo día, `_02`, `_03`. Corto, sin curso (la carpeta ya lo dice).
Ejemplos: `20230127_ex`, `20210612_ep_02`, `2023_ea`, `sinfecha_pc`, `2012_ev_03`.
El nombre del expediente, del `.tex`, del script y de los PDF es **el mismo tallo**.

## 4. El expediente: una carpeta por evaluación

```
04-evaluaciones/<subcarpeta>/AAAAMMDD_sig/
├── AAAAMMDD_sig.tex               ← LA fuente (academic-exam): enunciado fiel + solución modelo
├── AAAAMMDD_sig.pdf               ← examen en blanco   (build.sh --modo examen)
├── AAAAMMDD_sig-soluciones.pdf    ← solucionario       (build.sh --modo soluciones)
└── code/                          ← solo si hay datos, cálculos, figuras o tablas
    ├── AAAAMMDD_sig.py            ← reproduce TODOS los números del solucionario con una orden
    ├── data/                      ← data.xlsx (trabajo) + fuentes con el mismo tallo: data.wf1, data.dta, data.sav, data.ods
    │                                 varias bases: data-1.xlsx, data-2.xlsx o data-<desc>.xlsx
    ├── figures/                   ← gráficos que genera el código (.pdf/.png) → \includegraphics{code/figures/…}
    └── table/                     ← tablas .tex que genera el código → \input{code/table/…}
```

- **Solo los archivos involucrados.** Ni `index.md`, ni `datos/ codigo/ resultados/ anexos/`, ni
  `enunciado*.pdf`, ni respuestas manuscritas, ni `.smcl/.log/.spv` de otro software: lo que
  aporte se incorpora al `.tex`/`code/`; lo demás se elimina al validar (decisión del autor,
  2026-09-15; sustituye al «`enunciado*.pdf ← original`» del prompt de julio).
- El `.tex` **cita los archivos por su nombre real** (`\texttt{data.xlsx}`), no por el nombre
  que usaba el escaneo (`Importaciones_Examen`, `Data_Examen`…).
- `code/` se llama `code` (no `codigo`); el script lleva el tallo del examen; las carpetas
  `figures/` y `table/` existen solo si el código las produce; nada de gráficos a mano
  (TikZ) para lo que el examen manda calcular.
- Datos pesados (> 5 MB) no viven aquí: el catálogo de `02 analysis` los aloja y `curso.yml`
  los cita en `datasets[]` (§7.6 del estándar de docencia); en `code/data/` queda la muestra.
- Lecturas y anexos de terceros (artículos, capítulos) van a la biblioteca Calibre
  (`bibliografia[]` del `curso.yml`), no al expediente.

## 5. Contenido del `.tex` (resumen del prompt maestro, que sigue siendo la guía de redacción)

Cabecera de identidad en la línea 1 (`%% cursos/<slug>/04-evaluaciones/<sub>/<tallo>/<tallo>.tex — <Tipo>: <Curso> (<periodo>)`),
metadatos (`\universidad`, `\facultad`, `\escuela`, `\curso`, `\codigocurso`, `\docente`,
`\periodo`, `\tipoevaluacion`, `\subtitulo` = solo el tema, `\fechaevaluacion`, `\modalidad`),
`\membrete`, `{instrucciones}`, `{datos}` si hay archivo de datos, y por pregunta:
`\begin{pregunta}[puntos]` · `\ficha{nivel=…, tiempo=…}` · enunciado **fiel** · `{apartados}` con
`\pts{}` · `{solucion}` con `\etapa{}` por disciplina (econometría: Modelo y variables ·
Hipótesis y supuestos · Método · Estimación · Resultados · Pruebas · Bondad de ajuste ·
Interpretación · Implicaciones), `\paso{}` en primera persona del plural, `{ecua}` para una
igualdad por línea, `{ecuac}` para varias, `\aplica{}` para la fórmula usada, `\interpreta{}`
para la lectura breve (antes `\nota{}`), `\respuesta{}` para el resultado. Sin rastro de
corrección: la solución es la versión oficial correcta. Valores por defecto: UNSCH, Facultad y
Escuela de Economía, estudiante titular y su código (los pone la clase); lo que no se sabe se deja
vacío, no se inventa. Símbolos: unicode-math (`\mdlgblksquare`, no `\blacksquare`).

## 6. Compilar, validar, cerrar

1. Si hay `code/`: `python3 code/<tallo>.py` corre con una orden y deja `figures/` y `table/`.
2. `scripts/build.sh <tallo>.tex --modo todos` con **código 0**; se conservan `<tallo>.pdf` y
   `<tallo>-soluciones.pdf` (la hoja de claves se regenera cuando haga falta).
3. Revisar el PDF: título en tres líneas, datos del membrete, matemática, figuras, puntajes.
4. `build.sh <tallo>.tex --clean` (los auxiliares nunca se versionan; **ojo**: `.log` también es la
   extensión de las bitácoras de Stata: el `--clean` del script solo borra `<tallo>*.log`).
5. Registrar el estado en `docencia/migracion/estado-examenes.csv` y **eliminar las fuentes**
   del expediente. `validate.sh CURSO` debe seguir limpio (sin carpetas vacías).
6. `python3 scripts/enlazar.py examenes --aplicar` y `temario-generar.sh generar --aplicar --que readme`
   cuando cambie el conteo de una subcarpeta.

## 7. Registro de la migración (`docencia/migracion/estado-examenes.csv`)

Una fila por expediente o PDF suelto: `curso; sub; expediente; estado; …`. Estados:
`transformado` (solo `.tex` + PDF propios + `code/`), `parcial` (`.tex` hecho, quedan fuentes),
`pendiente` (fuente sin transformar), `manual` (no transformable automáticamente: sin enunciado,
escaneo ilegible, datos en formato sin lector…, con el motivo en `detalle`). Nada se da por
migrado por estar dentro de `04-evaluaciones/`. El migrador `migrar-examenes.py` (R10) solo
reorganizó y convirtió los `.tex` que ya existían; la transformación es trabajo por expediente
según este estándar y el prompt maestro.

## 8. Datos en formatos propietarios

`.wf1` (EViews) se convierte con `gretlcli` (`open x.wf1` → `store data.csv`), y de ahí a
`data.xlsx`; `.dta`/`.sav` los lee `pandas` directo; `.ods/.xls/.xlsx` con LibreOffice
headless o `pandas`. La fuente original se conserva en `code/data/` con el tallo estándar
(`data.wf1`) solo si el `.py` la necesita para reproducir; si no, basta `data.xlsx`.
