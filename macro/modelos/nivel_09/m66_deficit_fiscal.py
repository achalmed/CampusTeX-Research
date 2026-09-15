"""simuladores/macro/modelos/nivel_09/m66_deficit_fiscal.py — déficit estructural vs cíclico (nivel 9).

El déficit OBSERVADO mezcla dos cosas que exigen respuestas opuestas:
  déficit observado = déficit ESTRUCTURAL − ε·brecha
El término cíclico (−ε·brecha) son los estabilizadores automáticos (m04:
los impuestos caen y el gasto social sube solos en recesión). Los errores
clásicos de lectura:
  en RECESIÓN el observado exagera el desequilibrio (ajustar sería m69);
  en BOOM el observado lo esconde (el "superávit" ilusorio pre-crisis).
Las reglas fiscales modernas (Chile pionera; Perú con la suya — menciones)
se escriben sobre el ESTRUCTURAL por esta exacta razón.

Procedencia: descomposición estándar de balances fiscales (OCDE/FMI,
mención) — conocimiento general; calibración didáctica.
"""

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _deficits(p):
    ciclico = -p["eps"] * p["brecha"]
    return p["def_est"], ciclico, p["def_est"] + ciclico


def _curvas(p):
    est, cic, obs = _deficits(p)
    cats = ["estructural\n(la decisión)", "cíclico\n(el ciclo, $-\\varepsilon\\cdot$brecha)",
            "OBSERVADO\n(el titular)"]
    vals = [est, cic, obs]
    cols = [config.AZUL2, config.DORADO, config.ROJO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"brecha del producto: {p['brecha']:+.1f}% (m16)\n"
                          f"observado = {est:.1f} + ({cic:+.1f}) = {obs:.1f}% del PIB\n"
                          "el titular mezcla decisión y ciclo — la regla los separa")}


def _resultados(p):
    est, cic, obs = _deficits(p)
    return {"déficit estructural (% PIB)": est,
            "componente cíclico": cic,
            "déficit observado": obs,
            "estabilizadores automáticos |ε·brecha|": abs(cic),
            "error de leer el observado": obs - est}


def _ecuaciones_calibradas(p):
    est, cic, obs = _deficits(p)
    return [f"$obs = {est:.1f} - {p['eps']:.2f} \\times ({p['brecha']:+.1f}) = {obs:.2f}$"]


_P0 = {"def_est": 1.5, "eps": 0.4, "brecha": -3.0}


def _v_descomposicion():
    est, cic, obs = _deficits(_P0)
    return abs(obs - (est + cic)) < 1e-12, "observado = estructural + cíclico, sin residuo"


def _v_brecha_cero():
    est, cic, obs = _deficits(dict(_P0, brecha=0.0))
    return abs(obs - est) < 1e-12, \
        "con brecha cero el observado ES el estructural: solo en el potencial se ve la verdad"


def _v_boom_esconde():
    est, cic, obs = _deficits(dict(_P0, brecha=4.0))
    return obs < est, (f"con brecha +4%, el observado ({obs:.1f}) esconde al estructural "
                       f"({est:.1f}): el 'superávit' ilusorio de todo boom — el error pre-crisis clásico")


def _v_estabilizadores():
    cic1 = _deficits(dict(_P0, brecha=-2.0))[1]
    cic2 = _deficits(dict(_P0, brecha=-4.0))[1]
    return abs(cic2 - 2 * cic1) < 1e-12, \
        (f"el componente cíclico escala lineal con la brecha ({cic1:.1f}→{cic2:.1f}): "
         "los estabilizadores de m04 trabajando solos, sin decreto")


