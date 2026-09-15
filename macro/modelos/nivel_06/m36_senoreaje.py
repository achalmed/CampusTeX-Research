"""simuladores/macro/modelos/nivel_06/m36_senoreaje.py — señoreaje: la curva de Laffer de la inflación (nivel 6).

El gobierno que emite recauda un "impuesto inflación" sobre los saldos reales:
  s(π) = (π/100) · L(π),   con demanda de dinero tipo Cagan  L(π) = a·e^{−bπ}
La base del impuesto HUYE cuando la tasa sube (la gente escapa del dinero):
s(π) tiene forma de Laffer con máximo en π* = 1/b. Más allá del pico, MÁS
inflación recauda MENOS — la aritmética de toda hiperinflación, incluida la
peruana de 1988-1990 (episodio histórico; los datos exactos, vía BCRP en el
nivel 12).

Procedencia: demanda de Cagan (1956, mención); análisis del impuesto
inflación: Bailey/Friedman (menciones) — conocimiento general. Calibración
didáctica (decisión de diseño).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _s(pi, p):
    return (pi / 100) * p["a"] * np.exp(-p["b"] * pi)


def _curvas(p):
    pi = np.linspace(0, 160, 300)
    pico = 1 / p["b"]
    return {"lineas": {"señoreaje $s(\\pi) = \\frac{\\pi}{100}\\,a\\,e^{-b\\pi}$": (pi, _s(pi, p), config.AZUL2)},
            "equilibrio": (p["pi"], float(_s(p["pi"], p))),
            "puntos": [(pico, float(_s(pico, p)), f"pico: $\\pi = 1/b = {pico:.0f}\\%$")],
            "anotacion": (f"tu inflación: $\\pi = {p['pi']:.0f}\\%$ → "
                          f"$s = {float(_s(p['pi'], p)):.2f}\\%$ del PIB\n"
                          f"máximo posible: {float(_s(pico, p)):.2f}% del PIB\n"
                          "más allá del pico, MÁS inflación recauda MENOS")}


def _resultados(p):
    pico = 1 / p["b"]
    return {"señoreaje en tu π (% del PIB)": float(_s(p["pi"], p)),
            "π del máximo (= 1/b, %)": pico,
            "señoreaje máximo (% del PIB)": float(_s(pico, p)),
            "saldos reales L(π) (% del PIB)": float(p["a"] * np.exp(-p["b"] * p["pi"])),
            "saldos con π=0 (% del PIB)": p["a"]}


def _ecuaciones_calibradas(p):
    return [f"$L(\\pi) = {p['a']:.0f}\\,e^{{-{p['b']:.3f}\\,\\pi}}$",
            f"$s({p['pi']:.0f}) = {p['pi'] / 100:.2f} \\times {float(p['a'] * np.exp(-p['b'] * p['pi'])):.1f} "
            f"= {float(_s(p['pi'], p)):.2f}\\%\\;PIB$",
            f"$\\pi^{{max}} = 1/b = {1 / p['b']:.0f}\\%$"]


_P0 = {"a": 15.0, "b": 0.025, "pi": 30.0}


def _v_laffer():
    pi = np.linspace(0.1, 200, 8001)
    s = _s(pi, _P0)
    pico_num = float(pi[int(np.argmax(s))])
    return abs(pico_num - 1 / _P0["b"]) < 0.1, \
        f"el máximo numérico cae en π = {pico_num:.1f}% = 1/b: la Laffer del impuesto inflación"


def _v_mas_alla_del_pico():
    s40, s120 = float(_s(40, _P0)), float(_s(120, _P0))
    return s120 < s40, (f"con π=120% se recauda {s120:.2f}% del PIB, MENOS que con π=40% "
                        f"({s40:.2f}%): la base huye más rápido de lo que la tasa sube")


def _v_extremos():
    return abs(float(_s(0, _P0))) < 1e-12 and float(_s(1000, _P0)) < 0.01, \
        "sin inflación no hay impuesto; con hiperinflación tampoco (nadie sostiene dinero)"


def _v_base_huye():
    L30, L90 = 15 * np.exp(-0.025 * 30), 15 * np.exp(-0.025 * 90)
    return L90 < L30 / 2, (f"triplicar π (30→90%) reduce los saldos reales de {L30:.1f}% a "
                           f"{L90:.1f}% del PIB: la fuga del dinero es la esencia del fenómeno")


MODELO = Modelo(
    id="m36", nivel=6,
    nombre="Señoreaje (impuesto inflación)",
    xlabel="Inflación $\\pi$ (%)", ylabel="Señoreaje (% del PIB)",
    parametros=[
        Parametro("pi", _P0["pi"], 0, 150, 5, "Inflación elegida π (%)", grupo="política",
                  definicion="la 'tasa' del impuesto inflación"),
        Parametro("a", _P0["a"], 5, 30, 1, "Saldos reales con π=0 (% del PIB)", grupo="estructura",
                  definicion="cuánto dinero sostiene la economía sin inflación"),
        Parametro("b", _P0["b"], 0.005, 0.06, 0.005, "Semielasticidad b (fuga)", grupo="estructura",
                  definicion="cuán rápido huye la gente del dinero al subir π"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto puede financiarse un gobierno imprimiendo — y por qué toda hiperinflación termina recaudando casi nada?",
        variables=[("s(π)", "recaudación por emisión — la Laffer del dinero"),
                   ("L(π)", "saldos reales — la BASE del impuesto, que huye"),
                   ("π", "la tasa del impuesto — elegida por el fisco desesperado")],
        derivacion=["s = \\frac{\\Delta M}{P} = g_M \\cdot \\frac{M}{P} \\;\\;(en\\;EE:\\;g_M = \\pi)",
                    "L(\\pi) = a\\,e^{-b\\pi} \\;\\;(Cagan)",
                    "\\frac{ds}{d\\pi} = 0 \\;\\Rightarrow\\; \\pi^{max} = \\frac{1}{b}"],
        contexto=("Cuando un gobierno no puede cobrar impuestos ni endeudarse, queda "
                  "la imprenta: emitir es transferir recursos de quienes sostienen "
                  "dinero hacia el fisco. Cagan (1956) estudió las grandes "
                  "hiperinflaciones y encontró la mecánica: la demanda de dinero cae "
                  "exponencialmente con la inflación esperada, así que el impuesto "
                  "tiene curva de Laffer. Los finales de los 80 en América Latina — "
                  "el Perú de 1988-1990 entre ellos — recorrieron la curva hasta el "
                  "lado malo: inflaciones astronómicas recaudando migajas."),
        autores=("Cagan (1956, The Monetary Dynamics of Hyperinflation — mención); "
                 "el 'impuesto inflación' como concepto: Bailey (1956), Friedman — "
                 "menciones."),
        supuestos=["Demanda de Cagan: L(π)=a·e^{−bπ} con expectativas cumplidas (π esperada = efectiva).",
                   "Estado estacionario: gM = π (todo el crecimiento del dinero es inflación, m34 con gY=0).",
                   "El fisco es el ÚNICO motivo de la emisión: este modelo es teoría fiscal de la inflación."],
        ecuaciones=[
            Ecuacion("s(\\pi) = \\frac{\\pi}{100}\\,a\\,e^{-b\\pi}", "la Laffer del dinero",
                     "tasa (π) por base (L): la base se encoge exponencialmente — a diferencia de "
                     "casi cualquier otro impuesto, aquí la fuga es comprarse cualquier cosa."),
            Ecuacion("\\pi^{max} = \\frac{1}{b}", "el pico",
                     "pasada esa inflación, cada punto adicional DESTRUYE recaudación: los últimos "
                     "meses de toda hiperinflación viven en esa pendiente."),
        ],
        intuicion=("El impuesto inflación es el único que se recauda sin SUNAT: basta "
                   "imprimir. Pero su base — la disposición a sostener dinero — es la "
                   "más volátil de todas: al primer indicio la gente huye a bienes y "
                   "dólares. Por eso el señoreaje sostenible es pequeño (2-3% del PIB "
                   "en el pico) y por eso los finales hiperinflacionarios son "
                   "espirales: recaudar lo mismo exige acelerar, acelerar encoge la "
                   "base, y así hasta el colapso o la reforma."),
        equilibrio=("Cada π define un EE con s(π); el máximo interior π*=1/b "
                    "(verificado numéricamente). La dinámica inestable más allá del "
                    "pico — perseguir recaudación acelerando — es la espiral "
                    "hiperinflacionaria."),
        limitaciones=[
            "Estático entre EEs: la transición (expectativas persiguiendo a la emisión) es lo que vuelve EXPLOSIVO el lado malo — Cagan la modela, aquí es lectura.",
            "b no es constante en la vida real: la propia hiperinflación acelera la fuga (dolarización) y encoge a — el Perú quedó dolarizado por décadas (mención).",
            "La salida no está en el modelo: reforma fiscal + prohibición de financiamiento monetario (la Constitución de 1993 se la prohíbe al BCRP — mención) + ancla nueva (m40).",
        ],
        evolucion=("Es el puente dinero-fisco del currículo: adelanta la restricción "
                   "presupuestaria del nivel 9 (m62-m63: cuando la deuda no cierra, "
                   "aparece la imprenta) y explica el DISEÑO institucional del nivel: "
                   "independencia del banco central y metas (m40-m41) existen para "
                   "clausurar esta máquina."),
    ),
    escenarios=[
        Escenario("financiamiento_moderado", "π = 10%: el impuesto discreto",
                  {"pi": 10.0},
                  "recauda ~1.2% del PIB: tentadoramente 'barato' — así empiezan "
                  "todas las historias que terminan en el pico.",
                  cadena=["déficit sin financiamiento", "emisión moderada", "π = 10%",
                          "s ≈ 1.2% del PIB", "la tentación queda sembrada"]),
        Escenario("en_el_pico", "π = 40% = 1/b: el máximo teórico",
                  {"pi": 40.0},
                  "≈2.2% del PIB, el TECHO del impuesto inflación: todo lo que un "
                  "fisco puede extraer de la imprenta en régimen sostenido.",
                  cadena=["π = 1/b", "tasa y fuga se equilibran al margen",
                          "s máximo ≈ 2.2% PIB", "de aquí en adelante todo es pérdida"]),
        Escenario("lado_malo_de_la_laffer", "π = 120%: la zona hiperinflacionaria",
                  {"pi": 120.0},
                  "recauda MENOS que con 40%: la base huyó — la aritmética del Perú "
                  "de 1989, cuando ni la inflación de tres dígitos cerraba la caja.",
                  cadena=["π ≫ 1/b", "fuga masiva del dinero (dolarización)",
                          "la base se evapora", "s cae pese a π creciente",
                          "espiral: acelerar para recaudar lo mismo"]),
        Escenario("fuga_facil", "economía ya dolarizada: b sube a 0.045",
                  {"b": 0.045},
                  "el pico baja a π=22% y el techo de recaudación se hunde: la "
                  "memoria inflacionaria (dolarización) desarma la imprenta para siempre.",
                  cadena=["experiencia hiperinflacionaria previa", "↑b (fuga fácil al dólar)",
                          "pico más bajo y más pobre", "el impuesto inflación queda inutilizado"]),
    ],
    verificaciones=[
        Verificacion("pico numérico = 1/b (Laffer verificada)", _v_laffer),
        Verificacion("más allá del pico: más π, menos recaudación", _v_mas_alla_del_pico),
        Verificacion("extremos: s(0)=0 y s(∞)→0", _v_extremos),
        Verificacion("la base huye exponencialmente", _v_base_huye),
    ],
    notas="El único impuesto sin recaudador — y con la base más fugitiva de todas. Perú 1988-90 vive en esta curva.",
)
