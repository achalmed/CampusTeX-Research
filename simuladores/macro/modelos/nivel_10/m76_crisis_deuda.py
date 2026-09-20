"""simuladores/macro/modelos/nivel_10/m76_crisis_deuda.py — crisis de deuda soberana: la zona de crisis (nivel 10).

La prima de riesgo NO es exógena (contra m64-m65): el mercado cobra r según
el default que ESPERA, y el default depende de si el servicio cabe en la
capacidad de pago κ (% del PIB). Eso crea equilibrios AUTOCUMPLIDOS
(Calvo 1988; Cole-Kehoe):
  servicio a tasa segura:  s_safe(b)  = rf·b/100
  servicio a tasa de pánico: s_panic(b) = (rf+spread)·b/100
  equilibrio BUENO existe  ⟺ s_safe(b) ≤ κ  (se puede pagar si nadie entra en pánico)
  equilibrio MALO existe   ⟺ s_panic(b) > κ  (NO se puede pagar si todos entran en pánico)
Tres zonas por umbrales de deuda:
  b < b_panic:            SOLO bueno (hasta el pánico es pagable) — deuda segura
  b_panic < b < b_safe:   AMBOS — la ZONA DE CRISIS (la creencia decide)
  b > b_safe:             SOLO malo — insolvencia (ni la tasa segura cabe)
El "lo que sea necesario" de Draghi (mención) coordinó al euro fuera del
equilibrio malo sin gastar apenas — como el seguro de m73.

Procedencia: Calvo (1988), Cole-Kehoe (crisis de confianza / zona de
crisis) — menciones; conocimiento general. Calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _servicios(b, p):
    s_safe = p["rf"] * b / 100
    s_panic = (p["rf"] + p["spread"]) * b / 100
    return s_safe, s_panic


def _umbrales(p):
    b_safe = p["kappa"] * 100 / p["rf"] if p["rf"] > 0 else float("inf")
    b_panic = p["kappa"] * 100 / (p["rf"] + p["spread"]) if (p["rf"] + p["spread"]) > 0 else float("inf")
    return b_panic, b_safe                             # b_panic < b_safe siempre


def _regimen(p, b=None):
    b = p["b"] if b is None else b
    s_safe, s_panic = _servicios(b, p)
    bueno = s_safe <= p["kappa"]
    malo = s_panic > p["kappa"]
    if bueno and malo:
        return "zona de crisis (múltiples)"
    if bueno and not malo:
        return "seguro (solo bueno)"
    return "insolvente (solo malo)"


def _curvas(p):
    b = np.linspace(10, 200, 300)
    s_safe, s_panic = _servicios(b, p)
    b_panic, b_safe = _umbrales(p)
    return {"lineas": {"servicio a tasa segura $r_f\\,b$": (b, s_safe, config.AZUL2),
                       "servicio a tasa de pánico $(r_f{+}spr)\\,b$": (b, s_panic, config.ROJO),
                       "capacidad de pago $\\kappa$": (b, np.full_like(b, p["kappa"]), config.GRIS)},
            "puntos": [(b_panic, p["kappa"], f"$b_{{pánico}}={b_panic:.0f}\\%$"),
                       (b_safe, p["kappa"], f"$b_{{seguro}}={b_safe:.0f}\\%$"),
                       (p["b"], float(_servicios(p["b"], p)[0]), "tu país")],
            "anotacion": (f"tu deuda $b={p['b']:.0f}\\%$ → {_regimen(p)}\n"
                          f"zona de crisis: $[{b_panic:.0f}\\%, {b_safe:.0f}\\%]$\n"
                          "en la zona, la creencia del mercado decide el destino")}


def _resultados(p):
    b_panic, b_safe = _umbrales(p)
    s_safe, s_panic = _servicios(p["b"], p)
    return {"servicio a tasa segura (% PIB)": s_safe,
            "servicio a tasa de pánico (% PIB)": s_panic,
            "capacidad de pago κ (% PIB)": p["kappa"],
            "umbral inferior b_pánico (%)": b_panic,
            "umbral superior b_seguro (%)": b_safe,
            "régimen (0 seguro,1 crisis,2 insolvente)":
                {"seguro (solo bueno)": 0.0, "zona de crisis (múltiples)": 1.0,
                 "insolvente (solo malo)": 2.0}[_regimen(p)]}


def _ecuaciones_calibradas(p):
    b_panic, b_safe = _umbrales(p)
    return [f"$s_{{safe}} = {p['rf']:.1f}\\times{p['b']:.0f}/100 = {_servicios(p['b'], p)[0]:.2f}$",
            f"$s_{{panic}} = {p['rf'] + p['spread']:.1f}\\times{p['b']:.0f}/100 = {_servicios(p['b'], p)[1]:.2f}$",
            f"zona: $[{b_panic:.0f}, {b_safe:.0f}]$; $\\kappa={p['kappa']:.1f}$"]


_P0 = {"b": 90.0, "rf": 2.0, "spread": 6.0, "kappa": 3.5}


def _v_zona_de_crisis():
    # b=90 con estos parámetros debe caer en la zona múltiple
    reg = _regimen(_P0)
    s_safe, s_panic = _servicios(_P0["b"], _P0)
    return reg == "zona de crisis (múltiples)" and s_safe <= _P0["kappa"] < s_panic, \
        (f"con b=90%: se paga a tasa segura ({s_safe:.2f}≤κ) pero NO a tasa de pánico "
         f"({s_panic:.2f}>κ) — DOS equilibrios autocumplidos (Calvo/Cole-Kehoe)")


def _v_umbrales_ordenados():
    b_panic, b_safe = _umbrales(_P0)
    return b_panic < b_safe, \
        (f"b_pánico ({b_panic:.0f}%) < b_seguro ({b_safe:.0f}%): la zona de crisis es el "
         "intervalo entre 'siempre pagable' e 'insolvente' — un país puede estar sano y frágil a la vez")


def _v_deuda_baja_segura():
    reg = _regimen(dict(_P0, b=30.0))
    return reg == "seguro (solo bueno)", \
        ("con deuda baja (30%) hasta la tasa de pánico es pagable: SOLO el equilibrio bueno — "
         "la deuda baja compra inmunidad al pánico (el premio de m64-m65)")


def _v_deuda_alta_insolvente():
    reg = _regimen(dict(_P0, b=200.0))
    return reg == "insolvente (solo malo)", \
        ("con deuda altísima (200%) ni la tasa segura cabe en κ: SOLO el equilibrio malo — "
         "insolvencia genuina, no pánico (Grecia, mención)")


MODELO = Modelo(
    id="m76", nivel=10,
    nombre="Crisis de deuda soberana (zona de crisis)",
    xlabel="Deuda/PIB $b$ (%)", ylabel="Servicio de deuda / capacidad (% PIB)",
    parametros=[
        Parametro("b", _P0["b"], 20, 220, 10, "Deuda/PIB del país b (%)", grupo="posición",
                  definicion="entre b_pánico y b_seguro = zona de crisis (frágil)"),
        Parametro("spread", _P0["spread"], 1, 12, 0.5, "Prima de pánico (pp)", grupo="mercado",
                  definicion="cuánto sube la tasa si el mercado teme el default"),
        Parametro("rf", _P0["rf"], 0.5, 5, 0.25, "Tasa libre de riesgo rf (%)", grupo="mercado"),
        Parametro("kappa", _P0["kappa"], 1.5, 7, 0.25, "Capacidad de pago κ (% PIB)", grupo="fundamentos",
                  definicion="el máximo servicio que el país puede/quiere pagar (m65)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué dos países idénticos pueden tener uno tasa baja y otro tasa de default — sin diferencia en sus fundamentos?",
        variables=[("s_safe, s_panic", "servicio a tasa segura vs de pánico"),
                   ("κ", "la capacidad de pago — el techo de m65"),
                   ("la zona de crisis", "[b_pánico, b_seguro]: donde la creencia decide")],
        derivacion=["mercado\\;cobra\\;según\\;el\\;default\\;que\\;espera:\\;r\\in\\{r_f,\\;r_f{+}spr\\}",
                    "bueno \\iff r_f\\,b/100 \\leq \\kappa \\;;\\;\\; malo \\iff (r_f{+}spr)\\,b/100 > \\kappa",
                    "b_{pánico} = \\frac{100\\kappa}{r_f+spr} < b < \\frac{100\\kappa}{r_f} = b_{seguro}"],
        contexto=("m64-m65 supusieron la tasa r exógena; la realidad la hace "
                  "endógena a la CREENCIA sobre el default — y ese lazo crea "
                  "equilibrios múltiples. Calvo (1988) y Cole-Kehoe mostraron la "
                  "'zona de crisis': un intervalo de deuda donde el país es a la vez "
                  "solvente (puede pagar a tasa normal) y vulnerable (no puede pagar "
                  "si el mercado entra en pánico y le sube la tasa). Dentro de esa "
                  "zona, la profecía se autocumple: si el mercado cree que no habrá "
                  "default, cobra poco y el país paga; si teme el default, cobra "
                  "mucho y el mayor servicio VUELVE el default real — la corrida de "
                  "m73 aplicada al Tesoro. La crisis del euro (2010-2012, mención) "
                  "fue exactamente esto: España e Italia, solventes, empujadas hacia "
                  "el equilibrio malo por el pánico — hasta que el 'whatever it "
                  "takes' de Draghi (mención) coordinó al mercado en el bueno sin "
                  "gastar casi nada, como el seguro de depósitos de m73."),
        autores=("Calvo (1988); Cole y Kehoe (crisis de confianza, zona de crisis "
                 "— menciones); la evidencia del euro y el backstop del BCE "
                 "(mención)."),
        supuestos=[
            "Dos tasas posibles (segura y de pánico) según la creencia: la realidad es un continuo, pero la lógica bi-estable es la misma.",
            "κ exógena (m65): el techo de pago sigue siendo la variable más incierta — política pura.",
            "Salto instantáneo entre equilibrios: Cole-Kehoe añaden probabilidad de 'sunspot' que dispara el malo — aquí, determinista por zonas.",
        ],
        ecuaciones=[
            Ecuacion("b_{pánico} = \\frac{100\\,\\kappa}{r_f + spr} \\;<\\; b_{seguro} = \\frac{100\\,\\kappa}{r_f}",
                     "los dos umbrales",
                     "debajo de b_pánico ni el pánico tumba al país; encima de b_seguro ni la "
                     "calma lo salva; en medio, la ZONA DE CRISIS donde manda la creencia."),
            Ecuacion("bueno \\land malo \\iff b \\in [b_{pánico}, b_{seguro}]",
                     "equilibrios autocumplidos",
                     "el mismo país, con los mismos fundamentos, sostenible o en default según lo "
                     "que el mercado espere — coordinación pura (verificado por zonas)."),
        ],
        intuicion=("La deuda soberana en la zona de crisis es un juego de confianza, "
                   "no un problema de aritmética: el mercado que cree que le pagarán "
                   "cobra poco (y le pagan), el que teme el default cobra mucho (y lo "
                   "provoca). Por eso los rescates que FUNCIONAN son los que "
                   "coordinan expectativas: el BCE prometió comprar deuda ilimitada "
                   "y casi no compró, igual que el seguro de m73. Y por eso el grado "
                   "de inversión vale tanto — mantiene al país a la izquierda de "
                   "b_pánico, en la zona segura, fuera del alcance del pánico. El "
                   "Perú lo alcanzó en 2008 (mención) tras la disciplina de "
                   "m64-m65: no es una etiqueta, es un domicilio en la zona segura."),
        equilibrio=("Tres regímenes por zonas (verificados): seguro (b<b_pánico), "
                    "crisis/múltiple (b_pánico<b<b_seguro) e insolvente (b>b_seguro). "
                    "En la zona de crisis, dos equilibrios estables — la firma de "
                    "las profecías autocumplidas (como m73, m74)."),
        limitaciones=[
            "Dos tasas discretas: la prima real es un continuo creciente en el riesgo percibido — suaviza las fronteras pero mantiene la zona.",
            "Sin default parcial: el mundo real reestructura con quitas, no solo paga-o-no (m78, mención).",
            "El backstop no está modelado: agregarlo (un prestamista que promete comprar) ELIMINA el equilibrio malo — el punto práctico (Draghi, FMI).",
        ],
        evolucion=("Cierra la trilogía de profecías autocumplidas del nivel "
                   "(m73 bancaria, m74 cambiaria, m76 soberana): las tres son "
                   "coordinación con backstop como cura. m78 muestra qué pasa "
                   "cuando la zona insolvente se alcanza (la trampa), y el riesgo "
                   "soberano peruano (grado de inversión, EMBI) es contexto de "
                   "m108/m110."),
    ),
    escenarios=[
        Escenario("zona_de_crisis", "deuda de 90%: solvente PERO vulnerable",
                  {"b": 90.0},
                  "se paga a tasa segura (1.8%≤3.5) pero NO a tasa de pánico "
                  "(7.2%>3.5): dos equilibrios — España/Italia 2011, empujadas al "
                  "malo por el miedo (mención).",
                  cadena=["deuda en la zona [b_pánico, b_seguro]", "si el mercado confía: tasa baja, se paga",
                          "si teme: tasa de pánico, el servicio no cabe", "el default se autocumple",
                          "la creencia crea la realidad (como m73)"]),
        Escenario("grado_de_inversion", "disciplina lleva la deuda a 30%",
                  {"b": 30.0},
                  "hasta la tasa de pánico es pagable: SOLO el equilibrio bueno — "
                  "fuera del alcance del pánico, el premio de la disciplina peruana "
                  "(m64-m65, grado de inversión 2008).",
                  cadena=["deuda baja (< b_pánico)", "el servicio cabe en κ aun con prima máxima",
                          "el pánico no puede tumbar al país", "equilibrio único bueno",
                          "la credibilidad como domicilio seguro (m41)"]),
        Escenario("insolvencia_genuina", "deuda de 200%: ni la calma salva",
                  {"b": 200.0},
                  "ni siquiera a tasa segura el servicio cabe en κ: SOLO el "
                  "equilibrio malo — insolvencia real, no pánico (Grecia necesitaba "
                  "quita, no confianza; mención).",
                  cadena=["deuda > b_seguro", "el servicio supera κ hasta a tasa segura",
                          "no hay confianza que alcance", "insolvencia genuina",
                          "la salida es reestructurar (m78), no coordinar"]),
        Escenario("mercado_nervioso", "el mismo 90% con prima de pánico mayor (spread=10)",
                  {"spread": 10.0},
                  "la zona de crisis se agranda hacia abajo (b_pánico cae): mercados "
                  "más nerviosos vuelven vulnerables a deudas menores — el contagio "
                  "que corre la frontera.",
                  cadena=["↑spread (mercado nervioso, contagio)", "b_pánico baja",
                          "la zona de crisis se ensancha", "deudas antes seguras entran en zona",
                          "el pánico se autoexpande (m80)"]),
    ],
    verificaciones=[
        Verificacion("b=90%: zona de crisis (dos equilibrios)", _v_zona_de_crisis),
        Verificacion("umbrales ordenados: b_pánico < b_seguro", _v_umbrales_ordenados),
        Verificacion("deuda baja: solo equilibrio bueno (inmune al pánico)", _v_deuda_baja_segura),
        Verificacion("deuda altísima: insolvencia genuina (solo malo)", _v_deuda_alta_insolvente),
    ],
    notas="La corrida de m73 aplicada al Tesoro: en la zona de crisis, el mercado que teme el default lo provoca. El backstop coordina.",
)
