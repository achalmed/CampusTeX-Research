"""simuladores/macro/modelos/nivel_07/m49_mundell_fleming.py — modelo Mundell-Fleming (nivel 7, ANCLA).

El IS-LM de la economía abierta pequeña con movilidad perfecta (r = r*):
  IS abierta:  Y = c0 + c1(Y−T) + I0 − b·r + G + XN,  XN = x0 + v·E − m1·Y
  LM:          M/P = k·Y − h·r
  movilidad:   r = r*   (la UIP de m48 sin prima y sin expectativas)

RÉGIMEN FLEXIBLE (E ajusta, M manda):   Y = (M/P + h·r*)/k
  → la política FISCAL no mueve Y (¡expulsión TOTAL vía apreciación!)
  → la política MONETARIA es superpotente (dY/dM = 1/k)
RÉGIMEN FIJO (E dado, M endógena):      Y = A(G, Ē)/(1−c1+m1)
  → la política FISCAL es potente (sin freno de r NI de E)
  → la política MONETARIA es IMPOSIBLE (la M vuelve sola defendiendo Ē)
La calibración hace coincidir la base de ambos regímenes (Y=660, E=100,
M=300): los experimentos parten del MISMO mundo.

Procedencia: Mundell (1963) y Fleming (1962) — menciones; Nobel a Mundell
1999. Formulación de manual (conocimiento general); calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _s(p):
    return 1 - p["c1"] + p["m1"]


def _autonomo(p, G=None, E=None):
    """Gasto autónomo con r = r* incluido y XN(E) dentro."""
    G = p["G"] if G is None else G
    E = p["E_fijo"] if E is None else E
    return (p["c0"] - p["c1"] * p["T_imp"] + p["I0"] - p["b"] * p["r_star"]
            + G + p["x0"] + p["v"] * E)


def _equilibrio(p):
    """(Y, E, M_efectiva) según el régimen."""
    if p["regimen"] >= 0.5:                       # FLEXIBLE: M manda, E ajusta
        Y = (p["M"] + p["h"] * p["r_star"]) / p["k"]
        E = (_s(p) * Y - _autonomo(p, E=0.0)) / p["v"]
        return Y, E, p["M"]
    Y = _autonomo(p) / _s(p)                      # FIJO: Ē manda, M endógena
    M_end = p["k"] * Y - p["h"] * p["r_star"]
    return Y, p["E_fijo"], M_end


def _curvas(p):
    Y_eq, E, M_ef = _equilibrio(p)
    Y = np.linspace(400, 900, 300)
    A_sin_rs = _autonomo(p, E=E) + p["b"] * p["r_star"]   # autónomo sin el −b·r*
    r_is = (A_sin_rs - _s(p) * Y) / p["b"]
    r_lm = (p["k"] * Y - M_ef) / p["h"]
    reg = "FLEXIBLE" if p["regimen"] >= 0.5 else "FIJO"
    return {"lineas": {"IS abierta (con $E$ del régimen)": (Y, r_is, config.AZUL2),
                       "LM (con $M$ del régimen)": (Y, r_lm, config.ROJO),
                       "movilidad perfecta: $r = r^*$": (Y, np.full_like(Y, p["r_star"]), config.GRIS)},
            "equilibrio": (Y_eq, p["r_star"]),
            "anotacion": (f"régimen {reg}\n"
                          f"$Y = {Y_eq:,.1f}$,  $E = {E:,.1f}$,  $M = {M_ef:,.1f}$\n"
                          + ("la IS se recoloca sola vía $E$" if p["regimen"] >= 0.5
                             else "la LM se recoloca sola vía $M$"))}


def _resultados(p):
    Y, E, M_ef = _equilibrio(p)
    xn = p["x0"] + p["v"] * E - p["m1"] * Y
    dG = 25.0
    p2 = dict(p); p2["G"] = p["G"] + dG
    dYdG = (_equilibrio(p2)[0] - Y) / dG
    return {"producto Y": Y, "tipo de cambio E (índice)": E,
            "dinero efectivo M": M_ef, "tasa r = r*": p["r_star"],
            "exportaciones netas XN": xn,
            "multiplicador fiscal del régimen": dYdG}


def _ecuaciones_calibradas(p):
    Y, E, M_ef = _equilibrio(p)
    return [f"$r = r^* = {p['r_star']:.1f}$",
            f"$XN = {p['x0']:.0f} + {p['v']:.1f}\\,E - {p['m1']:.2f}\\,Y$",
            (f"$Y = (M + h\\,r^*)/k = {Y:,.1f}$" if p["regimen"] >= 0.5
             else f"$Y = A(\\bar{{E}})/{_s(p):.2f} = {Y:,.1f}$"),
            f"$E = {E:,.1f}, \\quad M = {M_ef:,.1f}$"]


_P0 = {"regimen": 1.0, "G": 200.0, "M": 300.0, "r_star": 3.0, "E_fijo": 100.0,
       "c0": 100.0, "c1": 0.6, "T_imp": 100.0, "I0": 150.0, "b": 20.0,
       "k": 0.5, "h": 10.0, "x0": -167.0, "v": 2.0, "m1": 0.15}


def _v_fiscal_impotente_flexible():
    Y0 = _equilibrio(_P0)[0]
    Y1, E1, _ = _equilibrio(dict(_P0, G=250.0))
    ok = abs(Y1 - Y0) < 1e-9 and E1 < 100.0
    return ok, (f"con cambio FLEXIBLE, ΔG=50 deja Y EXACTAMENTE igual ({Y0:,.0f}) y aprecia "
                f"E de 100 a {E1:,.1f}: la expulsión ya no es parcial (m11) — es TOTAL, vía XN")


def _v_monetaria_potente_flexible():
    Y0 = _equilibrio(_P0)[0]
    Y1, E1, _ = _equilibrio(dict(_P0, M=360.0))
    ok = abs((Y1 - Y0) / 60.0 - 1 / _P0["k"]) < 1e-12 and E1 > 100.0
    return ok, (f"dY/dM = 1/k = {1 / _P0['k']:.1f} exacto: la monetaria es superpotente en "
                f"flexible — Y {Y0:,.0f}→{Y1:,.0f} con E depreciándose a {E1:,.1f}")


def _v_fiscal_potente_fijo():
    p = dict(_P0, regimen=0.0)
    Y0 = _equilibrio(p)[0]
    Y1 = _equilibrio(dict(p, G=250.0))[0]
    mult = (Y1 - Y0) / 50.0
    return abs(mult - 1 / _s(_P0)) < 1e-12, \
        (f"con cambio FIJO el multiplicador fiscal es 1/(1−c1+m1) = {1 / _s(_P0):.3f} exacto: "
         "sin freno de r (movilidad) ni de E (fijo), la fiscal manda")


def _v_monetaria_imposible_fijo():
    p = dict(_P0, regimen=0.0)
    Y0, _, M0 = _equilibrio(p)
    Y1, _, M1 = _equilibrio(dict(p, M=360.0))
    ok = abs(Y1 - Y0) < 1e-9 and abs(M1 - M0) < 1e-9
    return ok, (f"con cambio FIJO, 'subir M a 360' no hace nada: la M efectiva vuelve a "
                f"{M0:,.0f} defendiendo Ē — la autonomía monetaria NO EXISTE (trilema, m50)")


def _v_base_coherente():
    Yf, Ef, Mf = _equilibrio(_P0)
    Yj, Ej, Mj = _equilibrio(dict(_P0, regimen=0.0))
    ok = abs(Yf - Yj) < 1e-9 and abs(Ef - Ej) < 1e-9 and abs(Mf - Mj) < 1e-9
    return ok, (f"la base es el MISMO mundo en ambos regímenes (Y={Yf:,.0f}, E={Ef:,.0f}, "
                f"M={Mf:,.0f}): los experimentos comparan políticas, no calibraciones")


MODELO = Modelo(
    id="m49", nivel=7,
    nombre="Modelo Mundell-Fleming",
    xlabel="Producto ($Y$)", ylabel="Tasa de interés ($r$)",
    parametros=[
        Parametro("regimen", _P0["regimen"], 0, 1, 1, "Régimen (1 flexible, 0 fijo)",
                  grupo="régimen", definicion="LA elección: quién ajusta, ¿E o M?"),
        Parametro("G", _P0["G"], 100, 320, 10, "Gasto público G", grupo="políticas"),
        Parametro("M", _P0["M"], 200, 420, 10, "Dinero M (intento, si fijo)", grupo="políticas"),
        Parametro("r_star", _P0["r_star"], 1, 6, 0.25, "Tasa mundial r*", grupo="mundo",
                  definicion="la FED de m48: exógena para el país pequeño"),
        Parametro("E_fijo", _P0["E_fijo"], 70, 130, 5, "Paridad Ē (si fijo)", grupo="régimen"),
        Parametro("v", _P0["v"], 0.5, 4, 0.25, "Sensibilidad de XN a E (v)", grupo="estructura"),
        Parametro("m1", _P0["m1"], 0.05, 0.35, 0.05, "Propensión a importar m1", grupo="estructura"),
        Parametro("c1", _P0["c1"], 0.3, 0.85, 0.05, "Propensión a consumir c1", grupo="estructura"),
        Parametro("b", _P0["b"], 8, 35, 1, "Sensibilidad de I a r (b)", grupo="estructura"),
        Parametro("k", _P0["k"], 0.25, 0.9, 0.05, "Demanda de dinero por Y (k)", grupo="estructura"),
        Parametro("h", _P0["h"], 5, 22, 1, "Demanda de dinero por r (h)", grupo="estructura"),
        Parametro("c0", _P0["c0"], 60, 180, 10, "Consumo autónomo c0", grupo="estructura"),
        Parametro("I0", _P0["I0"], 80, 260, 10, "Inversión autónoma I0", grupo="estructura"),
        Parametro("T_imp", _P0["T_imp"], 20, 250, 10, "Impuestos T", grupo="estructura"),
        Parametro("x0", _P0["x0"], -220, -100, 5, "XN autónoma x0", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="En una economía abierta al capital, ¿qué política funciona — y por qué la respuesta se INVIERTE con el régimen cambiario?",
        variables=[("Y", "producto — endógeno"),
                   ("E", "tipo de cambio — endógeno en flexible, ancla en fijo"),
                   ("M", "dinero — instrumento en flexible, ENDÓGENO en fijo"),
                   ("r = r*", "la tasa — ya no es tuya: la fija el mundo (m48)")],
        derivacion=["movilidad\\;perfecta: \\;r = r^* \\;(UIP\\;sin\\;prima)",
                    "flexible: \\;LM\\;en\\;r^* \\Rightarrow Y = \\frac{M/P + h\\,r^*}{k};\\;\\;E\\;ajusta\\;la\\;IS",
                    "fijo: \\;IS\\;en\\;(\\bar{E}, r^*) \\Rightarrow Y = \\frac{A(G,\\bar{E})}{1-c_1+m_1};\\;\\;M\\;endógena"],
        contexto=("A inicios de los 60, con Bretton Woods vivo y el capital "
                  "empezando a moverse, Mundell y Fleming abrieron el IS-LM al "
                  "mundo y encontraron un resultado que reordenó la política "
                  "económica: la eficacia de CADA política depende del régimen "
                  "cambiario. Lo que la fiscal gana con cambio fijo lo pierde con "
                  "flexible (la apreciación se la come entera), y lo que la "
                  "monetaria no puede hacer con cambio fijo (nada) lo hace con "
                  "creces flotando. Sesenta años después sigue siendo la primera "
                  "pregunta ante cualquier país: ¿quién ajusta aquí, E o M?"),
        autores=("Mundell (1963) y Fleming (1962), independientes — menciones; "
                 "Nobel a Mundell (1999). Es el IS-LM (m10) + la UIP (m48) + la "
                 "XN(E) de m45-m46."),
        supuestos=[
            "País PEQUEÑO con movilidad PERFECTA: r = r* siempre (sin prima ni expectativas cambiarias — m48 completo las añadiría).",
            "Precios fijos (corto plazo estricto): el RER se mueve 1:1 con E (m46 sin passthrough).",
            "En fijo, el banco central compra/vende divisas SIN esterilizar: M es endógena por definición del régimen.",
            "XN lineal en E e Y (v y m1 constantes: Marshall-Lerner cumplida — mención).",
        ],
        ecuaciones=[
            Ecuacion("Y^{flex} = \\frac{M/P + h\\,r^*}{k}", "flexible: la LM manda",
                     "con r clavada en r*, la LM sola determina Y: la fiscal no aparece en la "
                     "fórmula — TODO impulso de gasto se filtra en apreciación que mata XN."),
            Ecuacion("Y^{fijo} = \\frac{c_0 - c_1 T + I_0 - b r^* + G + x_0 + v\\bar{E}}{1-c_1+m_1}",
                     "fijo: la IS manda",
                     "con Ē y r* dados, la IS sola determina Y: la M no aparece — el banco "
                     "central la pierde defendiendo la paridad."),
            Ecuacion("XN = x_0 + v\\,E - m_1\\,Y", "el canal cambiario",
                     "la novedad respecto de m10: la demanda tiene una puerta al mundo, y esa "
                     "puerta la abre o la cierra E."),
        ],
        intuicion=("La movilidad perfecta convierte a r en un espejo de r*: ya no "
                   "hay tasa propia que subir o bajar. Queda UNA válvula de ajuste "
                   "— el tipo de cambio o el dinero — y el régimen decide cuál está "
                   "soldada. Flexible: E libre absorbe los shocks fiscales "
                   "(apreciación = expulsión total) y deja a M todo el poder. Fijo: "
                   "E soldado convierte a M en rehén de la paridad y deja a G todo "
                   "el poder. No hay régimen 'bueno': hay una elección de qué "
                   "política conservar — el trilema (m50) en versión operativa."),
        equilibrio=("(Y, r*, E, M) coherentes por régimen; la base coincide en "
                    "ambos (verificado): los cuatro teoremas de eficacia — fiscal "
                    "nula/potente, monetaria potente/imposible — están verificados "
                    "como igualdades exactas, no aproximaciones."),
        limitaciones=[
            "Movilidad perfecta sin prima: con riesgo país (m48) la r local se despega de r* y los resultados se suavizan.",
            "Precios fijos: a mediano plazo el passthrough (m46) erosiona la ganancia real de las depreciaciones.",
            "Expectativas cambiarias estáticas: con Ee endógena aparecen el overshooting (Dornbusch, mención) y las crisis autocumplidas (m74).",
            "Fijo perfectamente creíble: si el mercado duda, el modelo correcto es el de crisis (m74), no este.",
        ],
        evolucion=("Es la síntesis del nivel: m43-m44 (cuentas), m45-m46 (precios) "
                   "y m48 (arbitraje) caben en un solo aparato de política. m50 lo "
                   "condensa en el trilema; el nivel 11 lo usará para la FED (m86), "
                   "la devaluación (m84) y la salida de capitales (m87); y el Perú "
                   "de flotación administrada con metas es exactamente la esquina "
                   "flexible+autonomía del trilema (m110-m111)."),
    ),
    escenarios=[
        Escenario("fiscal_en_flexible", "ΔG=+50 con cambio flexible",
                  {"G": 250.0, "regimen": 1.0},
                  "Y no se mueve NI UN CENTAVO: la entrada de capital aprecia E de "
                  "100 a 75 y las XN caen exactamente lo que G subió — la expulsión "
                  "total que m11 solo insinuaba.",
                  cadena=["↑G", "presión sobre r", "entra capital (r no puede subir de r*)",
                          "E se aprecia", "↓XN exactamente = ↑G", "ΔY = 0: expulsión TOTAL"]),
        Escenario("monetaria_en_flexible", "ΔM=+60 con cambio flexible",
                  {"M": 360.0, "regimen": 1.0},
                  "Y salta 120 (dY/dM = 1/k): el dinero presiona r a la baja, sale "
                  "capital, E se deprecia a 133 y las XN rematan el estímulo — la "
                  "política reina del régimen flotante.",
                  cadena=["↑M", "presión a la baja sobre r", "sale capital",
                          "E se deprecia", "↑XN refuerza", "ΔY = ΔM/k: superpotente"]),
        Escenario("fiscal_en_fijo", "ΔG=+50 con cambio fijo",
                  {"G": 250.0, "regimen": 0.0},
                  "Y sube 91 (multiplicador 1.82, el MAYOR del currículo hasta "
                  "aquí): el banco central, defendiendo Ē, emite la M que el "
                  "impulso necesita — el acomodo monetario de m11 es automático.",
                  cadena=["↑G", "presión sobre r y sobre E (entraría capital)",
                          "el BC compra divisas para sostener Ē", "M endógena crece",
                          "ni r ni E frenan", "multiplicador pleno abierto 1/(1−c1+m1)"]),
        Escenario("monetaria_en_fijo", "intento de ΔM=+60 con cambio fijo",
                  {"M": 360.0, "regimen": 0.0},
                  "NADA cambia: el dinero extra presiona E, el BC lo recompra "
                  "vendiendo reservas y M vuelve a 300 — la autonomía monetaria "
                  "murió con la paridad (m50).",
                  cadena=["↑M (intento)", "presión de depreciación sobre Ē",
                          "el BC vende divisas y recompra su moneda", "M regresa sola",
                          "ΔY = 0: el trilema cobra (m50)"]),
    ],
    verificaciones=[
        Verificacion("flexible: fiscal impotente (ΔY=0 exacto)", _v_fiscal_impotente_flexible),
        Verificacion("flexible: monetaria dY/dM = 1/k exacto", _v_monetaria_potente_flexible),
        Verificacion("fijo: multiplicador fiscal 1/(1−c1+m1) exacto", _v_fiscal_potente_fijo),
        Verificacion("fijo: monetaria imposible (M vuelve sola)", _v_monetaria_imposible_fijo),
        Verificacion("base idéntica entre regímenes", _v_base_coherente),
    ],
    notas="La pregunta previa a toda política en economía abierta: ¿quién ajusta aquí — E o M?",
)
