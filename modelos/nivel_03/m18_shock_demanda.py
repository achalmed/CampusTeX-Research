# m18_shock_demanda.py — shock de demanda agregada en AD-SRAS (nivel 3).
#
# Versión mínima (lineal) del aparato precio-producto, como ANTICIPO del nivel 4:
#   AD:    Y = A + dA − b·P          (la deriva desde IS-LM llega en m20)
#   SRAS:  P = Pe + λ·(Y − Y*)
# Equilibrio:  Y_eq = [A + dA − b·Pe + b·λ·Y*] / (1 + b·λ)
# Firma del shock de DEMANDA: P e Y se mueven en la MISMA dirección.
# Empleo: lectura vía Okun (m15), Δu ≈ −β_okun · %ΔY.
#
# Procedencia: AD-AS de manual (conocimiento general); calibración: decisión
# de diseño didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _eq(p, dA):
    Y = (p["A"] + dA - p["b"] * p["Pe"] + p["b"] * p["lam"] * p["Ystar"]) / (1 + p["b"] * p["lam"])
    P = p["Pe"] + p["lam"] * (Y - p["Ystar"])
    return Y, P


def _curvas(p):
    Y = np.linspace(400, 800, 200)
    ad0 = (p["A"] - Y) / p["b"]
    ad1 = (p["A"] + p["dA"] - Y) / p["b"]
    sras = p["Pe"] + p["lam"] * (Y - p["Ystar"])
    (Y0, P0), (Y1, P1) = _eq(p, 0.0), _eq(p, p["dA"])
    return {"lineas": {"AD base": (Y, ad0, config.AZUL2),
                       "AD con shock ($dA$)": (Y, ad1, config.ROJO),
                       "SRAS": (Y, sras, config.VERDE)},
            "puntos": [(Y0, P0, f"antes $({Y0:,.0f},\\,{P0:.2f})$"),
                       (Y1, P1, f"después $({Y1:,.0f},\\,{P1:.2f})$")],
            "anotacion": (f"$\\Delta Y = {Y1 - Y0:+.1f}$,  $\\Delta P = {P1 - P0:+.2f}$\n"
                          "misma dirección: firma del shock de DEMANDA")}


def _resultados(p):
    (Y0, P0), (Y1, P1) = _eq(p, 0.0), _eq(p, p["dA"])
    du = -0.4 * (100 * (Y1 - Y0) / Y0)          # lectura Okun didáctica (β=0.4)
    return {"Y antes": Y0, "Y después": Y1, "ΔY": Y1 - Y0,
            "P antes": P0, "P después": P1, "ΔP": P1 - P0,
            "reparto del shock hacia Y (%)": 100 * (Y1 - Y0) / p["dA"] if p["dA"] else 0.0,
            "Δu vía Okun β=0.4 (pp)": du}


_P0 = {"A": 700.0, "b": 50.0, "Pe": 2.0, "lam": 0.02, "Ystar": 600.0, "dA": 60.0}


def _v_equilibrio():
    Y1, P1 = _eq(_P0, _P0["dA"])
    ad = _P0["A"] + _P0["dA"] - _P0["b"] * P1
    sras = _P0["Pe"] + _P0["lam"] * (Y1 - _P0["Ystar"])
    return abs(ad - Y1) < 1e-9 and abs(sras - P1) < 1e-9, "el equilibrio satisface AD y SRAS a la vez"


def _v_misma_direccion():
    (Y0, P0), (Y1, P1) = _eq(_P0, 0.0), _eq(_P0, _P0["dA"])
    ok = (Y1 - Y0) > 0 and (P1 - P0) > 0
    return ok, f"ΔY={Y1 - Y0:+.1f} y ΔP={P1 - P0:+.2f}: mismo signo (a diferencia de m19)"


def _v_sras_plana():
    p = dict(_P0, lam=0.0)
    (Y0, _), (Y1, _) = _eq(p, 0.0), _eq(p, p["dA"])
    return abs((Y1 - Y0) - p["dA"]) < 1e-9, ("con SRAS plana (λ=0) TODO el shock va a cantidades: "
                                             "ΔY = dA exacto — el mundo keynesiano del nivel 1")


def _v_reparto():
    p = dict(_P0, lam=0.05)
    base = _resultados(_P0)["reparto del shock hacia Y (%)"]
    duro = _resultados(p)["reparto del shock hacia Y (%)"]
    return duro < base, (f"con oferta más rígida (λ↑) el reparto hacia Y cae "
                         f"({base:.0f}% → {duro:.0f}%): más precio, menos producto")


