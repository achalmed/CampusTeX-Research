# evaluaciones — sistema LaTeX de evaluaciones académicas

Módulo del **Academic_Class_Framework** para generar exámenes, prácticas y
evaluaciones con calidad editorial uniforme. Es el equivalente, para
**evaluaciones**, de lo que las diapositivas Beamer son para las **clases**:
el framework administra ambos a nivel profesional.

Todo el diseño vive en **una sola clase** (`evaluacion.cls`); las 12 plantillas
son puntos de partida ya maquetados para cada tipo de documento. Cualquier
ajuste tipográfico se hace una vez en la clase y se propaga a todo.

> **Dónde viven las evaluaciones de cada curso:** en la carpeta **`04_EVALUACIONES/`**
> del curso (`<Academic_Class>/course_NN/04_EVALUACIONES/<subcarpeta>/`). Ahí es
> donde se crean con `new-evaluacion.sh` y se irán migrando los exámenes reales.

**Identidad visual:** tipografía Libertinus (texto y matemática) + Inconsolata
(código), paleta sobria casi monocroma («tinta pizarra») que imprime idéntico en
blanco y negro, membrete institucional de doble filete, folios con curso y tipo
de evaluación, y cajas informativas consistentes.

## Flujo con el framework

```bash
FW=~/Documents/Academic_Class_Framework
C=~/Documents/Academic_Class-<Area>/course_NN_<slug>

# 1. Crear una evaluación en 04_EVALUACIONES/ (rellena metadatos desde config)
$FW/scripts/new-evaluacion.sh "$C" examen-desarrollo "Examen Parcial 01"
#   → $C/04_EVALUACIONES/examen_parcial/AAAAMMDD_EP.tex

# 2. Editar las preguntas y compilar los tres PDF de una vez
$FW/scripts/build-evaluacion.sh "$C/04_EVALUACIONES/examen_parcial/AAAAMMDD_EP.tex" --modo todos
#   → examen (estudiante) · -claves.pdf · -soluciones.pdf
```

`new-evaluacion.sh` mapea cada tipo a su subcarpeta de `04_EVALUACIONES/` y a una
sigla para el nombre `AAAAMMDD_SIGLA.tex`. `build-evaluacion.sh` localiza
`evaluacion.cls` vía `TEXINPUTS` (no se copia la clase) y compila dos veces (los
totales de puntos y páginas se calculan por el `.aux`).

## Un archivo, tres documentos

El mismo `.tex` genera el examen, la hoja de claves y el solucionario cambiando
solo la opción de clase (que `build-evaluacion.sh --modo` aplica sin editar el archivo):

| Opción / `--modo` | Efecto |
|---|---|
| *(ninguna)* / `examen` | Examen para el estudiante: oculta soluciones y claves; muestra líneas/espacios de respuesta. |
| `claves` | Muestra solo claves objetivas: `\correcta`, `\clave`, `\vf`, `\pareja`, `\completar`. |
| `soluciones` | Solucionario completo: muestra `{solucion}` y claves, **suprime** líneas y espacios de respuesta. |
| `compacto` | Márgenes y espaciados reducidos (ahorro de papel). |

```latex
\documentclass{evaluacion}             % examen
\documentclass[claves]{evaluacion}     % hoja de claves
\documentclass[soluciones]{evaluacion} % solucionario
```

## Las 12 plantillas y la taxonomía que cubren

| Plantilla | Cubre | Subcarpeta 04_EVALUACIONES · sigla |
|---|---|---|
| `01-examen-desarrollo` | Teóricos: definiciones, comparaciones, respuesta corta, ensayo. | `examen_parcial` · EP |
| `02-examen-objetivo` | Opción múltiple, V/F, emparejamiento, completar, ordenamiento. | `examen_parcial` · EP |
| `03-examen-problemas` | Cálculo, fórmulas, demostraciones, optimización; incluye formulario. | `examen_parcial` · EP |
| `04-practica-calificada` | Prácticas calificadas con problemas aplicados y tablas. | `practicas` · PC |
| `05-practica-dirigida` | Sesiones guiadas: ejercicio modelo (`{desarrollo}`) + propuestos. | `practicas` · PD |
| `06-laboratorio` | Software: código R·Stata·Python, salidas de consola, simulación. | `laboratorios` · LAB |
| `07-control-de-lectura` | Lectura crítica, comentario de texto, ensayo con rúbrica. | `tareas` · CL |
| `08-examen-oral` | Sustentaciones: protocolo, preguntas del jurado, rúbrica, firmas. | `examen_final` · EO |
| `09-caso-estudio` | Análisis de casos, datos, gráficos (pgfplots) y tablas. | `proyectos` · CASO |
| `10-tarea` | Tareas domiciliarias con condiciones de entrega y criterios. | `tareas` · TAR |
| `11-banco-de-preguntas` | Banco por tema y nivel de Bloom, con claves. | `banco_preguntas` · BP |
| `12-solucionario` | Convertir un examen del archivo en solucionario formal con portada. | `soluciones` · SOL |

