"""simuladores/macro/modelos/nivel_08/m60_shock_fiscal.py — el shock fiscal: un multiplicador POR RÉGIMEN (nivel 8).

La misma pregunta (¿cuánto producto por sol de gasto?) respondida por CINCO
modelos del currículo, con parámetros compartidos — cada barra se recalcula
con la fórmula de su modelo fuente:
  m04 simple:      k = 1/(1−c1)
  m49 fijo:        1/(1−c1+m1)
  m10 IS-LM:       1/[(1−c1)+b·k_d/h]
  m56 NK+Taylor:   b_g = 1/[(1−ρ_g+σφ_x)+σ(φ_π−ρ_g)κ/(1−βρ_g)]  (impacto)
  m49 flexible:    0   (expulsión total vía apreciación)
La gran lección para m70 (evidencia empírica): "EL multiplicador" no existe
— existe uno por régimen monetario-cambiario, y el régimen se elige.

Procedencia: comparador construido con los modelos del propio laboratorio
(m04, m10, m49, m56) — decisión de diseño; fórmulas: las de cada fuente.
"""

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _multiplicadores(p):
    simple = 1 / (1 - p["c1"])
    mf_fijo = 1 / (1 - p["c1"] + p["m1"])
    islm = 1 / ((1 - p["c1"]) + p["b"] * p["k_d"] / p["h"])
    nk = 1 / ((1 - p["rho_g"] + p["sigma"] * p["phi_x"])
              + p["sigma"] * (p["phi_pi"] - p["rho_g"]) * p["kappa"] / (1 - p["beta"] * p["rho_g"]))
    mf_flex = 0.0
    return simple, mf_fijo, islm, nk, mf_flex


def _curvas(p):
    simple, mf_fijo, islm, nk, mf_flex = _multiplicadores(p)
    cats = ["simple\n(m04)", "MF fijo\n(m49)", "NK+Taylor\n(m56)",
            "IS-LM\n(m10)", "MF flexible\n(m49)"]
    vals = [simple, mf_fijo, nk, islm, mf_flex]
    cols = [config.GRIS, config.VERDE, config.AZUL2, config.AZUL, config.ROJO]
    return {"barras": (cats, vals, cols),
            "anotacion": ("la MISMA expansión de gasto, cinco respuestas:\n"
                          "el multiplicador ES el régimen — no un número\n"
                          "(cada barra se recalcula con la fórmula de su modelo)")}


def _resultados(p):
    simple, mf_fijo, islm, nk, mf_flex = _multiplicadores(p)
    return {"multiplicador simple (m04)": simple,
            "Mundell-Fleming fijo (m49)": mf_fijo,
            "NK con Taylor activo (m56)": nk,
            "IS-LM (m10)": islm,
            "Mundell-Fleming flexible (m49)": mf_flex}


def _ecuaciones_calibradas(p):
    simple, mf_fijo, islm, nk, mf_flex = _multiplicadores(p)
    return [f"$k = \\frac{{1}}{{1-{p['c1']:.2f}}} = {simple:.2f}$",
            f"$k^{{fijo}} = {mf_fijo:.2f}, \\;\\; k^{{ISLM}} = {islm:.2f}, "
            f"\\;\\; k^{{NK}} = {nk:.2f}, \\;\\; k^{{flex}} = 0$"]


_P0 = {"c1": 0.6, "m1": 0.15, "b": 20.0, "k_d": 0.5, "h": 10.0,
       "sigma": 1.0, "kappa": 0.2, "beta": 0.97, "phi_pi": 1.5,
       "phi_x": 0.5, "rho_g": 0.5}


def _v_formulas_fuente():
    simple, mf_fijo, islm, nk, mf_flex = _multiplicadores(_P0)
    ok = (abs(simple - 2.5) < 1e-12 and abs(mf_fijo - 1 / 0.55) < 1e-12
          and abs(islm - 1 / 1.4) < 1e-12 and abs(mf_flex) < 1e-12)
    return ok, ("cada barra reproduce exactamente la fórmula de su modelo fuente "
                f"(2.50, {mf_fijo:.3f}, {islm:.3f}, {nk:.3f}, 0): un comparador auditable")


def _v_orden():
    simple, mf_fijo, islm, nk, mf_flex = _multiplicadores(_P0)
    return simple > mf_fijo > max(nk, islm) >= min(nk, islm) > mf_flex, \
        ("el orden cuenta la historia del currículo: cada freno nuevo (r de m10, "
         "regla de m56, apreciación de m49) recorta el k del nivel 1")


