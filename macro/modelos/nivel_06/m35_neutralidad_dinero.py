"""simuladores/macro/modelos/nivel_06/m35_neutralidad_dinero.py — neutralidad del dinero: la síntesis dinámica (nivel 6).

El experimento monetario definitivo sobre el aparato AD-AS dinámico (m25):
una emisión permanente dM y DOS relojes en el mismo gráfico (índices base=100):
  Y_t  sube de impacto (no-neutralidad de corto plazo, m23)…
       …y regresa exactamente a Y* (neutralidad de largo plazo, m22)
  P_t  sube y se queda: al final, TODO el dinero se hizo precios.
La duración del tránsito (que gobierna λ) es el espacio vital de la política
monetaria: neutral al final, potente mientras tanto.

Procedencia: experimento mental de Hume (1752, Of Money — mención) sobre la
maquinaria de la síntesis (m20-m25) — conocimiento general.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_04 import _adas
import config


def _trayectoria(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    F, bh, Ac = _adas.estructura(dict(p, T=p["T_imp"]))
    M1 = p["M"] + p["dM"]
    pe = p["Pe0"]
    Ys, Ps = [], []
    for _ in range(T + 1):
        Y, P = _adas.equilibrio_corto(F, bh, Ac, M1, pe, p["lam"], p["Ystar"])
        Ys.append(Y); Ps.append(P)
        pe = P
    return np.array(Ys), np.array(Ps)


def _curvas(p):
    Ys, Ps = _trayectoria(p)
    t = np.arange(len(Ys))
    iY = 100 * Ys / p["Ystar"]
    iP = 100 * Ps / p["Pe0"]
    razon_m = 100 * (p["M"] + p["dM"]) / p["M"]
    return {"lineas": {"producto $Y_t$ (índice, $Y^*{=}100$)": (t, iY, config.AZUL2),
                       "precios $P_t$ (índice, $P_0{=}100$)": (t, iP, config.ROJO),
                       "neutralidad: $100 \\cdot M'/M$": (t, np.full(len(t), razon_m), config.GRIS)},
            "anotacion": (f"impacto: $Y$ sube a {iY[0]:.1f} — corto plazo NO neutral\n"
                          f"final: $Y \\to 100$ y $P \\to {razon_m:.1f}$ — largo plazo neutral\n"
                          f"el tránsito dura lo que $\\lambda$ permita")}


def _resultados(p):
    Ys, Ps = _trayectoria(p, T=400)
    Ys0, Ps0 = _trayectoria(p)
    return {"Y de impacto (t=0)": float(Ys0[0]),
            "Y de largo plazo": float(Ys[-1]),
            "P inicial": p["Pe0"], "P de largo plazo": float(Ps[-1]),
            "razón P_∞/P_0": float(Ps[-1]) / p["Pe0"],
            "razón M'/M": (p["M"] + p["dM"]) / p["M"],
            "períodos con brecha > 0.5": float(np.sum(np.abs(Ys0 - p["Ystar"]) > 0.5))}


_P0 = {"dM": 60.0, "T": 15.0, "lam": 0.004,
       "c0": 100.0, "c1": 0.6, "I0": 150.0, "b": 20.0, "G": 200.0, "T_imp": 100.0,
       "k": 0.5, "h": 10.0, "M": 590.0, "Pe0": 2.0, "Ystar": 700.0}


def _v_neutral_largo():
    r = _resultados(_P0)
    razon_p, razon_m = r["razón P_∞/P_0"], r["razón M'/M"]
    ok = (abs(r["Y de largo plazo"] - _P0["Ystar"]) < 1e-6
          and abs(razon_p - razon_m) < 1e-6)
    return ok, (f"al final Y = Y* y P escala EXACTAMENTE con M "
                f"(razón P {razon_p:.4f} = razón M {razon_m:.4f})")


def _v_no_neutral_corto():
    r = _resultados(_P0)
    return r["Y de impacto (t=0)"] > _P0["Ystar"] + 1, \
        (f"de impacto Y = {r['Y de impacto (t=0)']:,.1f} > Y*: el mismo dinero que al final "
         "es velo, al principio es demanda")


def _v_rigidez_alarga():
    p_rigido = dict(_P0, lam=0.002)
    n1 = _resultados(_P0)["períodos con brecha > 0.5"]
    n2 = _resultados(p_rigido)["períodos con brecha > 0.5"]
    return n2 > n1, (f"con precios más rígidos (λ 0.004→0.002) la no-neutralidad dura más "
                     f"({n1:.0f} → {n2:.0f} períodos): λ es la vida útil de la política monetaria")


def _v_dosis_no_cambia_destino():
    r1 = _resultados(_P0)
    r2 = _resultados(dict(_P0, dM=120.0))
    ok = abs(r2["Y de largo plazo"] - _P0["Ystar"]) < 1e-6 and r2["P de largo plazo"] > r1["P de largo plazo"]
    return ok, "el doble de emisión NO deja más producto final — solo más precios: la dosis cambia P, no Y"


MODELO = Modelo(
    id="m35", nivel=6,
    nombre="Neutralidad del dinero",
    xlabel="Período $t$", ylabel="Índices (base = 100)",
    parametros=[
        Parametro("dM", _P0["dM"], 10, 200, 10, "Emisión permanente dM", grupo="experimento"),
        Parametro("lam", _P0["lam"], 0.001, 0.012, 0.001, "Rigidez λ (velocidad del ajuste)", grupo="estructura"),
        Parametro("T", _P0["T"], 5, 60, 1, "Períodos mostrados", grupo="experimento"),
        Parametro("M", _P0["M"], 400, 800, 10, "Dinero inicial M", grupo="estructura"),
        Parametro("Ystar", _P0["Ystar"], 620, 780, 10, "Producto potencial Y*", grupo="estructura"),
        Parametro("Pe0", _P0["Pe0"], 1.5, 2.8, 0.1, "Precio inicial P0", grupo="estructura"),
        Parametro("c1", _P0["c1"], 0.3, 0.85, 0.05, "Propensión a consumir c1", grupo="estructura"),
        Parametro("b", _P0["b"], 8, 35, 1, "Sensibilidad de I a r (b)", grupo="estructura"),
        Parametro("k", _P0["k"], 0.25, 0.9, 0.05, "Demanda de dinero por Y (k)", grupo="estructura"),
        Parametro("h", _P0["h"], 5, 22, 1, "Demanda de dinero por r (h)", grupo="estructura"),
        Parametro("c0", _P0["c0"], 60, 180, 10, "Consumo autónomo c0", grupo="estructura"),
        Parametro("I0", _P0["I0"], 80, 260, 10, "Inversión autónoma I0", grupo="estructura"),
        Parametro("G", _P0["G"], 120, 300, 10, "Gasto público G", grupo="estructura"),
        Parametro("T_imp", _P0["T_imp"], 20, 250, 10, "Impuestos T", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="Si el dinero es un velo, ¿por qué la política monetaria mueve al mundo — y por cuánto tiempo?",
        variables=[("Y_t, P_t", "producto y precios en el tránsito — endógenos"),
                   ("dM", "la emisión permanente — el experimento de Hume"),
                   ("λ", "rigidez de precios — la VIDA ÚTIL de la no-neutralidad")],
        derivacion=["t=0: \\;P^e\\;fijo \\Rightarrow \\;\\uparrow M/P \\Rightarrow \\downarrow r \\Rightarrow \\uparrow Y \\;(m23)",
                    "P^e_{t+1} = P_t: \\;la\\;SRAS\\;sube\\;período\\;a\\;período\\;(m25)",
                    "t\\to\\infty: \\;Y=Y^*, \\;\\frac{P_\\infty}{P_0} = \\frac{M'}{M} \\;(m22)"],
        contexto=("Hume (1752) imaginó que cada británico amanecía con el doble de "
                  "monedas en el bolsillo: nada real cambiaría, solo los precios. Dos "
                  "siglos y medio después la profesión suscribe el punto… con una "
                  "corrección decisiva: EN EL TRÁNSITO — meses o años, según la "
                  "rigidez — el dinero mueve producción y empleo. La política "
                  "monetaria vive enteramente en esa ventana: neutral al final, "
                  "poderosa mientras tanto."),
        autores=("Hume (1752, mención); la neutralidad de largo plazo es patrimonio "
                 "clásico-monetarista (Friedman); la duración del tránsito, el gran "
                 "tema de Lucas (1995, Nobel por la no-neutralidad con expectativas) "
                 "y de los nuevos keynesianos."),
        supuestos=["Todo el aparato AD-AS dinámico (m20-m25): expectativas adaptativas, Y* fijo, dinero exógeno.",
                   "La emisión es PERMANENTE y de una vez (nivel, no tasa): la superneutralidad — que cambiar la TASA de emisión tampoco afecte lo real — es otra pregunta (m36 la matiza).",
                   "Sin costos de la inflación en sí (menú, redistribución): solo el mecanismo de ajuste."],
        ecuaciones=[
            Ecuacion("Y_0 > Y^* \\;\\to\\; Y_\\infty = Y^*", "no-neutralidad transitoria",
                     "el impacto es real porque los precios esperados están contratados; el final "
                     "es nominal porque nada real cambió."),
            Ecuacion("\\frac{P_\\infty}{P_0} = \\frac{M'}{M}", "neutralidad de largo plazo",
                     "la proporcionalidad cuantitativa (m34), ahora ALCANZADA por una trayectoria "
                     "verificable en vez de postulada."),
        ],
        intuicion=("El gráfico cuenta toda la historia monetaria en dos líneas: el "
                   "producto sube y regresa (una comba); los precios suben y se quedan "
                   "(una escalera). El área bajo la comba es lo que la política "
                   "monetaria puede 'comprar'; la altura de la escalera, lo que "
                   "siempre paga. Los bancos centrales modernos (m38-m40) son la "
                   "administración profesional de ese intercambio."),
        equilibrio=("El punto fijo del tránsito es (Y*, P0·M'/M): globalmente estable "
                    "vía Pe_{t+1}=P_t. Verificado con precisión 1e-6 en ambas patas."),
        limitaciones=[
            "Con expectativas RACIONALES y anuncio previo, el tránsito se comprime o desaparece (m42): esta duración es la del aprendizaje adaptativo.",
            "Superneutralidad no incluida: inflaciones permanentes distorsionan saldos reales y recaudan señoreaje (m36) — el dinero no es velo para la TASA.",
            "Y* fijo: con histéresis, recesiones monetarias podrían dejar cicatriz real (mención).",
        ],
        evolucion=("Cierra la trilogía cuantitativa (m22 estático, m23 corto plazo, "
                   "m35 la película completa) y plantea LA pregunta operativa: si solo "
                   "el tránsito es real, ¿cómo usarlo bien? m38 (regla), m40 (metas) y "
                   "m41 (credibilidad) son tres respuestas institucionales."),
    ),
    escenarios=[
        Escenario("experimento_de_hume", "emisión permanente dM = 60 (≈10%)",
                  {"dM": 60.0},
                  "Y sube ~2.3% de impacto y regresa; P termina exactamente 10% "
                  "arriba: la comba y la escalera.",
                  cadena=["↑M permanente", "M/P sube (Pe contratado)", "↓r ⇒ ↑I ⇒ ↑Y (impacto real)",
                          "brecha ⇒ sorpresas de precios", "SRAS sube período a período",
                          "Y→Y*, P escala con M: velo al final"]),
        Escenario("doble_dosis", "emisión del doble (dM = 120)",
                  {"dM": 120.0},
                  "más impacto transitorio y MISMO producto final — solo cambia cuánta "
                  "escalera de precios se paga.",
                  cadena=["↑↑M", "impacto real mayor", "el mismo mecanismo de ajuste",
                          "destino real idéntico (Y*)", "solo P termina más arriba"]),
        Escenario("precios_de_hielo", "rigidez extrema (λ = 0.001)",
                  {"lam": 0.001},
                  "la comba se estira: la no-neutralidad dura varias veces más — en "
                  "economías rígidas la política monetaria es más potente por más tiempo.",
                  cadena=["↓λ", "las sorpresas de precios corrigen lento",
                          "la brecha sobrevive muchos períodos", "ventana de política larga"]),
        Escenario("precios_de_mercurio", "flexibilidad alta (λ = 0.010)",
                  {"lam": 0.010},
                  "el ajuste casi instantáneo: en el límite flexible, hasta el corto "
                  "plazo es clásico y el dinero nace neutral.",
                  cadena=["↑λ", "los precios absorben el dinero casi de inmediato",
                          "comba mínima", "neutralidad casi desde t=0"]),
    ],
    verificaciones=[
        Verificacion("neutralidad de largo plazo exacta (Y=Y*, P∝M)", _v_neutral_largo),
        Verificacion("no-neutralidad de impacto (Y0 > Y*)", _v_no_neutral_corto),
        Verificacion("más rigidez ⇒ tránsito más largo", _v_rigidez_alarga),
        Verificacion("la dosis cambia P, nunca el Y final", _v_dosis_no_cambia_destino),
    ],
    notas="La comba (Y) y la escalera (P): toda la política monetaria vive en la comba.",
)
