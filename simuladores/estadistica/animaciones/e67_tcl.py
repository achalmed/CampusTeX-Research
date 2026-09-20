"""simuladores/estadistica/animaciones/e67_tcl.py — animación Manim del Teorema Central del Límite (sección V, tema 67).

La "estrella" del currículo de estadística (destacada por Edison): cómo la
distribución de la media muestral X̄ se aproxima a una normal al crecer n,
PARTIENDO de una población claramente NO normal (exponencial). Primera escena
de la capa de animación del laboratorio; valida el patrón Manim.

Convenciones del lab: aleatoriedad reproducible (semilla fija, como m17),
paleta del laboratorio (_comun) y matemática en LaTeX real (MathTex). La
lógica de simulación (dist_muestral) es la MISMA que alimentaría un modelo
base.py; esta capa solo la VISUALIZA (el modelo nunca se mezcla con la interfaz).

Render (env conda manim-datafw):
  ~/anaconda3/envs/manim-datafw/bin/manim -qm e67_tcl.py TeoremaCentralLimite
"""

from manim import *
import numpy as np

from _comun import (AZUL, AZUL_OSC, DORADO, ROJO, VERDE, GRIS,
                    rng, titulo_lab, histograma, pdf_normal)

_RNG = rng(42)


def _dist_muestral(n, reps=20000):
    """Distribución muestral de X̄ para tamaño n (población exponencial(1))."""
    return _RNG.exponential(scale=1.0, size=(reps, n)).mean(axis=1)


class TeoremaCentralLimite(Scene):
    def construct(self):
        poblacion = _RNG.exponential(scale=1.0, size=200000)
        mu, sigma = float(poblacion.mean()), float(poblacion.std())

        self.play(Write(titulo_lab("Teorema Central del Límite")))

        # --- Izquierda: la POBLACIÓN (sesgada, no normal) ---
        ejes_pob = Axes(x_range=[0, 5, 1], y_range=[0, 1.05, 0.5], x_length=5.4, y_length=3.0,
                        axis_config={"include_tip": False, "color": GRIS, "stroke_width": 2})
        ejes_pob.to_edge(LEFT, buff=0.55).shift(DOWN * 0.35)
        etq_pob = Text("Población: exponencial (sesgada)", color=VERDE, weight=BOLD)
        etq_pob.scale(0.42).next_to(ejes_pob, UP, buff=0.18)
        hist_pob = histograma(poblacion, ejes_pob, bins=45, rango=(0, 5), color=VERDE)
        linea_mu = DashedLine(ejes_pob.c2p(mu, 0), ejes_pob.c2p(mu, 1.0), color=ROJO, stroke_width=3)
        etq_mu = MathTex(r"\mu", color=ROJO).scale(0.7).next_to(linea_mu, UP, buff=0.05)

        self.play(Create(ejes_pob), FadeIn(etq_pob))
        self.play(FadeIn(hist_pob, shift=UP * 0.2))
        self.play(Create(linea_mu), Write(etq_mu))
        self.wait(0.6)

        # --- Derecha: la DISTRIBUCIÓN MUESTRAL de X̄ ---
        ejes_x = Axes(x_range=[0, 3, 1], y_range=[0, 3.2, 1], x_length=5.4, y_length=3.0,
                      axis_config={"include_tip": False, "color": GRIS, "stroke_width": 2})
        ejes_x.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.35)
        self.play(Create(ejes_x))

        def etiqueta(n):
            return MathTex(r"\bar{X}\ \text{de muestras de }", f"n={n}", color=AZUL).scale(0.5).next_to(ejes_x, UP, buff=0.18)

        def normal_en(n):
            sd = sigma / np.sqrt(n)
            return ejes_x.plot(pdf_normal(mu, sd), x_range=[max(0.01, mu - 4 * sd), min(3, mu + 4 * sd)],
                               color=DORADO, stroke_width=5)

        n = 2
        hist_x = histograma(_dist_muestral(n), ejes_x, bins=45, rango=(0, 3), color=AZUL)
        curva, etq_x = normal_en(n), etiqueta(n)
        self.play(FadeIn(hist_x), Write(etq_x))
        self.play(Create(curva))
        self.wait(0.7)

        for n in [5, 30]:
            nuevo_hist = histograma(_dist_muestral(n), ejes_x, bins=45, rango=(0, 3), color=AZUL)
            self.play(Transform(hist_x, nuevo_hist), Transform(curva, normal_en(n)),
                      Transform(etq_x, etiqueta(n)), run_time=1.4)
            self.wait(0.7)

        # --- El teorema, en LaTeX real ---
        formula = MathTex(r"\bar{X}_n \;\xrightarrow{\ d\ }\; N\!\left(\mu,\ \dfrac{\sigma^2}{n}\right)",
                          color=AZUL_OSC).scale(0.95).to_edge(DOWN, buff=0.35)
        caja = SurroundingRectangle(formula, color=DORADO, buff=0.18, corner_radius=0.1)
        self.play(Write(formula))
        self.play(Create(caja))
        self.wait(2)
