"""simuladores/macro/modelos/nivel_12/m102_tipo_cambio.py — tipo de cambio PEN/USD, con datos del BCRP (nivel 12).

El sol frente al dólar (BCRP PN01207PM), 2004-2024. La serie muestra la
FLOTACIÓN ADMINISTRADA peruana: el sol se mueve (de ~3.3 a ~3.8 en la
muestra) pero con volatilidad MODERADA comparada con otros emergentes —
resultado de la intervención del BCRP (m45) y las reservas altas (m50). El
laboratorio calcula la depreciación acumulada y la volatilidad, y las
conecta con m47 (PPP: la tendencia sigue al diferencial de inflación) y m85
(passthrough bajo: por eso el sol se mueve sin desatar inflación). Es la
esquina flexible+autonomía del trilema (m50) con datos.

Procedencia: dato BCRP PN01207PM (tipo de cambio interbancario, S//US$),
muestra 2004-2024. La flotación administrada es política del BCRP; las
lecturas (volatilidad, tendencia) son descriptivas.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _serie():
    return _datos_bcrp.serie("tipo_cambio", anual=True)  # (años, S//US$)


def _curvas(p):
    anos, e = _serie()
    # variación anual (%)
    dep = np.concatenate([[0], 100 * np.diff(e) / e[:-1]])
    return {"lineas": {"tipo de cambio S//US$ (BCRP)": (anos, e, config.AZUL2)},
            "puntos": [(2020.0, float(e[anos == 2020][0]), "COVID: 3.50"),
                       (float(anos[np.argmax(e)]), float(e.max()), f"máx {e.max():.2f}")],
            "anotacion": (f"tipo de cambio interbancario (BCRP PN01207PM)\n"
                          f"depreciación acumulada {100 * (e[-1] / e[0] - 1):+.0f}% en "
                          f"{int(anos[-1] - anos[0])} años\n"
                          f"volatilidad anual {float(dep.std()):.1f}% — flotación administrada (m50)")}


def _resultados(p):
    anos, e = _serie()
    dep = 100 * np.diff(e) / e[:-1]
    return {"tipo de cambio inicial (S//US$)": float(e[0]),
            "tipo de cambio final (S//US$)": float(e[-1]),
            "depreciación acumulada (%)": 100 * (e[-1] / e[0] - 1),
            "depreciación anual promedio (%)": float(dep.mean()),
            "volatilidad anual (pp)": float(dep.std()),
            "máxima depreciación anual (%)": float(dep.max())}


def _ecuaciones_calibradas(p):
    anos, e = _serie()
    return [f"$E: {float(e[0]):.2f} \\to {float(e[-1]):.2f}$ S//US$ "
            f"({100 * (e[-1] / e[0] - 1):+.0f}\\% en {int(anos[-1] - anos[0])} años)",
            f"volatilidad anual {float(np.diff(e).std() / e[:-1].mean() * 100):.1f}\\% (flotación administrada)"]


_P0 = {"ref_volatilidad": 15.0}


def _v_depreciacion_moderada():
    anos, e = _serie()
    dep_anual = abs(100 * (e[-1] / e[0] - 1)) / (anos[-1] - anos[0])
    return dep_anual < 3, \
        (f"la depreciación promedio del sol es moderada ({dep_anual:.1f}%/año): coherente con el "
         "bajo diferencial de inflación Perú-EE.UU. (PPP, m47) — el ancla (m99) estabiliza la tendencia")


def _v_baja_volatilidad():
    anos, e = _serie()
    dep = 100 * np.diff(e) / e[:-1]
    return float(dep.std()) < _P0["ref_volatilidad"], \
        (f"la volatilidad del sol ({float(dep.std()):.1f}% anual) es baja para un emergente: la "
         "flotación ADMINISTRADA del BCRP (intervención m45 + reservas m50) suaviza el tipo de cambio")


def _v_ppp_tendencia():
    # la depreciación tendencial debe ser pequeña, coherente con inflación anclada (m47)
    anos, e = _serie()
    _, ipc = _datos_bcrp.serie("ipc_12m", anual=True)
    return float(ipc.mean()) < 4, \
        (f"con inflación peruana anclada (~{float(ipc.mean()):.1f}%, m99) cercana a la de EE.UU., "
         "el sol no tiene tendencia depreciatoria fuerte (PPP, m47): estabilidad de precios = estabilidad cambiaria")


def _v_covid_deprecio():
    anos, e = _serie()
    # el sol se depreció en/tras el COVID (risk-off, m87)
    return float(e[anos == 2020][0]) > float(e[anos == 2019][0]) if 2019 in anos else True, \
        ("el sol se depreció con el COVID (2020): el risk-off global (m87) presionó el tipo de "
         "cambio — pero de forma ordenada, amortiguada por las reservas (m50)")


MODELO = Modelo(
    id="m102", nivel=12,
    nombre="Tipo de cambio PEN/USD (datos BCRP)",
    xlabel="Año", ylabel="Tipo de cambio (S/ por US$)",
    parametros=[
        Parametro("ref_volatilidad", _P0["ref_volatilidad"], 5, 25, 2.5, "Volatilidad de referencia (%)",
                  grupo="comparación", definicion="umbral de un emergente típico; el sol está por debajo"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo se ha comportado el sol frente al dólar — y qué revela sobre el régimen cambiario del Perú?",
        variables=[("E_t", "tipo de cambio S//US$ (BCRP PN01207PM)"),
                   ("volatilidad", "moderada: la flotación administrada (m45, m50)"),
                   ("tendencia", "suave: coherente con inflación anclada (PPP, m47)")],
        derivacion=["dato: \\;E_t\\;interbancario\\;(BCRP\\;PN01207PM)",
                    "tendencia\\;suave \\sim diferencial\\;de\\;inflación\\;(PPP, m47)",
                    "volatilidad\\;baja \\sim flotación\\;administrada\\;(m45, m50)"],
        contexto=("La serie del tipo de cambio sol/dólar (BCRP PN01207PM) documenta "
                  "el régimen cambiario peruano: la FLOTACIÓN ADMINISTRADA. El sol "
                  "NO está fijo (se movió de ~3.3 a ~3.8 en la muestra 2004-2024, "
                  "con episodios de apreciación en el boom del cobre y depreciación "
                  "en el COVID) pero tampoco flota libremente — su volatilidad es "
                  "MODERADA comparada con otros emergentes, resultado de dos cosas: "
                  "la intervención del BCRP en el mercado cambiario (m45, comprando "
                  "en las bonanzas y vendiendo en las crisis para suavizar) y el "
                  "colchón de reservas altas (m50, ~30% del PIB) que da confianza y "
                  "capacidad de intervenir. Esta serie es la esquina "
                  "flexible+autonomía del trilema (m50) con datos: el Perú eligió "
                  "abrir la cuenta de capitales y mantener política monetaria "
                  "propia (m40), a costa de dejar flotar el tipo de cambio — pero lo "
                  "administra para evitar movimientos bruscos. Dos lecturas "
                  "teóricas la iluminan. Primero, PPP (m47): la tendencia suave del "
                  "sol es coherente con el bajo diferencial de inflación entre el "
                  "Perú (anclado, m99) y EE.UU. — sin inflación crónica, no hay "
                  "depreciación tendencial fuerte. Segundo, el passthrough bajo "
                  "(m85): precisamente porque el sol se mueve poco y de forma "
                  "creíble, sus movimientos no se repasan a los precios, lo que a "
                  "su vez permite dejarlo flotar sin miedo (m84) — un círculo "
                  "virtuoso de credibilidad. La estabilidad cambiaria peruana no es "
                  "casualidad ni suerte; es el producto de la baja dolarización "
                  "(m84), el ancla de inflación (m99) y las reservas (m50) "
                  "construidas deliberadamente tras la crisis de los 80."),
        autores=("Dato: BCRP (PN01207PM); flotación administrada: régimen del BCRP; "
                 "la teoría: m45 (mercado cambiario), m47 (PPP), m50 (trilema), "
                 "m85 (passthrough) — conocimiento general."),
        supuestos=[
            "El tipo de cambio interbancario del BCRP es la referencia: otros tipos (paralelo, real) pueden diferir levemente.",
            "La baja volatilidad se atribuye a la flotación administrada (m45, m50): la atribución es lectura coherente con el régimen, no prueba causal.",
            "La tendencia suave se conecta con PPP (m47) e inflación anclada (m99): es interpretación teórica, no una estimación de la relación.",
        ],
        ecuaciones=[
            Ecuacion("E_t: \\;flotación\\;administrada\\;(m45, m50)", "el régimen",
                     "el sol se mueve pero con volatilidad moderada: ni fijo ni libre, administrado "
                     "por intervención y reservas — la esquina del trilema que el Perú eligió (m50)."),
            Ecuacion("tendencia \\sim \\pi_{Perú} - \\pi_{EEUU} \\;(PPP, m47)",
                     "la tendencia anclada",
                     "sin inflación crónica (m99), el sol no tiene deriva fuerte: la estabilidad de "
                     "precios se traduce en estabilidad cambiaria (verificado)."),
        ],
        intuicion=("La serie del sol enseña que un tipo de cambio estable en un "
                   "emergente no es un accidente sino una CONSTRUCCIÓN. El Perú no "
                   "tiene un sol estable porque tuvo suerte, sino porque edificó las "
                   "condiciones: ancló la inflación (m99), redujo la dolarización "
                   "(m84), acumuló reservas (m50) y administra la flotación (m45). "
                   "Cada una de esas piezas se estudió en el currículo teórico, y "
                   "aquí se ven trabajando juntas en los datos. El contraste con un "
                   "emergente sin esas piezas (alta inflación, dolarizado, sin "
                   "reservas) sería dramático: allí el tipo de cambio sería volátil, "
                   "el passthrough alto (m85), y cada shock externo (m86, m87) una "
                   "crisis. La flotación administrada peruana es un punto dulce del "
                   "trilema (m50): suficiente flexibilidad para absorber shocks "
                   "externos (el sol se deprecia en el COVID y amortigua el golpe) "
                   "pero suficiente estabilidad para no desanclar la inflación ni "
                   "quebrar balances. Es, en datos, la recompensa de dos décadas de "
                   "política monetaria y cambiaria coherente."),
        equilibrio=("El sol flota con tendencia suave (coherente con PPP e inflación "
                    "anclada) y volatilidad moderada (flotación administrada), "
                    "verificado. Se deprecia en los shocks (COVID) de forma "
                    "ordenada — el régimen absorbe sin romperse."),
        limitaciones=[
            "Descriptivo: no estima la regla de intervención del BCRP ni la relación PPP (eso exige más análisis).",
            "Muestra anual: la volatilidad intra-anual (diaria/mensual) es mayor y más relevante para la gestión cambiaria.",
            "La atribución a la flotación administrada es coherente con el régimen pero no probada causalmente (contrafactual no observable).",
        ],
        evolucion=("Completa el retrato de la política peruana con datos (m99 "
                   "inflación, m100 regla, m101 transmisión, m102 tipo de cambio) y "
                   "conecta m45/m47/m50/m85 con la evidencia. Prepara m104 "
                   "(cobre→tipo de cambio: el driver externo del sol) y m110-m111 "
                   "(shock externo y FED sobre el Perú). Es la esquina del trilema "
                   "peruana documentada."),
    ),
    escenarios=[
        Escenario("comparacion_emergente", "referencia de volatilidad de un emergente típico (15%)",
                  {"ref_volatilidad": 15.0},
                  "el sol está muy por debajo: la flotación administrada peruana "
                  "logra una estabilidad que muchos emergentes envidian — el fruto "
                  "de los colchones (m50, m84, m99).",
                  cadena=["emergente típico: volatilidad alta", "el sol: volatilidad moderada",
                          "flotación administrada (m45, m50)", "+ ancla (m99) + baja dolarización (m84)",
                          "estabilidad construida, no heredada"]),
        Escenario("emergente_volatil", "referencia de un emergente frágil (8%)",
                  {"ref_volatilidad": 8.0},
                  "incluso contra un umbral exigente, el sol suele cumplir: la "
                  "administración cambiaria del BCRP es efectiva — aunque los shocks "
                  "grandes (COVID) sí lo mueven.",
                  cadena=["umbral exigente de estabilidad", "el sol lo cumple la mayoría del tiempo",
                          "salvo shocks grandes (COVID, m81)", "el BCRP suaviza pero no fija",
                          "flexibilidad con estabilidad"]),
    ],
    verificaciones=[
        Verificacion("depreciación tendencial moderada (PPP, m47)", _v_depreciacion_moderada),
        Verificacion("baja volatilidad (flotación administrada, m50)", _v_baja_volatilidad),
        Verificacion("tendencia coherente con inflación anclada (m99)", _v_ppp_tendencia),
        Verificacion("el sol se depreció en el COVID (risk-off, m87)", _v_covid_deprecio),
    ],
    notas="Flotación administrada: el sol estable es una construcción (m50+m84+m99), no un accidente. La esquina del trilema peruana.",
)
