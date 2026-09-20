# CLAUDE.md — simuladores (el laboratorio computacional)

Laboratorio pedagógico multi-disciplina de `10 Class` (repo `Academic_Class_Framework`).
Vivió en `02 analysis/simuladores/` hasta el 2026-09-20 (D02: `02 analysis/docs/ARQUITECTURA.md`
§6); se trasladó con su historia git porque es **currículo** —fichas pedagógicas, verificaciones
que son teoremas, animaciones— y lo consumen los cursos (`docencia/cursos/*/curso.yml`,
recursos `{tipo: simulador}` enlazados por `scripts/enlazar.py simuladores`), no el pipeline de
datos. Leer `README.md` de esta carpeta para el uso; lo que sigue es la doctrina.

## Estructura: un laboratorio, varias disciplinas hermanas

El MOTOR compartido (agnóstico a la disciplina) vive en la RAÍZ: `base.py` (dataclasses,
cálculo, verificación; SIN matplotlib), `graficos.py` (render matplotlib: colocación
automática de etiquetas anti-solape, dibujo progresivo), `laboratorio.py` (láminas de
experimento), `app.py` (LA aplicación: `python3 main.py` sin argumentos abre el recorrido
pedagógico progresivo; los subcomandos CLI son herramientas técnicas) y `reporte.py` (MD).
Cada disciplina es una subcarpeta con su propio `config.py`/`main.py`/`modelos/`: `macro/`
(completa), `estadistica/` (en curso), y futuras `econometria/`/`micro/`/`mate/`. El `main.py`
de cada disciplina añade la raíz al `sys.path` (motor) y su carpeta primero (su `config` y
`modelos` ganan): así se comparte el motor sin copiarlo. Correr: `cd <disciplina> && python3
main.py …`. Los `docs/`, `salidas/` (regenerables, no se versionan) y la
`matriz_trazabilidad.csv` de cada disciplina viven en su subcarpeta. Código común de un nivel
va en `modelos/nivel_NN/_*.py` (el guion bajo lo excluye del descubrimiento).

## Reglas de un modelo

Un modelo = un archivo `modelos/nivel_NN/<id>_slug.py` con `Ficha` pedagógica completa
(contexto histórico, autores, supuestos, ecuaciones explicadas, intuición, limitaciones,
evolución; derivación LaTeX en estadística), `escenarios` con lectura y `verificaciones`
numéricas (identidades exactas, convergencias con tolerancia; en estadística, los TEOREMAS:
$E[\bar X]=\mu$, TCL…). Plantilla académica de 20 puntos en §2 del diseño de macro: modelos
nuevos traen `pregunta`, `cadena` de transmisión por escenario y, cuando aplique,
`derivacion`/`variables`/`ecuaciones_calibradas`/`grupo`. Reglas duras: procedencia declarada
(sin citas de página no verificadas; regla 00a de datafw); calibraciones didácticas ≠ datos
oficiales; `python3 main.py verificar` al 100 % y fila en la `matriz_trazabilidad.csv` de su
disciplina antes de dar un modelo por bueno; aleatoriedad con `np.random.default_rng(semilla)`.
Figuras con tipografía académica (mathtext STIX, notación `$…$` en ejes y leyendas; opción
`USAR_TEX_COMPLETO` en config). Cada concepto se DERIVA, SIMULA y VISUALIZA: no es una
fórmula (regresión = derivar $\hat\beta=(X'X)^{-1}X'Y$, no llamar `lm()`).

## Macroeconomía (`macro/`, 2026-08-19)

Currículo COMPLETO: 115 modelos en 12 niveles, 569 verificaciones; plan vigente en
`macro/docs/LABORATORIO_MACRO.md`. El nivel 12 es el laboratorio del Perú con datos reales del
BCRP: m97-m115 usan series macro (PBI, IPC, tasa, tipo de cambio, cobre, términos de
intercambio, bloque fiscal) que descarga `02 analysis/connectors/bcrp`; el detalle mensual se
lee de `02 analysis/data/raw/peru/bcrp/` **por nombre** (`nivel_12/_datos_bcrp.py` localiza
`core/env.py: ANALYSIS_DIR`) y, si no está, cae al snapshot anual embebido en `_series_bcrp.py`
(auto-contenido). Verifica contra el dato real, no contra calibración didáctica: coef. Taylor
0,55 < 1 = sesgo de variable omitida (m100); correlación tasa-inflación = causalidad inversa
(m101); canal del cobre (m103-m105: TdI mueven el INGRESO, no el PBI-volumen); inversión
pública corr ≈ 0 porque es contracíclica (m106-m108) vs exportaciones exógenas (m109); shock
externo real y financiero (m110-m111); enclave minero (m112); passthrough ≈ 0 (m113); El Niño
como shock de oferta (m114); síntesis (m115). Tras macro vendrán micro/econometría/mate (§9 del
diseño); la econometría pedagógica NO duplicará `02 analysis/pipeline/`.

## Estadística (`estadistica/`, 2026-08-20)

Currículo de Edison: 239 temas en 20 secciones (I fundamentos → XX ML); diseño en
`estadistica/docs/LABORATORIO_ESTADISTICA.md`. Estado 2026-09-05: 23 modelos (niveles 1-3),
115 verificaciones en verde; la app interactiva es la del motor (`app.py`) y ya sirve a esta
disciplina. DOS renderizadores, un modelo: matplotlib (app + reportes) y **Manim**
(`estadistica/animaciones/`, «ver el método en movimiento»), que corre en un env conda APARTE
(`manim-datafw`, Manim 0.20.1 sobre ffmpeg + TeX Live) porque `manimpango` no tiene wheel para
py3.13; utilidades comunes en `_comun.py` (prohibido copiarlas). Siguiente: sección III.

## Relación con el resto del ecosistema

- Datos reales: siempre de `02 analysis` por nombre (`core/env.py`), nunca por rutas relativas
  ni copias; el laboratorio no adquiere datos.
- Cursos: `docencia/cursos/<slug>/curso.yml` enlaza modelos como `recursos: [{tipo: simulador,
  archivo: 10 Class/simuladores/<disciplina>/modelos/…}]`; `scripts/enlazar.py simuladores`
  propone los enlaces por similitud de título y `enlazar.py verificar` los comprueba.
- Forma de archivos: normativa `meta/NORMATIVA_ARCHIVOS.md` (`core/archivos.py validar "10 Class"`).
