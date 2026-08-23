# Laboratorio histórico y computacional de Estadística (`estadistica/`)

Segunda disciplina del laboratorio (tras el currículo macro de 115 modelos; §9
del diseño macro). Diseño y currículo pedidos por Edison (2026-08-20).

**Visión:** cada concepto estadístico **no es una fórmula que se memoriza, sino
un método que se DERIVA, se SIMULA y se VISUALIZA** — para ver *qué está haciendo
matemáticamente*. La regresión no es `lm(y ~ x)`: es derivar
$\hat\beta=(X'X)^{-1}X'Y$ desde $\min_\beta (Y-X\beta)'(Y-X\beta)$, simular el
estimador, ver su distribución, y recién entonces aplicarlo a datos reales.

El recorrido reconstruye la evolución de la disciplina:

```
DATOS → DESCRIPTIVA → PROBABILIDAD → DISTRIBUCIONES → MUESTREO → TCL →
INFERENCIA → ESTIMACIÓN → PRUEBAS → CORRELACIÓN → REGRESIÓN → MÁXIMA
VEROSIMILITUD → BAYES → BOOTSTRAP/MONTE CARLO → MULTIVARIANTE → SERIES →
ESPACIAL → CAUSAL → MACHINE LEARNING
```

## 1. Arquitectura: un laboratorio, muchas disciplinas, un motor

`simuladores/` es **el laboratorio** (paraguas). El MOTOR compartido vive en su
raíz; cada disciplina (macro, estadística, y futuras econometría/micro/mate) es
una **subcarpeta hermana** con su propio `config`/`main`/`app`/`modelos`
(patrón config-por-proyecto / lib-compartida; prohibido copiar el motor):

```
simuladores/                 ← EL laboratorio (paraguas)
├── base.py                  ┐  MOTOR compartido (agnóstico a la disciplina):
├── graficos.py              │  dataclasses, cálculo, verificación (base) +
├── reporte.py               │  render matplotlib (graficos) + informe (reporte)
├── laboratorio.py           ┘  + láminas de experimento (laboratorio)
├── macro/                   ← disciplina: macroeconomía (115 modelos, completa)
│   ├── config.py main.py app.py
│   └── modelos/nivel_01..12/
├── estadistica/             ← disciplina: estadística (esta)
│   ├── config.py main.py app.py     (scaffolding pendiente)
│   ├── modelos/
│   │   ├── nivel_01/  sección I  (fundamentos)
│   │   └── nivel_20/  sección XX (ML)      eNN_slug.py = un tema
│   ├── animaciones/  capa Manim (ver animaciones/README.md)
│   ├── demos/        demos interactivos (matplotlib)
│   ├── docs/         este diseño
│   └── salidas/      reportes/figuras/videos (regenerable, en .gitignore)
└── (econometria/  micro/  mate/  … futuras disciplinas hermanas)
```

Cada disciplina reusa el motor de la raíz: su `main.py` añade la raíz al
`sys.path` (para `base`/`graficos`/`reporte`) y su propia carpeta primero (su
`config`/`modelos` ganan). Así `import config` resuelve al de la disciplina y
`from base import` al motor común — sin duplicar el motor.

**Dos renderizadores, un modelo** (el modelo NUNCA se mezcla con la interfaz):

| Renderizador | Rol | Motor |
|---|---|---|
| **matplotlib** | app interactiva (sliders) + figuras de reporte | `simuladores/graficos.py` |
| **Manim** | animaciones de "ver el método en movimiento" | `estadistica/animaciones/` (env conda aparte) |

Un mismo tema puede tener figura estática (reporte), exploración interactiva
(sliders: mover $\mu,\sigma,n,\lambda$ y ver la distribución en vivo) y una
animación (la convergencia desplegándose en el tiempo).

## 2. El patrón de un modelo (reutiliza `base.py`)

Un tema = `modelos/nivel_NN/eNN_slug.py` con la `Ficha` pedagógica estándar,
adaptada a estadística:

- `Ficha.contexto/autores`: historia del concepto (Bernoulli, Gauss, Fisher,
  Pearson, Neyman, Bayes, Gosset/"Student", Kolmogorov…).
- `Ficha.derivacion`: la derivación matemática en LaTeX, paso a paso (el corazón).
- `Ficha.ecuaciones` / `Ficha.intuicion` / `Ficha.limitaciones`.
- `parametros`: los parámetros del método ($\mu,\sigma,n,\lambda,\alpha,\beta$…).
- `curvas(params)`: la distribución / histograma (usa `"barras"` del motor) /
  distribución muestral / recta de regresión.
- `resultados(params)`: los estadísticos calculados.
- `escenarios`: distintos ajustes (n pequeño vs grande; sesgada vs simétrica).
- `verificaciones`: **los TEOREMAS como aserciones numéricas** — el análogo
  estadístico de las identidades del macro-lab:
  - identidades exactas: $E[\bar X]=\mu$, $\operatorname{Var}(\bar X)=\sigma^2/n$,
    $\sum(x_i-\bar x)=0$, $\hat\beta=(X'X)^{-1}X'Y$ reproduce a `polyfit`.
  - convergencias con tolerancia y **semilla fija**: TCL (la media muestral se
    aproxima a normal), LGN ($\bar X_n\to\mu$), cobertura de un IC 95% ≈ 0.95,
    tasa de error tipo I ≈ $\alpha$ bajo $H_0$.

**Aleatoriedad reproducible**: `np.random.default_rng(semilla)` con semilla fija
(convención del lab, como `m17`) — las verificaciones estocásticas deben dar el
mismo número cada corrida.

Reglas heredadas del macro-lab: procedencia declarada (sin citas de página no
verificadas); `python3 main.py verificar` al 100% y fila en la matriz de
trazabilidad antes de dar un modelo por bueno; `salidas/` regenerable.

## 3. Datos reales (política actualizada 2026-08-20)

Edison **levantó la política solo-ejemplos** (regla 0): se descargan datos reales
*poco a poco*. Cada bloque del currículo culmina aplicando el método a **datos
reales** (vía los conectores de datafw + capa `clean`): INEI/ENAHO (pobreza,
empleo, educación — Ayacucho, provincias, distritos), BCRP (ya embebido para el
macro-lab), etc. Regla: incremental (dataset a dataset), procedencia declarada,
sin cosechas masivas; no redistribuir microdatos restringidos (`data/` nunca a
repos públicos).

## 4. El currículo — 239 temas en 20 secciones

(Lista completa en la conversación de diseño; mapa de secciones aquí.)

| # | Sección | Temas | Simulación insignia |
|---|---|---|---|
| I | Fundamentos: datos y medición | 1-16 | poblaciones artificiales; ¿la muestra representa a la población? |
| II | Estadística descriptiva | 17-33 | mover un dato extremo y ver cambiar media/mediana/varianza (robustez) |
| III | Probabilidad | 34-48 | monedas/dados/cartas; demostrar $P(A\mid B)=P(A\cap B)/P(B)$ |
| IV | Distribuciones de probabilidad | 49-63 | mover $\mu,\sigma,\lambda,\alpha,\beta$ y ver la distribución en vivo |
| V | Teoremas fundamentales | 64-71 | **TCL** (✔ animación e67); LGN; convergencias |
| VI | Muestreo | 72-81 | población → métodos de muestreo → sesgo y error muestral |
| VII | Inferencia estadística | 82-96 | propiedades de estimadores; IC y su cobertura real |
| VIII | Pruebas de hipótesis | 97-112 | ¿qué es de verdad un valor-p? (miles de experimentos bajo $H_0$) |
| IX | Pruebas no paramétricas | 113-122 | chi-cuadrado, Mann-Whitney, KS, Shapiro-Wilk |
| X | Correlación y asociación | 123-130 | $X\to Y$ vs $X\leftarrow Z\to Y$: por qué correlación ≠ causa |
| XI | Regresión estadística | 131-143 | derivar $\hat\beta=(X'X)^{-1}X'Y$; distribución del estimador |
| XII | Diagnóstico de modelos | 144-152 | residuos, heterocedasticidad, Cook, VIF (puente a econometría) |
| XIII | Máxima verosimilitud | 153-160 | mover $\theta$ y ver $L(\theta\mid x)$ hasta el máximo |
| XIV | Métodos bayesianos | 161-172 | priori × verosimilitud → posteriori; MCMC actualizando creencias |
| XV | Bootstrap y simulación | 173-180 | remuestreo; distribución muestral por Monte Carlo |
| XVI | Multivariante | 181-192 | PCA, clustering, Mahalanobis |
| XVII | Series temporales | 193-207 | AR/MA/ARIMA/VAR; cointegración (aplicada a economía) |
| XVIII | Estadística espacial | 208-213 | Moran's I, LISA — Ayacucho, provincias, pobreza |
| XIX | Estadística causal | 214-224 | DAGs, DiD, IV, RD, control sintético — puente a econometría |
| XX | Computacional y ML | 225-239 | regularización, árboles, bosques, boosting, sesgo-varianza |

Las secciones XII, XVII y XIX **conectan con econometría**; la XIX es el puente
Estadística → Econometría → inferencia causal. La econometría pedagógica NO
duplicará `pipeline/` (hará fichas sobre los métodos ya implementados allí).

## 5. Estado

- **Hito 0 (2026-08-20): capa de animación Manim VALIDADA.** Entorno conda
  `manim-datafw` (Manim 0.20.1) sobre ffmpeg 8 + TeX Live 2025. Primera escena:
  `animaciones/e67_tcl.py` (Teorema Central del Límite). Utilidades compartidas
  en `animaciones/_comun.py`. ✔
- **Hito 1 (2026-08-20): scaffolding + primeros modelos.** `config.py` (paletas,
  rutas, secciones) y `main.py` (CLI `verificar`/`reporte`/`listar`/`ficha`/…,
  descubrimiento con id genérico `eNN`) reusan el motor de la raíz. Primeros dos
  modelos, uno por sección ancla, con Ficha completa + verificaciones (los
  teoremas):
  - **e02 población y muestra** (sec. I): el modelo FUNDACIONAL. Población
    bimodal conocida → miles de muestras → x̄ insesgada (E[x̄]=μ), error estándar
    σ/√n, precisión ∝ √n. Verifica los 4 teoremas del muestreo.
  - **e17 media aritmética** (sec. II): la media como centro de masa
    (Σ(xᵢ−x̄)=0) y minimizador del error cuadrático (x̄=argmin Σ(xᵢ−a)², semilla
    de la regresión); y su fragilidad (punto de ruptura 0%).
  Total: **2 modelos, 10 verificaciones**; `python3 main.py verificar` al 100%. ✔
- **Siguiente:** completar la sección II (e18 mediana, e19 moda, …, e27 varianza,
  e32-e33 robustez — el demo `demos/robustez_interactiva.py` pasa a ser la vista
  interactiva de e32); luego la `app.py` interactiva (adaptada del motor con
  las secciones de `config.SECCIONES`); y las animaciones Manim por tema. Ir
  sección por sección (239 temas es un maratón).
