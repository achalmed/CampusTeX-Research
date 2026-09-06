# 04_EVALUACIONES — Exámenes, prácticas, tareas y bancos

> **Responsabilidad única:** **todo lo que se califica**. Cada evaluación es un `.tex`
> de la clase `academic-exam` que, según la opción de clase, genera el **examen en
> blanco**, las **claves** o el **solucionario** desde un mismo archivo. Es la carpeta
> donde aterriza el flujo del prompt de resolución de exámenes.
>
> **Guía de resolución (léela junto a este README):**
> [`prompts/learning-skill/prompt_resolucion_examenes_plantillas.md`](../../../../git-awesome-ai-prompts/learning-skill/prompt_resolucion_examenes_plantillas.md)
> — el prompt y este estándar **van de la mano**: el prompt dice *cómo se redacta y
> resuelve* la evaluación; este README dice *dónde vive y cómo se nombra*.

---

## Organización: subcarpetas por naturaleza de la evaluación

```
04_EVALUACIONES/
├── examen_parcial/    exámenes de desarrollo, objetivos y de problemas (momento: parcial)
├── examen_final/      exámenes finales y sustentaciones orales
├── practicas/         prácticas calificadas (PC) y dirigidas (PD)
├── laboratorios/      laboratorios de software/código (R, Python, Stata)
├── tareas/            tareas domiciliarias y controles de lectura
├── proyectos/         casos de estudio y proyectos
├── banco_preguntas/   banco por tema y nivel de Bloom
├── soluciones/        solucionarios formales (con portada)
├── diagnostica/       evaluación diagnóstica de entrada (se llena a mano)
└── rubricas/          rúbricas ligadas a una evaluación (new-report.sh rubrica)
```

Cada subcarpeta tiene su propio `README.md`. La subcarpeta agrupa por **momento /
naturaleza**; la **plantilla** (abajo) define la **estructura** del documento. Un
examen final con formato de problemas usa la plantilla `examen-problemas` pero se
guarda en `examen_final/` (mueve el `.tex` si el momento no coincide con el destino
por defecto del script).

---

## Las 12 plantillas → subcarpeta y sigla (lo que hace `new-evaluacion.sh`)

| Nº | Plantilla (`templates/exam/`) | Cubre | Subcarpeta destino | Sigla (script) |
|---|---|---|---|---|
| 01 | `examen-desarrollo`   | teoría, definiciones, ensayo, respuesta corta | `examen_parcial/` | `EP` |
| 02 | `examen-objetivo`     | opción múltiple, V/F, emparejar, completar | `examen_parcial/` | `EP` |
| 03 | `examen-problemas`    | cálculo, fórmulas, demostraciones (+ formulario) | `examen_parcial/` | `EP` |
| 04 | `practica-calificada` | problemas aplicados, tablas | `practicas/` | `PC` |
| 05 | `practica-dirigida`   | ejercicio modelo + propuestos | `practicas/` | `PD` |
| 06 | `laboratorio`         | software/código, salidas de consola | `laboratorios/` | `LAB` |
| 07 | `control-de-lectura`  | lectura crítica, comentario de texto | `tareas/` | `CL` |
| 08 | `examen-oral`         | sustentaciones, defensas, rúbrica de jurado | `examen_final/` | `EO` |
| 09 | `caso-estudio`        | análisis de casos, datos, gráficos | `proyectos/` | `CASO` |
| 10 | `tarea`               | tareas domiciliarias | `tareas/` | `TAR` |
| 11 | `banco-de-preguntas`  | banco por tema y nivel de Bloom | `banco_preguntas/` | `BP` |
| 12 | `solucionario`        | solucionario formal con portada | `soluciones/` | `SOL` |

> **Ejes secundarios que NO cambian de plantilla** (solo metadatos): el **momento**
> (diagnóstico, parcial, final, sustitutorio, suficiencia) va en `\tipoevaluacion{…}`
> y en la sigla del nombre; la **forma** (individual/grupal, presencial/virtual) va en
> `\modalidad{…}`.

---

## Nomenclatura del archivo: `AAAAMMDD_SIGLA[-NN].tex`

Regla del prompt (más completa que el default del script; **manda el prompt** al
nombrar a mano):

- Empieza con la **fecha más completa que se conozca**: `AAAAMMDD` (exacta),
  `AAAAMM_SIGLA` (año-mes), `AAAA_SIGLA` (solo año), `sinfecha_SIGLA` (ninguna).