Ejes que no necesitan plantilla propia: **el momento** (diagnóstico, parcial,
final, sustitutorio…) es texto en `\tipoevaluacion{...}`; **la forma**
(individual/grupal, presencial/virtual…) se declara en `\modalidad{...}`.

## Metadatos (preámbulo)

```latex
\universidad{...} \facultad{...} \escuela{...}
\curso{...} \codigocurso{...} \docente{...} \periodo{...}
\tipoevaluacion{Examen Parcial 02}    % SOLO el tipo; nunca «Solucionario · …»
\fechaevaluacion{...} \duracion{...}
\modalidad{Presencial · individual}
\estudiante{Achalma Mendoza, Elmer Edison}   % por defecto el titular
\codigoestudiante{...} \seccion{...}          % opcionales; vacíos → línea en blanco
% opcionales
\subtitulo{...}  \autorevaluacion{Edison Achalma}  \logoinstitucional{ruta/logo.pdf}
```

En modo `[soluciones]` la clase añade sola el rótulo **«(Solucionario)»** bajo el
título; no lo escribas en `\tipoevaluacion`. (`new-evaluacion.sh` rellena
`\curso`, `\docente`, `\universidad`, `\periodo`, `\tipoevaluacion` y
`\fechaevaluacion` desde `config/course.yml` y el curso.)

## Referencia rápida de la clase

**Estructura:** `\membrete` (encabezado compacto de 1.ª página) · `\portada[descriptor]`
(carátula completa del solucionario) · `\findelexamen`. El título lleva
«— Solucionario» automático en modo `[soluciones]`.

**Preguntas:** `\begin{pregunta}[puntos][tema] ... \end{pregunta}` (o `{ejercicio}`).
Los puntos (admiten decimales `2.5`) alimentan `\totalpuntos` / `\totalpreguntas`.
Dentro: `{apartados}` para a), b), c) con `\pts{2}` por ítem. La `{solucion}` se
compone en bloque diferenciado (fondo gris, filete azul, rótulo burdeos).

**Objetivas:**

```latex
\begin{opciones}(2)                  % nº de columnas
  \opcion texto  \opcion \correcta{texto correcto}
\end{opciones}
\clave{b}
\begin{tablavf} \vf[V]{Enunciado...} \vf[F]{Otro...} \end{tablavf}
\begin{emparejamiento} \pareja[c]{Concepto}{Definición} ... \end{emparejamiento}
La demanda es \completar[elástica]{3cm} ...
```

**Espacios de respuesta** (desaparecen en modo `soluciones`):
`\lineasrespuesta{8}` · `\espaciorespuesta{6cm}` · `\recuadrorespuesta{5cm}`.

**Soluciones:** `\begin{solucion}...\end{solucion}` (visible solo con `soluciones`).
`{desarrollo}` es la variante siempre visible (prácticas dirigidas).

**Cajas:** `{instrucciones}` · `{observacion}` · `{datos}` · `{formulario}` ·
`{criterios}` (título opcional entre corchetes) · `{definicion}[nombre]` y
`{teorema}[nombre]` (numerados).

**Código:** `\begin{codigo}[language=R] ... \end{codigo}` (R, Python, Stata
resaltados; funciona dentro de `{solucion}`) y `{salida}` para salidas de consola.

## Compilación manual (sin el script)

```bash
export TEXINPUTS="$HOME/Documents/Academic_Class_Framework/evaluaciones:"
latexmk -pdf 04_EVALUACIONES/examen_parcial/AAAAMMDD_EP.tex   # 2 pasadas
```

Requiere TeX Live con `tcolorbox`, `tasks`, `libertinus-type1` y `fontawesome5`.
Los PDF de ejemplo de las 12 plantillas están en `muestras/`.

## Mantenimiento

- Los cambios de diseño se hacen **solo** en `evaluacion.cls`.
- Colores: `colorprimario`, `colorsecundario`, `colorenfasis`, `colorexito`,
  `colornota` (sección «paleta» de la clase).
- No edite los PDF de `muestras/`: se regeneran compilando las plantillas.