MODELO = Modelo(
    id="m18", nivel=3,
    nombre="Shock de demanda agregada",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("dA", _P0["dA"], -120, 120, 10, "Shock de demanda dA"),
        Parametro("lam", _P0["lam"], 0.0, 0.06, 0.005, "Pendiente de la SRAS (λ)"),
        Parametro("b", _P0["b"], 20, 100, 5, "Sensibilidad de la AD a P (b)"),
        Parametro("A", _P0["A"], 500, 900, 10, "Demanda autónoma A"),
        Parametro("Pe", _P0["Pe"], 1.0, 4.0, 0.1, "Precio esperado Pe"),
        Parametro("Ystar", _P0["Ystar"], 450, 750, 10, "Producto potencial Y*"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Cómo se reparte un shock de gasto entre más producto y más precios?",
        contexto=("El nivel 2 mantuvo los precios congelados; el nivel 3 los despierta. "
                  "Este modelo introduce el plano (Y, P) con el que la síntesis "
                  "neoclásica reconcilió a Keynes con los clásicos: una demanda "
                  "agregada decreciente en P y una oferta de corto plazo creciente. Un "
                  "shock de demanda — estímulo fiscal, euforia, crédito — desplaza la "
                  "AD y se reparte entre producto y precios según la pendiente de la "
                  "oferta."),
        autores=("Aparato AD-AS de la síntesis neoclásica, formalizado en los manuales "
                 "de macro intermedia (conocimiento general); la lectura del reparto "
                 "cantidades/precios es el corazón del debate keynesianos-clásicos."),
        supuestos=[
            "AD lineal POSTULADA: la derivación seria desde IS-LM (P↓ → M/P↑ → r↓ → Y↑) llega en m20.",
            "SRAS lineal con Pe fijo: los contratos se firmaron esperando Pe y no se renegocian dentro del período.",
            "Y* dado (lo explica el nivel 5); sin dinámica de expectativas (llega en m25).",
        ],
        ecuaciones=[
            Ecuacion("Y = A + dA - b\\,P", "demanda agregada (forma reducida)",
                     "todo lo que mueve el gasto a precios dados vive en A (fiscal, ánimo, exterior); "
                     "b resume por qué precios altos deprimen demanda (saldos reales, r, competitividad)."),
            Ecuacion("P = P^e + \\lambda\\,(Y - Y^*)", "oferta de corto plazo",
                     "producir sobre el potencial tensiona costos y precios; λ es la rigidez: λ=0 es "
                     "el mundo keynesiano de precios fijos, λ→∞ el clásico de pleno empleo."),
            Ecuacion("\\Delta Y = \\frac{dA}{1+b\\lambda}, \\quad \\Delta P = \\frac{\\lambda\\,dA}{1+b\\lambda}",
                     "reparto del shock",
                     "el mismo dA se divide: más rigidez de oferta (λ alto) → más inflación y menos "
                     "producto. El multiplicador del nivel 1 era el caso λ=0."),
        ],
        intuicion=("La firma del shock de demanda es su SIMETRÍA: producto y precios "
                   "suben (o caen) juntos. Por eso estabilizar demanda no plantea "
                   "dilema: enfriar una economía sobrecalentada baja la inflación Y la "
                   "brecha a la vez. El dilema de política nace con los shocks de "
                   "oferta (m19), que rompen esa simetría."),
        equilibrio=("Intersección AD-SRAS, única y estable con pendientes estándar. La "
                    "estática comparativa respecto de dA es todo el contenido: el "
                    "denominador 1+bλ es el 'impuesto' que los precios cobran al "
                    "multiplicador."),
        limitaciones=[
            "AD postulada, no derivada (m20 la construye desde IS-LM y ahí b deja de ser un número libre).",
            "Pe fijo: tras el shock las expectativas se ajustarían y la SRAS se desplazaría (el ajuste al largo plazo es m25).",
            "Lectura de empleo vía Okun con β didáctico: en el Perú informal esa traducción es débil (m15).",
        ],
        evolucion=("Es el prólogo del nivel 4: m20-m23 derivan AD y las dos ofertas con "
                   "fundamento, m24 usa este mismo plano para la estanflación y m25 "
                   "añade el ajuste de expectativas que aquí falta. La respuesta ÓPTIMA "
                   "al shock de demanda (regla de política) es m38/m56."),
    ),
    escenarios=[
        Escenario("estimulo", "impulso de demanda dA = +60",
                  {"dA": 60.0},
                  "con λ=0.02 el 50% del impulso se hace producto y el resto precios: "
                  "el multiplicador ya no es el del nivel 1 — los precios cobran peaje."),
        Escenario("colapso_demanda", "desplome dA = −80 (estilo 2008-2009)",
                  {"dA": -80.0},
                  "recesión CON desinflación: la firma de demanda en reversa — y la "
                  "razón por la que 2009 trajo inflación baja, no alta."),
        Escenario("oferta_rigida", "el mismo estímulo con λ = 0.05",
                  {"lam": 0.05},
                  "cerca del pleno empleo la oferta empina: el estímulo rinde 29% en "
                  "producto y el resto se evapora en precios."),
    ],
    verificaciones=[
        Verificacion("equilibrio satisface AD y SRAS", _v_equilibrio),
        Verificacion("firma de demanda: ΔY y ΔP mismo signo", _v_misma_direccion),
        Verificacion("λ=0 → multiplicador pleno (ΔY=dA)", _v_sras_plana),
        Verificacion("más λ → menos producto, más precios", _v_reparto),
    ],
    notas="Firma de demanda: P e Y juntos. m19 rompe la simetría y crea el dilema de política.",
)
