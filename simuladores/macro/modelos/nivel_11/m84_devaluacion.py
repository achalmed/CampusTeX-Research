"""simuladores/macro/modelos/nivel_11/m84_devaluacion.py — devaluación: expansiva o contractiva (nivel 11).

El debate clásico de los emergentes. Una devaluación tiene DOS efectos
opuestos que combinan m46 (competitividad) y m71 (balances):
  (+) COMPETITIVIDAD: E↑ abarata exportaciones → ↑XN → expansiva (Mundell, m49)
  (−) HOJA DE BALANCE: si la deuda es en DÓLARES, E↑ infla el pasivo en soles
      → quiebras → contractiva (efecto Krugman de tercera generación, m74)
El efecto NETO depende de la dolarización de la deuda:
  devaluación_neta = competitividad·(1−dolar) − balance·dolar
Alta dolarización invierte el signo: la devaluación que debería estimular,
quiebra. Es la razón del "miedo a flotar" (fear of floating, Calvo-Reinhart)
y de por qué la desdolarización peruana (mención) fue política de Estado.

Procedencia: devaluación contractiva (Krugman-Taylor; balance sheet effects,
Krugman 1999; fear of floating, Calvo-Reinhart — menciones) — conocimiento
general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _efectos(p):
    comp = p["competitividad"] * (p["dev"] / 100)          # efecto expansivo
    balance = p["balance"] * (p["dev"] / 100) * (p["dolar"] / 100)  # efecto contractivo
    neto = comp - balance
    return comp, balance, neto


def _curvas(p):
    dolar = np.linspace(0, 100, 200)
    comp = p["competitividad"] * (p["dev"] / 100) * np.ones_like(dolar)
    balance = p["balance"] * (p["dev"] / 100) * (dolar / 100)
    neto = comp - balance
    d0 = 100 * p["competitividad"] / p["balance"]           # dolarización de cruce
    return {"lineas": {"efecto competitividad (+, m46/m49)": (dolar, comp, config.VERDE),
                       "efecto hoja de balance (−, m71/m74)": (dolar, balance, config.ROJO),
                       "efecto NETO sobre el producto": (dolar, neto, config.AZUL2),
                       "cero": (dolar, np.zeros_like(dolar), config.GRIS)},
            "puntos": [(d0, 0.0, f"cruce: {d0:.0f}% dolarización"),
                       (p["dolar"], float(_efectos(p)[2]), "tu economía")],
            "anotacion": (f"devaluación {p['dev']:.0f}% con {p['dolar']:.0f}% de deuda en USD\n"
                          f"neto: {float(_efectos(p)[2]):+.2f} "
                          f"({'EXPANSIVA' if _efectos(p)[2] > 0 else 'CONTRACTIVA'})\n"
                          "alta dolarización invierte el signo: fear of floating")}


def _resultados(p):
    comp, balance, neto = _efectos(p)
    return {"efecto competitividad (+)": comp,
            "efecto hoja de balance (−)": balance,
            "efecto NETO sobre Y": neto,
            "dolarización de cruce (%)": 100 * p["competitividad"] / p["balance"],
            "¿expansiva? (1 sí)": 1.0 if neto > 0 else 0.0}


def _ecuaciones_calibradas(p):
    comp, balance, neto = _efectos(p)
    return [f"$comp = {p['competitividad']:.1f}\\times{p['dev'] / 100:.2f} = {comp:.2f}$",
            f"$bal = {p['balance']:.1f}\\times{p['dev'] / 100:.2f}\\times{p['dolar'] / 100:.2f} = {balance:.2f}$",
            f"$neto = {comp:.2f} - {balance:.2f} = {neto:+.2f}$"]


_P0 = {"dev": 20.0, "dolar": 30.0, "competitividad": 3.0, "balance": 5.0}


def _v_baja_dolar_expansiva():
    _, _, neto = _efectos(dict(_P0, dolar=10.0))
    return neto > 0, \
        (f"con poca deuda en dólares (10%), la devaluación es EXPANSIVA (neto {neto:+.2f}): "
         "domina la competitividad (Mundell-Fleming, m49)")


def _v_alta_dolar_contractiva():
    _, _, neto = _efectos(dict(_P0, dolar=80.0))
    return neto < 0, \
        (f"con mucha deuda en dólares (80%), la devaluación es CONTRACTIVA (neto {neto:+.2f}): "
         "los balances estallan (Krugman tercera generación, m71+m74)")


def _v_cruce_exacto():
    d0 = 100 * _P0["competitividad"] / _P0["balance"]
    _, _, neto = _efectos(dict(_P0, dolar=d0))
    return abs(neto) < 1e-9, \
        (f"en la dolarización de cruce ({d0:.0f}%) el efecto neto es EXACTAMENTE cero: "
         "el umbral entre devaluación buena y mala")


def _v_fear_of_floating():
    _, _, neto = _efectos(_P0)
    return _P0["dolar"] > 0 and neto < _efectos(dict(_P0, dolar=0.0))[2], \
        ("cualquier dolarización reduce el beneficio de devaluar: por eso los emergentes "
         "temen flotar (Calvo-Reinhart) y desdolarizan (Perú, mención)")


MODELO = Modelo(
    id="m84", nivel=11,
    nombre="Devaluación (expansiva o contractiva)",
    xlabel="Dolarización de la deuda (%)", ylabel="Efecto sobre el producto",
    parametros=[
        Parametro("dolar", _P0["dolar"], 0, 100, 5, "Deuda en dólares (%)", grupo="vulnerabilidad",
                  definicion="la variable clave: alta = devaluación contractiva"),
        Parametro("dev", _P0["dev"], 5, 50, 5, "Magnitud de la devaluación (%)", grupo="shock"),
        Parametro("competitividad", _P0["competitividad"], 1, 6, 0.5, "Fuerza del canal competitividad",
                  grupo="canales", definicion="cuánto estimula XN (m46/m49)"),
        Parametro("balance", _P0["balance"], 1, 8, 0.5, "Fuerza del canal balance", grupo="canales",
                  definicion="cuánto quiebran los deudores en dólares (m71)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Devaluar estimula la economía o la hunde? Depende de UNA cosa: cuánta deuda está en dólares.",
        variables=[("competitividad", "el efecto BUENO: exportaciones más baratas (m46/m49)"),
                   ("hoja de balance", "el efecto MALO: deuda en dólares que estalla (m71/m74)"),
                   ("dolarización", "la variable que decide cuál gana")],
        derivacion=["(+)\\;comp = \\gamma\\cdot dev \\;\\;(Mundell, m49)",
                    "(-)\\;bal = \\beta\\cdot dev\\cdot dolar \\;\\;(Krugman, m71)",
                    "neto = comp - bal; \\;\\;cambia\\;de\\;signo\\;en\\;dolar^* = \\gamma/\\beta"],
        contexto=("La teoría de manual (Mundell-Fleming, m49) dice que devaluar es "
                  "expansivo: abarata las exportaciones, mejora la balanza "
                  "comercial, estimula el producto. Pero los emergentes aprendieron "
                  "en carne propia que a veces devaluar HUNDE la economía. La razón "
                  "es la hoja de balance: si empresas, bancos y gobierno se "
                  "endeudaron en dólares (porque el crédito local era caro o "
                  "escaso), una devaluación multiplica su deuda medida en moneda "
                  "local, provoca quiebras masivas y contrae el crédito — el efecto "
                  "de tercera generación que Krugman (1999, mención) formalizó tras "
                  "la crisis asiática. El efecto NETO depende de la dolarización: "
                  "baja, domina la competitividad (devaluación buena); alta, domina "
                  "el balance (devaluación mala). Esta asimetría explica el 'fear "
                  "of floating' (Calvo-Reinhart, mención): los emergentes dicen "
                  "flotar pero intervienen para evitar devaluaciones grandes. Y "
                  "explica por qué la DESDOLARIZACIÓN fue política de Estado en el "
                  "Perú (mención): reducir la deuda en dólares es recuperar la "
                  "devaluación como herramienta."),
        autores=("Devaluación contractiva: Krugman-Taylor (años 70); balance sheet "
                 "effects: Krugman (1999); fear of floating: Calvo y Reinhart "
                 "(2002) — menciones."),
        supuestos=[
            "Dos canales lineales opuestos: la realidad es más rica (curva J, passthrough) pero la asimetría es robusta.",
            "La deuda en dólares no tiene cobertura natural (exportadores con ingresos en dólares están cubiertos — matiz).",
            "Efecto de impacto: la competitividad tarda (curva J) mientras el balance golpea de inmediato — el corto plazo es aún más contractivo.",
        ],
        ecuaciones=[
            Ecuacion("neto = \\gamma\\cdot dev - \\beta\\cdot dev\\cdot dolar", "los dos efectos",
                     "competitividad (constante en la dolarización) menos balance (creciente en "
                     "ella): la resta cambia de signo en un umbral verificable."),
            Ecuacion("dolar^* = \\gamma / \\beta", "la dolarización de cruce",
                     "por debajo, devaluar estimula; por encima, quiebra: el umbral que separa "
                     "una herramienta de una bomba (verificado exacto)."),
        ],
        intuicion=("La devaluación es una herramienta que se vuelve arma según el "
                   "estado del paciente: en una economía con deuda en su propia "
                   "moneda, es el ajuste más suave (el precio se mueve, no las "
                   "cantidades); en una dolarizada, es un infarto de balances. Por "
                   "eso la política más importante para PODER devaluar cuando se "
                   "necesita es, paradójicamente, reducir la dolarización EN LAS "
                   "BUENAS — construir mercados de deuda en moneda local, anclar la "
                   "inflación (m40) para que la gente confíe en el sol. El Perú "
                   "recorrió ese camino: de una economía altamente dolarizada en "
                   "los 90 a una que hoy puede dejar flotar el sol sin pánico "
                   "(m110). La lección: la resiliencia cambiaria se compra años "
                   "antes de necesitarla."),
        equilibrio=("El efecto neto cruza cero en dolar* = γ/β (verificado exacto): "
                    "tres regímenes — expansiva (dolar<dolar*), neutra (=) y "
                    "contractiva (>). El 'miedo a flotar' vive en la región "
                    "contractiva."),
        limitaciones=[
            "Curva J: la competitividad tarda meses (los contratos existentes), el balance golpea ya — el corto plazo es más contractivo que el neto de impacto.",
            "Cobertura natural: los exportadores con ingresos en dólares no quiebran al devaluar — la dolarización relevante es la NO cubierta.",
            "Sin respuesta de política: intervenir (fear of floating) o subir la tasa (m48) cambia el resultado — aquí es devaluación 'pura'.",
        ],
        evolucion=("Sintetiza m46 (competitividad), m49 (Mundell) y m71/m74 "
                   "(balances) en el debate más práctico de los emergentes. Conecta "
                   "con m85 (la devaluación como fuente de inflación importada) y "
                   "m87 (la salida de capitales que fuerza la devaluación). Para el "
                   "Perú, la baja dolarización actual es lo que hace viable su "
                   "régimen de flotación (m110)."),
    ),
    escenarios=[
        Escenario("moneda_propia", "economía desdolarizada: 10% de deuda en USD",
                  {"dolar": 10.0},
                  "devaluación EXPANSIVA: domina la competitividad, como en el "
                  "manual (m49) — el privilegio de deber en tu propia moneda.",
                  cadena=["devaluación", "exportaciones más baratas (m46)",
                          "poca deuda en dólares: balances sanos", "domina competitividad",
                          "efecto neto expansivo"]),
        Escenario("economia_dolarizada", "80% de deuda en dólares (emergente frágil)",
                  {"dolar": 80.0},
                  "devaluación CONTRACTIVA: los balances estallan y las quiebras "
                  "superan el estímulo exportador — Asia 1997, Argentina 2001.",
                  cadena=["devaluación", "la deuda en dólares se multiplica en moneda local",
                          "quiebras masivas (m71)", "crédito se contrae",
                          "el balance domina: efecto neto contractivo"]),
        Escenario("umbral_exacto", "en la dolarización de cruce (60%)",
                  {"dolar": 60.0},
                  "los dos efectos se cancelan: el punto donde devaluar no ayuda ni "
                  "perjudica — la frontera entre herramienta y arma.",
                  cadena=["dolarización = γ/β", "competitividad = balance",
                          "efecto neto cero", "el umbral crítico"]),
        Escenario("desdolarizar", "política de Estado: bajar dolar de 80% a 30%",
                  {"dolar": 30.0},
                  "recuperar la devaluación como herramienta: el camino peruano de "
                  "los 90 a hoy — resiliencia comprada años antes.",
                  cadena=["desdolarización (mercados en soles, ancla m40)",
                          "menos deuda en dólares", "el balance pesa menos",
                          "la devaluación vuelve a ser expansiva", "resiliencia estructural"]),
    ],
    verificaciones=[
        Verificacion("baja dolarización ⇒ expansiva (Mundell)", _v_baja_dolar_expansiva),
        Verificacion("alta dolarización ⇒ contractiva (Krugman)", _v_alta_dolar_contractiva),
        Verificacion("efecto neto cero en la dolarización de cruce", _v_cruce_exacto),
        Verificacion("cualquier dolarización reduce el beneficio (fear of floating)", _v_fear_of_floating),
    ],
    notas="Herramienta o arma según la dolarización. La resiliencia cambiaria se compra años antes de necesitarla.",
)
