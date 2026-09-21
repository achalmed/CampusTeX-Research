---
tipo: readme
estado: activo
---
# animaciones/ — capa de animación (Manim) del laboratorio de estadística

Animaciones matemáticas del currículo de estadística con
[Manim Community](https://www.manim.community/). Es la capa que muestra
**el método en movimiento** (la convergencia del TCL, una distribución que se
deforma al mover $\mu,\sigma$, el remuestreo bootstrap, el descenso de
gradiente, una cadena MCMC explorando…) — lo que la figura estática de
matplotlib no puede.

## Filosofía (dos renderizadores, un modelo)

El laboratorio separa el **modelo** de la **interfaz** (principio del macro-lab).
La lógica de simulación es la fuente de verdad; se visualiza de dos formas
complementarias:

| Renderizador | Para qué | Dónde |
|---|---|---|
| **matplotlib** | app interactiva (sliders, exploración en vivo) + figuras de reporte | `simuladores/graficos.py` (motor reutilizado) |
| **Manim** (esta carpeta) | animaciones pulidas de "ver qué hace el método" | `estadistica/animaciones/` |

Manim **complementa**, no reemplaza: rinde *video* (lento, offline, no
interactivo), ideal para procesos que se despliegan en el tiempo; la
interactividad sigue en matplotlib.

## Entorno (conda aparte — importante)

Manim trae dependencias pesadas (pango, cairo, ffmpeg) y `manimpango` **no
tiene wheel para Python 3.13**, así que NO se instala en el env del lab. Vive en
un entorno conda propio (aísla el runtime de matplotlib del macro-lab):

```bash
conda create -y -n manim-datafw -c conda-forge python=3.12 manim
```

El sistema ya aporta lo demás: **ffmpeg** (codifica el video) y **TeX Live +
dvisvgm** (para que `MathTex` rinda LaTeX real — las derivaciones se ven como
en un libro, p. ej. $\hat\beta=(X'X)^{-1}X'Y$).

## Renderizar

```bash
# desde estadistica/animaciones/
MANIM=~/anaconda3/envs/manim-datafw/bin/manim
SAL=../salidas/animaciones            # regenerable, en .gitignore

# vista rápida (480p15): validar la escena
$MANIM -ql --media_dir $SAL e67_tcl.py TeoremaCentralLimite

# calidad media (720p30) / alta (1080p60) para la versión final
$MANIM -qm --media_dir $SAL e67_tcl.py TeoremaCentralLimite
$MANIM -qh --media_dir $SAL e67_tcl.py TeoremaCentralLimite

# GIF en vez de mp4:  añadir  --format=gif
```

El video queda en `estadistica/salidas/animaciones/videos/<archivo>/<calidad>/`.

## Convenciones

- **Un archivo por tema**: `eNN_slug.py` (NN = tema del currículo; ver
  `../docs/laboratorio-estadistica.md`). Una clase `Scene` con nombre descriptivo.
- **Aleatoriedad reproducible**: `rng(semilla)` de `_comun.py` con semilla fija
  (convención del lab, como `m17`) — la animación debe ser idéntica cada render.
- **Paleta e identidad**: importar colores y helpers de `_comun.py`
  (`histograma`, `pdf_normal`, `titulo_lab`) — prohibido copiarlos por escena.
- **Matemática en LaTeX**: usar `MathTex`/`Tex` para fórmulas y derivaciones
  (no imágenes ni texto plano) — el objetivo es *derivar*, no solo mostrar.
- **La escena solo VISUALIZA**: la simulación (p. ej. `_dist_muestral`) es la
  misma lógica que alimentaría un modelo `base.py`; no mezclar cálculo pesado
  específico del modelo con la coreografía Manim.

## Escenas

| Tema | Archivo | Escena | Concepto |
|---|---|---|---|
| 67 | `e67_tcl.py` | `TeoremaCentralLimite` | El TCL: la media muestral tiende a la normal (población exponencial → $\bar X \sim N(\mu,\sigma^2/n)$) |
