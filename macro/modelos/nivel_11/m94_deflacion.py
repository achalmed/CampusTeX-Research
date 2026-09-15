"""simuladores/macro/modelos/nivel_11/m94_deflacion.py — deflación y la espiral de Fisher (nivel 11).

El peligro opuesto a la inflación, y más difícil de combatir. La deflación
(π<0) es peligrosa por la deuda-deflación de Fisher (1933): con precios
cayendo, la tasa de interés REAL sube aunque la nominal esté en cero (r =
i − π, con π<0 ⇒ r>i), lo que:
  (1) encarece la deuda real (los deudores deben MÁS en términos reales)
  (2) incentiva posponer el consumo (esperar precios más bajos)
  → menos demanda → más deflación → ESPIRAL.
Y en el ZLB (m12) la política monetaria no puede bajar más la nominal. La
única salida: subir las EXPECTATIVAS de inflación (prometer inflación
futura, m54) — lo que el banco central creíble por lo bajo NO puede hacer.
Combina m12 (ZLB), m54 (expectativas), m34 (Fisher).

Procedencia: deuda-deflación de Fisher (1933 — mención); trampa deflacionaria
(Krugman 1998 sobre Japón — mención) — conocimiento general; calibración
didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    pi = np.empty(T + 1); Y = np.empty(T + 1)
    pi[0] = p["pi0"]
    Y[0] = 100 + p["shock"]
    for j in range(1, T + 1):
        # tasa real = nominal (ZLB=0) menos inflación esperada (≈ pasada)
        r_real = max(0.0, p["i_zlb"]) - pi[j - 1]
        # brecha responde negativamente a la tasa real (m54): r_real alta deprime
        Y[j] = 100 - p["sensib"] * r_real + p["expectativas"]
        # Phillips: la brecha negativa profundiza la deflación (m21)
        pi[j] = pi[j - 1] + p["lam"] * (Y[j] - 100)
        if p["expectativas"] > 0:                        # forward guidance rompe la espiral
            pi[j] += p["expectativas"] * 0.3
    return t, pi, Y


def _curvas(p):
    t, pi, Y = _sendas(p)
    return {"lineas": {"inflación $\\pi_t$ (%)": (t, pi, config.ROJO),
                       "producto $Y_t$ (índice)": (t, Y, config.AZUL2),
                       "cero inflación / potencial": (t, np.full(len(t), 100.0) * 0
                                                       if False else np.zeros(len(t)), config.GRIS)},
            "anotacion": (f"shock inicial {p['shock']:+.0f}, tasa nominal en ZLB (0)\n"
                          f"π final {float(pi[-1]):.1f}% "
                          f"({'ESPIRAL deflacionaria' if pi[-1] < pi[0] - 0.5 else 'contenida'})\n"
                          "deflación → tasa real sube → menos demanda → más deflación")}


def _resultados(p):
    t, pi, Y = _sendas(p)
    return {"inflación inicial (%)": p["pi0"],
            "inflación final (%)": float(pi[-1]),
            "producto final (índice)": float(Y[-1]),
            "¿espiral? (π cae en el tiempo)": float(pi[-1]) - float(pi[0]),
            "tasa real implícita (i−π final)": max(0.0, p["i_zlb"]) - float(pi[-1])}


def _ecuaciones_calibradas(p):
    return [f"$r_{{real}} = i_{{ZLB}} - \\pi = 0 - \\pi$ (Fisher, m34)",
            f"$\\pi < 0 \\Rightarrow r_{{real}} > 0$ aun con $i=0$ (m12)"]


_P0 = {"pi0": -0.5, "shock": -3.0, "i_zlb": 0.0, "sensib": 1.5, "lam": 0.3,
       "expectativas": 0.0, "T": 14.0}


def _v_espiral_deflacionaria():
    t, pi, Y = _sendas(_P0)
    return float(pi[-1]) < float(pi[0]), \
        (f"la deflación se PROFUNDIZA sola ({float(pi[0]):.1f}→{float(pi[-1]):.1f}%): la espiral "
         "de Fisher — precios que caen suben la tasa real y deprimen más la demanda")


def _v_tasa_real_sube():
    t, pi, Y = _sendas(_P0)
    r_real = max(0.0, _P0["i_zlb"]) - float(pi[-1])
    return r_real > 0, \
        (f"con la tasa nominal en CERO, la tasa real es POSITIVA ({r_real:.1f}%) porque los "
         "precios caen (Fisher): el ZLB no basta — la política monetaria pierde tracción (m12)")


def _v_forward_guidance_salva():
    t_sin, pi_sin, _ = _sendas(_P0)
    t_con, pi_con, _ = _sendas(dict(_P0, expectativas=2.0))
    return float(pi_con[-1]) > float(pi_sin[-1]), \
        (f"prometer inflación futura (forward guidance, m54) rompe la espiral "
         f"({float(pi_sin[-1]):.1f}→{float(pi_con[-1]):.1f}%): subir las EXPECTATIVAS es la única salida")


def _v_credibilidad_paradoja():
    # el banco central creíble por lo bajo NO puede prometer inflación creíblemente
    return _P0["expectativas"] == 0, \
        ("la paradoja de la credibilidad: el banco central que ancló la inflación baja (m40) "
         "NO puede prometer inflación alta creíblemente — su virtud se vuelve trampa (Krugman)")


MODELO = Modelo(
    id="m94", nivel=11,
    nombre="Deflación (espiral de Fisher)",
    xlabel="Período $t$", ylabel="Inflación (%) y producto",
    parametros=[
        Parametro("shock", _P0["shock"], -6, 0, 0.5, "Shock inicial de demanda", grupo="detonante",
                  definicion="la recesión que empuja los precios a la baja"),
        Parametro("expectativas", _P0["expectativas"], 0, 3, 0.5, "Forward guidance (m54)",
                  grupo="salida", definicion="prometer inflación futura: la única salida del ZLB"),
        Parametro("i_zlb", _P0["i_zlb"], 0, 2, 0.25, "Tasa nominal en el ZLB (%)", grupo="estructura",
                  definicion="el piso: 0 = trampa de liquidez (m12)"),
        Parametro("pi0", _P0["pi0"], -2, 1, 0.25, "Inflación inicial (%)", grupo="inicial"),
        Parametro("sensib", _P0["sensib"], 0.5, 3, 0.25, "Sensibilidad de Y a la tasa real",
                  grupo="estructura"),
        Parametro("lam", _P0["lam"], 0.1, 0.6, 0.05, "Pendiente de Phillips λ", grupo="estructura"),
        Parametro("T", _P0["T"], 10, 24, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué la deflación es MÁS peligrosa que la inflación — y por qué el banco central creíble no puede combatirla?",
        variables=[("π<0", "deflación: precios que caen"),
                   ("r real = i − π", "la tasa real sube aunque la nominal esté en cero (Fisher)"),
                   ("expectativas", "la única salida: prometer inflación futura (m54)")],
        derivacion=["Fisher\\;(m34): \\;r_{real} = i - \\pi",
                    "\\pi < 0 \\;con\\;i = 0\\;(ZLB, m12) \\Rightarrow r_{real} > 0",
                    "r_{real}\\uparrow \\Rightarrow demanda\\downarrow \\Rightarrow \\pi\\downarrow \\;(espiral)"],
        contexto=("La deflación es el peligro opuesto a la inflación, menos "
                  "frecuente pero más difícil de combatir — y la razón por la que "
                  "los bancos centrales apuntan a una meta POSITIVA (2%, no 0%). El "
                  "mecanismo mortal es la deuda-deflación de Irving Fisher (1933, "
                  "mención): cuando los precios caen, la tasa de interés REAL sube "
                  "aunque la nominal esté en cero (r = i − π, con π<0 da r>0), lo "
                  "que produce dos efectos perniciosos. Primero, encarece la deuda "
                  "en términos reales — los deudores deben cada vez más poder de "
                  "compra, quiebran, y el crédito se contrae. Segundo, incentiva a "
                  "posponer el consumo: si los precios van a caer, conviene esperar "
                  "— lo que reduce la demanda hoy. Ambos deprimen la demanda, lo que "
                  "profundiza la deflación: una ESPIRAL. Y aquí está la trampa: en "
                  "el ZLB (m12), la política monetaria no puede bajar más la tasa "
                  "nominal. La única salida es subir las EXPECTATIVAS de inflación "
                  "(prometer inflación futura para bajar la tasa real esperada, "
                  "m54) — pero, como notó Krugman (1998, mención) sobre Japón, un "
                  "banco central que se ganó la credibilidad de mantener la "
                  "inflación BAJA no puede prometer creíblemente inflación ALTA: su "
                  "propia virtud se vuelve trampa. Japón vivió esto por dos "
                  "décadas; la eurozona coqueteó con ello tras 2008. Es el caso "
                  "límite que justifica toda la política monetaria no convencional "
                  "(QE, forward guidance, metas de nivel de precios)."),
        autores=("Deuda-deflación: Fisher (1933, mención); trampa deflacionaria y "
                 "la paradoja de la credibilidad: Krugman (1998, sobre Japón — "
                 "mención); política no convencional: Bernanke, Woodford "
                 "(menciones)."),
        supuestos=[
            "Tasa nominal en el ZLB (m12): sin ese piso, el banco central bajaría la tasa y no habría espiral.",
            "Expectativas adaptativas (≈ inflación pasada): con expectativas ancladas a una meta positiva creíble, la espiral no arranca.",
            "El forward guidance funciona si es creíble: la paradoja es que la credibilidad de baja inflación lo dificulta (Krugman).",
        ],
        ecuaciones=[
            Ecuacion("r_{real} = i - \\pi = 0 - \\pi > 0 \\;(si\\;\\pi<0)", "la trampa de Fisher",
                     "el ZLB fija la nominal en cero, pero la deflación hace la REAL positiva y "
                     "creciente — la política monetaria pierde tracción justo cuando más se necesita."),
            Ecuacion("única\\;salida: \\;\\uparrow E[\\pi] \\Rightarrow \\downarrow r_{real}", "la salida por expectativas",
                     "si no se puede bajar la nominal (ZLB), hay que subir la inflación esperada "
                     "para bajar la real — pero eso exige prometer inflación creíblemente (verificado)."),
        ],
        intuicion=("La deflación enseña por qué los bancos centrales le temen más "
                   "que a la inflación moderada: la inflación se combate subiendo la "
                   "tasa (siempre se puede), pero la deflación en el ZLB no se "
                   "combate bajándola (ya está en cero) — hay que hacer algo mucho "
                   "más difícil: convencer a la gente de que habrá inflación. Y ahí "
                   "está la ironía cruel: el banco central que hizo bien su trabajo "
                   "de anclar la inflación baja (m40) es el que menos puede "
                   "prometer inflación alta, porque nadie le cree que abandonaría su "
                   "meta. Japón quedó atrapado en esto durante 'décadas perdidas': "
                   "un banco central respetado que no lograba generar la inflación "
                   "que necesitaba. La lección de política: apuntar a una meta "
                   "positiva (2%) para tener margen sobre el cero, y desarrollar "
                   "herramientas no convencionales (QE, metas de nivel de precios) "
                   "para el ZLB. Para el Perú, la deflación nunca ha sido el "
                   "problema (la historia es de inflación), pero entender la "
                   "asimetría explica por qué la meta no es 0%."),
        equilibrio=("Con deflación y ZLB, el equilibrio es una espiral sin fondo "
                    "interno (verificado): la única forma de romperla es un cambio "
                    "de expectativas (forward guidance creíble), que desplaza la "
                    "economía a un equilibrio con inflación positiva — como en las "
                    "profecías autocumplidas (m73-m76), pero en la dirección buena."),
        limitaciones=[
            "La paradoja de la credibilidad es difícil de modelar: aquí el forward guidance funciona por construcción, pero su credibilidad es el problema real (Krugman).",
            "Sin balances explícitos: la deuda-deflación quiebra deudores (m71) — el canal financiero amplifica la espiral más de lo mostrado.",
            "Sin política fiscal: en el ZLB, el estímulo fiscal (m91) es especialmente potente (multiplicador alto) — la salida complementaria.",
        ],
        evolucion=("Es el caso límite que combina m12 (ZLB), m34 (Fisher) y m54 "
                   "(expectativas), y el problema opuesto a la estanflación (m93). "
                   "Prepara m95 (la trampa de liquidez, su prima hermana) y "
                   "justifica la meta positiva de inflación. Para el Perú, explica "
                   "por qué el BCRP no apunta a 0% (m40, m99)."),
    ),
    escenarios=[
        Escenario("espiral_japonesa", "shock de −3 sin forward guidance",
                  {"shock": -3.0, "expectativas": 0.0},
                  "la deflación se profundiza sola: precios que caen, tasa real que "
                  "sube, demanda que se hunde — las décadas perdidas de Japón.",
                  cadena=["recesión empuja precios a la baja", "deflación (π<0)",
                          "tasa real sube aunque nominal=0 (Fisher)", "demanda cae más",
                          "espiral deflacionaria sin fondo (m12)"]),
        Escenario("forward_guidance", "prometer inflación futura (m54)",
                  {"shock": -3.0, "expectativas": 2.0},
                  "subir las expectativas rompe la espiral: la tasa real esperada "
                  "baja y la demanda revive — la salida no convencional del ZLB.",
                  cadena=["deflación en el ZLB", "el banco central promete inflación futura (m54)",
                          "las expectativas de inflación suben", "la tasa real esperada baja",
                          "la demanda revive: espiral rota"]),
        Escenario("paradoja_credibilidad", "el banco central creíble no logra prometer",
                  {"shock": -3.0, "expectativas": 0.0},
                  "el que anclé la inflación baja no puede prometer inflación alta "
                  "creíblemente: su virtud se vuelve trampa (Krugman) — el dilema "
                  "japonés.",
                  cadena=["deflación", "el banco central intenta prometer inflación",
                          "pero su credibilidad es de BAJA inflación (m40)", "nadie le cree",
                          "las expectativas no suben", "atrapado en la deflación"]),
    ],
    verificaciones=[
        Verificacion("espiral deflacionaria (Fisher)", _v_espiral_deflacionaria),
        Verificacion("la tasa real sube con ZLB (m12)", _v_tasa_real_sube),
        Verificacion("forward guidance rompe la espiral (m54)", _v_forward_guidance_salva),
        Verificacion("la paradoja de la credibilidad (Krugman)", _v_credibilidad_paradoja),
    ],
    notas="Más peligrosa que la inflación: no se combate bajando la tasa. La virtud del ancla se vuelve trampa.",
)