def _v_nk_menor_que_uno():
    nk = _multiplicadores(_P0)[3]
    return nk < 1, (f"con Taylor activo el multiplicador NK = {nk:.2f} < 1: la regla se come "
                    "parte del impulso ANTES de que llegue — la política fiscal ya no actúa sola")


def _v_flexible_cero():
    return abs(_multiplicadores(_P0)[4]) < 1e-12, \
        "en flotación con movilidad perfecta el multiplicador es EXACTAMENTE 0 (m49): el caso extremo"


MODELO = Modelo(
    id="m60", nivel=8,
    nombre="Shock fiscal (un multiplicador por régimen)",
    xlabel="", ylabel="Multiplicador dY/dG",
    parametros=[
        Parametro("c1", _P0["c1"], 0.3, 0.85, 0.05, "Propensión a consumir c1", grupo="compartidos"),
        Parametro("m1", _P0["m1"], 0.05, 0.35, 0.05, "Propensión a importar m1", grupo="compartidos"),
        Parametro("phi_pi", _P0["phi_pi"], 1.1, 3, 0.1, "Respuesta de Taylor φ_π (NK)", grupo="regla NK"),
        Parametro("phi_x", _P0["phi_x"], 0.0, 1.5, 0.05, "Respuesta a la brecha φ_x (NK)", grupo="regla NK"),
        Parametro("rho_g", _P0["rho_g"], 0.0, 0.9, 0.05, "Persistencia del gasto ρ_g (NK)", grupo="regla NK"),
        Parametro("kappa", _P0["kappa"], 0.05, 0.6, 0.05, "Pendiente NKPC κ", grupo="regla NK"),
        Parametro("sigma", _P0["sigma"], 0.5, 2, 0.1, "Sensibilidad IS σ", grupo="regla NK"),
        Parametro("beta", _P0["beta"], 0.90, 0.99, 0.01, "Descuento β", grupo="regla NK"),
        Parametro("b", _P0["b"], 8, 35, 1, "Sensibilidad de I a r (IS-LM)", grupo="compartidos"),
        Parametro("k_d", _P0["k_d"], 0.25, 0.9, 0.05, "Demanda de dinero por Y (IS-LM)", grupo="compartidos"),
        Parametro("h", _P0["h"], 5, 22, 1, "Demanda de dinero por r (IS-LM)", grupo="compartidos"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto vale un sol de gasto público? Depende — y el 'depende' tiene cinco fórmulas exactas.",
        variables=[("dY/dG", "el multiplicador — la variable dependiente del REGIMEN"),
                   ("régimen", "monetario (regla, M fija) y cambiario (fijo, flexible)"),
                   ("las 5 barras", "m04, m49-fijo, m56, m10, m49-flex: el currículo compitiendo")],
        derivacion=["m04: \\;k = \\tfrac{1}{1-c_1} \\;(nada\\;frena)",
                    "m10: \\;\\tfrac{1}{(1-c_1)+bk_d/h} \\;(la\\;tasa\\;frena)",
                    "m56: \\;b_g = \\tfrac{1}{(1-\\rho_g+\\sigma\\phi_x)+\\sigma(\\phi_\\pi-\\rho_g)\\kappa/(1-\\beta\\rho_g)} \\;(la\\;REGLA\\;frena)",
                    "m49: \\;\\tfrac{1}{1-c_1+m_1}\\;(fijo) \\;\\;vs\\;\\; 0\\;(flexible)"],
        contexto=("Cada debate fiscal — del New Deal a las respuestas al COVID — "
                  "gira sobre un número: el multiplicador. Este modelo muestra por "
                  "qué el debate nunca se cierra: el número NO es un parámetro de "
                  "la naturaleza sino una propiedad del RÉGIMEN. La misma expansión "
                  "rinde 2.5 si nada responde (m04), 1.8 con paridad fija que obliga "
                  "al banco central a acomodar (m49), 0.7 si la tasa (m10) o la "
                  "regla (m56) frenan, y CERO en flotación con capital libre (m49). "
                  "La evidencia empírica moderna (m70) confirma la lógica: los "
                  "multiplicadores medidos dependen del régimen — grandes en el "
                  "ZLB (la regla dormida), pequeños con bancos centrales activos."),
        autores=("Comparador construido sobre los modelos del laboratorio (m04, "
                 "m10, m49, m56); la lectura régimen-dependiente de la evidencia: "
                 "literatura post-2008 (Ramey; Ilzetzki-Mendoza-Végh — menciones)."),
        supuestos=[
            "Parámetros COMPARTIDOS entre modelos donde aplica: las diferencias entre barras son de RÉGIMEN, no de calibración.",
            "Multiplicadores de IMPACTO (el NK usa la solución AR(1) de m56 con shock de demanda).",
            "Cada fórmula hereda los supuestos de su fuente (precios fijos en m04/m10/m49; racionales+Calvo en m56).",
        ],
        ecuaciones=[
            Ecuacion("k^{simple} > k^{fijo} > k^{NK} \\approx k^{ISLM} > k^{flex} = 0",
                     "la escalera de frenos",
                     "cada modelo añade un mecanismo que devuelve parte del impulso: ahorro (m04), "
                     "importaciones y tasa (m10/m49), la regla del banco central (m56), y la "
                     "apreciación cambiaria que lo devuelve TODO (m49-flex)."),
        ],
        intuicion=("Preguntar '¿cuál es EL multiplicador?' es como preguntar cuánto "
                   "corre UN auto: depende del terreno. La pregunta bien hecha — la "
                   "de m70 y del nivel 12 con datos del MEF — es '¿en qué régimen "
                   "está mi economía HOY?': ¿el BCRP acomodará o responderá (m56)?, "
                   "¿el sol flota (m49)?, ¿hay capacidad ociosa (m04)? El Perú "
                   "flotante con metas vive normalmente entre las barras NK e "
                   "IS-LM — lejos del 2.5 de los discursos."),
        equilibrio=("No hay equilibrio propio: es un meta-modelo que consulta los "
                    "equilibrios de otros cuatro. Su verificación es de "
                    "CONSISTENCIA: cada barra reproduce exactamente la fórmula "
                    "fuente con los parámetros compartidos."),
        limitaciones=[
            "Multiplicadores de impacto, no acumulados: la dinámica completa (rezagos fiscales, reversiones) los cambia (m68-m70).",
            "El financiamiento importa y aquí no está: deuda vs impuestos vs emisión (nivel 9, m67).",
            "El ZLB — donde los multiplicadores CRECEN porque la regla duerme (m12+m56) — queda como lectura: es EL caso empírico post-2008 (m70).",
        ],
        evolucion=("Cierra la trilogía de shocks del nivel 8 (tecnológico m58, "
                   "monetario m59, fiscal m60) y deja armada la pregunta del nivel "
                   "9: si el multiplicador depende del régimen, ¿y la SOSTENIBILIDAD "
                   "del gasto? (m62-m70, con m70 como el juicio empírico)."),
    ),
    escenarios=[
        Escenario("regla_dura", "el banco central NK endurece: φ_π = 2.5",
                  {"phi_pi": 2.5},
                  "el multiplicador NK cae: cuanto más halcón el banco central, "
                  "menos rinde el gasto — la política fiscal ya no decide sola.",
                  cadena=["↑G", "la brecha y π suben", "la regla dicta más tasa",
                          "la IS de m54 descuenta la senda entera", "el impulso llega recortado"]),
        Escenario("economia_cerrada_keynesiana", "sin importaciones: m1 = 0.05",
                  {"m1": 0.05},
                  "el MF-fijo casi alcanza al simple: la fuga externa era la única "
                  "diferencia — el multiplicador de economía cerrada es una cota superior.",
                  cadena=["↓m1", "menos filtración importadora",
                          "k fijo → k simple", "las economías cerradas multiplican más"]),
        Escenario("gasto_persistente", "el impulso NK dura: ρ_g = 0.8",
                  {"rho_g": 0.8},
                  "el multiplicador NK de impacto cambia con la persistencia "
                  "anunciada: en el mundo racional, CUÁNTO dura el gasto importa "
                  "tanto como cuánto es.",
                  cadena=["gasto anunciado como persistente", "la IS descuenta más períodos",
                          "pero la regla también responde más", "el neto lo decide φ_π vs ρ_g"]),
    ],
    verificaciones=[
        Verificacion("cada barra = fórmula exacta de su modelo fuente", _v_formulas_fuente),
        Verificacion("la escalera de frenos ordena el currículo", _v_orden),
        Verificacion("con Taylor activo, el NK < 1", _v_nk_menor_que_uno),
        Verificacion("flotación + movilidad ⇒ multiplicador 0 exacto", _v_flexible_cero),
    ],
    notas="No existe EL multiplicador: existe uno por régimen — y el régimen se elige. m70 traerá el juicio empírico.",
)