MODELO = Modelo(
    id="m66", nivel=9,
    nombre="Déficit fiscal (estructural vs cíclico)",
    xlabel="", ylabel="% del PIB",
    parametros=[
        Parametro("brecha", _P0["brecha"], -6, 6, 0.5, "Brecha del producto (%)", grupo="ciclo",
                  definicion="la de m16 — con su incertidumbre de medición a cuestas"),
        Parametro("def_est", _P0["def_est"], -2, 4, 0.25, "Déficit estructural (% PIB)", grupo="decisión",
                  definicion="lo que queda con la economía en su potencial"),
        Parametro("eps", _P0["eps"], 0.1, 0.7, 0.05, "Sensibilidad cíclica ε", grupo="estructura",
                  definicion="cuánto déficit genera solo cada punto de brecha"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿El déficit del titular es decisión o es ciclo — y por qué confundirlos produce los dos peores errores fiscales?",
        variables=[("estructural", "la política de verdad — lo que hay con brecha cero"),
                   ("cíclico", "los estabilizadores automáticos — el ciclo pasando factura solo"),
                   ("observado", "el titular — la mezcla que engaña en ambas direcciones")],
        derivacion=["obs = est - \\varepsilon \\cdot brecha",
                    "brecha < 0 \\Rightarrow obs > est \\;(la\\;recesión\\;exagera)",
                    "brecha > 0 \\Rightarrow obs < est \\;(el\\;boom\\;esconde)"],
        contexto=("Dos errores históricos comparten causa: ajustar en recesión "
                  "porque el déficit observado 'explotó' (cuando era el ciclo, no "
                  "el desorden — la puerta a m69), y celebrar superávits de boom "
                  "que eran espejismo cíclico (España e Irlanda pre-2008, mención: "
                  "superávits observados con deterioro estructural). La "
                  "descomposición es la vacuna: Chile la institucionalizó con su "
                  "regla estructural (mención pionera) y el Perú tiene la suya "
                  "(mención; m108 con datos MEF). El precio de la vacuna: hay que "
                  "estimar la brecha — con toda la niebla de m16."),
        autores=("Metodología estándar de balances estructurales (OCDE, FMI — "
                 "menciones); regla estructural chilena (mención pionera); marco "
                 "fiscal peruano (mención)."),
        supuestos=[
            "ε lineal y estable: la sensibilidad real depende de la estructura tributaria (más IVA = más cíclica, mención).",
            "La brecha es observable: es la MISMA niebla de m16 — las reglas estructurales heredan sus revisiones.",
            "Sin precios de materias primas: en Perú el ciclo del cobre pide una corrección adicional (estructural minero, mención — m103).",
        ],
        ecuaciones=[
            Ecuacion("obs = est - \\varepsilon\\,brecha", "la descomposición",
                     "una recta en la brecha: ε son los estabilizadores de m04 institucionalizados "
                     "— impuestos que caen y gasto social que sube sin que nadie firme nada."),
        ],
        intuicion=("El déficit observado es un termómetro puesto al sol: mide la "
                   "fiebre del paciente MÁS el clima. La regla estructural lo pone "
                   "a la sombra (brecha cero) y decide sobre la fiebre real. El "
                   "dividendo es doble: en recesión, permite dejar trabajar a los "
                   "estabilizadores sin pánico (m68); en boom, obliga a guardar el "
                   "espejismo en vez de gastarlo — exactamente el fondo de "
                   "estabilización peruano (mención)."),
        equilibrio=("Descomposición contable exacta (verificada); su punto fijo "
                    "conceptual es brecha=0, donde titular y verdad coinciden — "
                    "el único momento en que el observado no miente."),
        limitaciones=[
            "Hereda TODA la incertidumbre de la brecha (m16): un estructural mal medido es un error con sello oficial.",
            "ε varía con la estructura tributaria y el tipo de shock (no es lo mismo recesión de consumo que de exportaciones).",
            "Para exportadores de materias primas falta el ajuste por precios (cobre): el estructural peruano lo incorpora (mención, m103/m108).",
        ],
        evolucion=("Da el instrumento de medición que la política contracíclica "
                   "(m68) necesita para operar sin engañarse, y el lenguaje en que "
                   "la austeridad (m69) debe evaluarse: ajustar lo ESTRUCTURAL, "
                   "dejar respirar lo cíclico. m108 leerá el balance peruano con "
                   "esta lente."),
    ),
    escenarios=[
        Escenario("recesion_que_asusta", "brecha −3%: el titular grita 2.7%",
                  {"brecha": -3.0},
                  "el observado (2.7%) casi duplica al estructural (1.5%): ajustar "
                  "por el titular sería apretar en plena recesión — el error que "
                  "m69 disecciona.",
                  cadena=["recesión (brecha<0)", "impuestos caen solos, gasto social sube",
                          "componente cíclico +1.2%", "el titular exagera",
                          "la regla estructural evita el pánico (m68)"]),
        Escenario("boom_enganoso", "brecha +4%: el titular celebra",
                  {"brecha": 4.0},
                  "observado −0.1% ('¡superávit!') con estructural de +1.5%: el "
                  "espejismo exacto de España/Irlanda pre-2008 (mención) — el boom "
                  "pagaba la fiesta.",
                  cadena=["boom (brecha>0)", "la recaudación cíclica inunda",
                          "el observado se ve sano", "el estructural sigue en déficit",
                          "cuando el ciclo gira, el espejismo se evapora"]),
        Escenario("regla_estructural", "déficit estructural 0 con recesión de −3%",
                  {"def_est": 0.0, "brecha": -3.0},
                  "el observado muestra 1.2% de déficit y está PERFECTO: son los "
                  "estabilizadores trabajando — la regla bien leída no los estrangula.",
                  cadena=["estructural en cero (la regla se cumple)",
                          "la recesión genera déficit cíclico", "el titular muestra rojo",
                          "no hay nada que corregir: es el seguro pagando (m68)"]),
    ],
    verificaciones=[
        Verificacion("descomposición exacta sin residuo", _v_descomposicion),
        Verificacion("con brecha cero, observado = estructural", _v_brecha_cero),
        Verificacion("el boom esconde el desequilibrio", _v_boom_esconde),
        Verificacion("estabilizadores lineales en la brecha (m04)", _v_estabilizadores),
    ],
    notas="El termómetro al sol: el observado mide fiebre MÁS clima. La regla decide sobre la fiebre.",
)