- Guion bajo + **sigla del tipo/momento**. Siglas por **momento** (del prompt):
  `EX` examen genérico · `EP` parcial · `EF` final · `ES` sustitutorio · `EA` aplazado
  · `EU` suficiencia · `ED` diagnóstico · `EV` virtual · `PC` práctica calificada ·
  `PD` dirigida · `PR` práctica genérica · `LB` laboratorio · `CL` control de lectura ·
  `TA` tarea · `OR` oral · `BP` banco.
- Si hay más de una del mismo tipo el mismo día, añade `-NN` (`-02`, `-03`).

Ejemplos: `20230127_EX.tex`, `20210612_EP-02.tex`, `2023_EA.tex`, `sinfecha_PC.tex`.

> **Nota de coherencia (script vs. prompt).** `new-evaluacion.sh` genera un nombre con
> su sigla por plantilla (p. ej. `LAB`, `TAR`, `EO`), útil como punto de partida. El
> prompt usa una taxonomía por **momento** más rica (p. ej. `LB`, `TA`, `OR`, y
> `EF/ES/EA/EU/ED/EV` para los momentos del examen). Al nombrar la versión definitiva,
> sigue el prompt y renombra/mueve si hace falta.

---

## Expediente reproducible (cuando hay datos/código)

Si la evaluación se resuelve con datos reales (econometría, estadística,
programación), deja rastro reproducible **junto al `.tex`**:

```
<subcarpeta>/
├── AAAAMMDD_SIGLA.tex / .pdf     ← enunciado + solucionario (una fuente, 3 modos)
├── enunciado*.pdf                ← original escaneado (si existe)
└── code/
    ├── AAAAMMDD_SIGLA.py         ← script que resuelve (o .R, .do); una sola orden
    ├── data/                     ← base de trabajo: SIEMPRE data.xlsx / data.csv
    ├── figures/                  ← gráficos generados (.pdf/.png) → \includegraphics
    └── table/                    ← tablas generadas (.tex, booktabs) → \input
```

- El **nombre de los datos es estándar**: `data.xlsx` (trabajo); fuentes originales
  con el mismo tallo (`data.wf1`, `data.dta`, `data.sav`, `data.ods`). El nombre que
  cita el `.tex` **debe ser exactamente** el del archivo en `code/data/`.
- **No** se crea `index.md` en los expedientes: solo enunciado, solucionario y `code/`.

---

## Flujo completo (crear → resolver → compilar)

```bash
# 1) Andamiar el .tex (elige plantilla, subcarpeta y sigla por defecto)
./scripts/new-evaluacion.sh "$COURSE" examen-problemas "Examen Final" --fecha 20260721
#    → 04_EVALUACIONES/examen_parcial/20260721_EP.tex   (muévelo a examen_final/ si aplica)

# 2) Resolver el .tex siguiendo el prompt (enunciado FIEL + {solucion} completa)

# 3) Si hay figuras/datos: generar el expediente
python 04_EVALUACIONES/.../code/20260721_EP.py

# 4) Compilar los 3 modos con LuaLaTeX (debe salir con código 0)
./scripts/build.sh "04_EVALUACIONES/examen_parcial/20260721_EP.tex" --modo todos
#    → examen · -claves · -soluciones
```

## Qué NO va aquí

- La **evaluación de salida breve** de una sesión concreta →
  `03_SESIONES/SNN/04_Evaluacion/`.
- Las **notas/calificaciones** de un dictado real →
  [`09_SEMESTRES/<periodo>/calificaciones/`](../09_SEMESTRES/README.md).
- Las **entregas de los estudiantes** → [`05_ESTUDIANTES/`](../05_ESTUDIANTES/README.md).

## Ejemplo — esqueleto de `20260721_EP.tex` (academic-exam, resumido)

```latex
\documentclass{academic-exam}          % [claves] o [soluciones] cambian el modo
\curso{Matemática para Economistas II}
\tipoevaluacion{Examen Final}          % el momento va aquí (no en el título del archivo)
\fechaevaluacion{21 de julio de 2026}
\duracion{120 minutos}
\begin{document}
\membrete
\begin{instrucciones} \begin{itemize}
  \item El procedimiento vale tanto como el resultado.
\end{itemize} \end{instrucciones}
\begin{pregunta}[5]
  Enunciado FIEL del examen (verbatim); subpreguntas en \begin{apartados}…\end{apartados}.
  \espaciorespuesta{8cm}
  \begin{solucion}
    \etapa{Datos} … \etapa{Procedimiento} \paso{Sustituimos} …
    \respuesta{…}                    % cierra SIEMPRE la solución
  \end{solucion}
\end{pregunta}
\findelexamen
\end{document}
```
