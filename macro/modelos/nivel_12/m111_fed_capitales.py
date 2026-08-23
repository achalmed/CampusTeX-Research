# m111_fed_capitales.py — la FED y los flujos de capital hacia el Perú (nivel 12).
#
# El canal FINANCIERO del exterior, complemento del real (m110). La política
# monetaria de Estados Unidos —la tasa de la Reserva Federal (FED)— gobierna el
# apetito global por riesgo y, con él, los flujos de capital hacia economías
# emergentes como la peruana. Cuando la FED baja su tasa a casi cero (2009-2015,
# 2020-2021), el capital busca rendimiento y fluye al Perú: el sol se aprecia
# (el tipo de cambio bajó de 3.01 en 2009 a 2.64 en 2012). Cuando la FED sube
# agresivamente (2022-2023, de 0 a 5%), el capital vuelve a EE.UU., el dólar se
# fortalece y el sol se presiona. Y el Perú NO puede ignorarla: con cuenta de
# capitales abierta, la tasa del BCRP sigue en gran medida a la FED (corr +0.54)
# — el TRILEMA de m50: no se puede tener a la vez tipo de cambio estable,
# libre movilidad de capital y política monetaria autónoma. 2021 recuerda el
# matiz de m104: a veces el riesgo idiosincrático (la crisis política) pesa más
# que la FED — el sol se debilitó con la FED aún en cero.
#
# Procedencia: tasa del BCRP (PD04722MM) y tipo de cambio (PN01207PM) son datos
# BCRP reales; la tasa de la FED (funds rate efectiva, promedio anual) es dato
# PÚBLICO de la Reserva Federal/FRED — FRED tiene salida bloqueada desde este
# entorno, así que se embeben valores de conocimiento público, DECLARADOS
# ILUSTRATIVOS (no descargados). El trilema: m50 (conocimiento general).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


# Tasa de la FED (effective federal funds rate, promedio anual, %). Dato público
# (Reserva Federal / FRED serie DFF); declarado ILUSTRATIVO — no descargado
# (FRED bloqueado desde este entorno). Valores de conocimiento público.
_FED = {2004: 1.35, 2005: 3.22, 2006: 4.97, 2007: 5.02, 2008: 1.92, 2009: 0.16,
        2010: 0.18, 2011: 0.10, 2012: 0.14, 2013: 0.11, 2014: 0.09, 2015: 0.13,
        2016: 0.40, 2017: 1.00, 2018: 1.83, 2019: 2.16, 2020: 0.38, 2021: 0.08,
        2022: 1.68, 2023: 5.03, 2024: 5.16}


def _series():
    anos_t, tasa = _datos_bcrp.serie("tasa_ref", anual=True)
    anos_e, tc = _datos_bcrp.serie("tipo_cambio", anual=True)
    anos = np.array(sorted(set(int(a) for a in anos_t) & set(_FED)))
    fed = np.array([_FED[int(a)] for a in anos])
    bcrp = np.array([tasa[list(anos_t).index(a)] for a in anos])
    tc_v = np.array([tc[list(anos_e).index(a)] for a in anos])
    return anos.astype(float), fed, bcrp, tc_v


def _idx(anos, p):
    a = int(p["anio_foco"])
    return int(list(anos.astype(int)).index(a)) if a in anos.astype(int) else len(anos) - 1


def _curvas(p):
    anos, fed, bcrp, tc = _series()
    return {"lineas": {"tasa de la FED (EE.UU., %)": (anos, fed, config.ROJO),
                       "tasa de referencia del BCRP (%)": (anos, bcrp, config.AZUL2)},
            "puntos": [(2009.0, float(fed[anos == 2009][0]), "2009-12: FED ≈ 0 → capital entra, sol ↑"),
                       (2023.0, float(fed[anos == 2023][0]), "2022-23: FED sube → BCRP sube")],
            "anotacion": (f"tasa FED (dato público) vs tasa BCRP (PD04722MM)\n"
                          f"corr $= {_datos_bcrp.correlacion(fed, bcrp):+.2f}$: el Perú sigue a la FED (trilema, m50)\n"
                          "cuenta de capitales abierta → autonomía limitada")}


def _resultados(p):
    anos, fed, bcrp, tc = _series()
    i = _idx(anos, p)
    return {"corr(FED, tasa BCRP)": float(_datos_bcrp.correlacion(fed, bcrp)),
            "corr(FED, tipo de cambio)": float(_datos_bcrp.correlacion(fed, tc)),
            "tipo de cambio 2009 (FED≈0, entra capital)": float(tc[anos == 2009][0]),
            "tipo de cambio 2012 (tras años de FED≈0)": float(tc[anos == 2012][0]),
            f"tasa FED {int(anos[i])} (%)": float(fed[i]),
            f"tasa BCRP {int(anos[i])} (%)": float(bcrp[i]),
            f"tipo de cambio {int(anos[i])}": float(tc[i])}


def _ecuaciones_calibradas(p):
    anos, fed, bcrp, tc = _series()
    return [f"corr(FED, BCRP) $= {_datos_bcrp.correlacion(fed, bcrp):+.2f}$ (trilema m50: autonomía limitada)",
            f"FED$\\downarrow \\Rightarrow$ capital entra $\\Rightarrow$ sol$\\uparrow$; FED$\\uparrow \\Rightarrow$ capital sale $\\Rightarrow$ sol$\\downarrow$"]


_P0 = {"anio_foco": 2023.0}


def _v_peru_sigue_fed():
    anos, fed, bcrp, tc = _series()
    c = _datos_bcrp.correlacion(fed, bcrp)
    return c > 0.4, \
        (f"la tasa del BCRP sigue en gran medida a la FED (corr {c:+.2f}): con cuenta de capitales abierta, "
         "el Perú no puede fijar su tasa ignorando a EE.UU. — el TRILEMA de m50 (autonomía monetaria limitada)")


def _v_fed_barato_capitales():
    anos, fed, bcrp, tc = _series()
    tc09 = float(tc[anos == 2009][0])
    tc12 = float(tc[anos == 2012][0])
    return tc12 < tc09, \
        (f"con la FED en ≈0 (2009-2012) el capital buscó rendimiento y fluyó al Perú: el sol se APRECIÓ "
         f"({tc09:.2f}→{tc12:.2f} S//US$) — dinero barato global infla los activos emergentes (m88 financiero)")


def _v_fed_sube_presiona():
    anos, fed, bcrp, tc = _series()
    c = _datos_bcrp.correlacion(fed, tc)
    return c > 0.25, \
        (f"cuando la FED sube, el sol se presiona (corr FED-tipo de cambio {c:+.2f}): tasas altas en EE.UU. "
         "atraen el capital de vuelta, fortalecen el dólar y debilitan al sol — el reverso del ciclo (2022-23)")


def _v_2021_idiosincratico():
    anos, fed, bcrp, tc = _series()
    fed21 = float(fed[anos == 2021][0])
    tc21 = float(tc[anos == 2021][0])
    tc19 = float(tc[anos == 2019][0])
    return fed21 < 0.5 and tc21 > tc19 + 0.3, \
        (f"2021 es el matiz de m104: la FED seguía en ≈0 ({fed21:.2f}%) y aun así el sol se debilitó "
         f"({tc19:.2f}→{tc21:.2f}) — el riesgo político interno (fuga de capitales) pesó MÁS que la FED: no todo es externo")


MODELO = Modelo(
    id="m111", nivel=12,
    nombre="FED → flujo de capitales hacia el Perú (BCRP)",
    xlabel="Año", ylabel="Tasa de interés (%)",
    parametros=[
        Parametro("anio_foco", _P0["anio_foco"], 2004, 2024, 1, "Año a destacar (ciclo de la FED)",
                  grupo="análisis", definicion="año a inspeccionar; 2009-12 FED≈0 (capital entra), 2022-23 FED sube"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto de la política monetaria y el tipo de cambio del Perú los decide, en realidad, la Reserva Federal de EE.UU.?",
        variables=[("i_FED", "tasa de la Reserva Federal de EE.UU. (dato público, ilustrativo)"),
                   ("i_BCRP", "tasa de referencia del BCRP (PD04722MM)"),
                   ("e", "tipo de cambio PEN/USD (PN01207PM)")],
        derivacion=["i_{FED}\\downarrow \\Rightarrow apetito\\;por\\;riesgo\\uparrow \\Rightarrow capital\\;entra\\;al\\;Perú \\Rightarrow e\\downarrow",
                    "i_{FED}\\uparrow \\Rightarrow capital\\;vuelve\\;a\\;EE.UU. \\Rightarrow dólar\\uparrow \\Rightarrow e\\uparrow",
                    "corr(i_{FED}, i_{BCRP}) \\approx +0.54 \\;(trilema\\;m50)",
                    "salvo\\;2021: \\;riesgo\\;idiosincrático > FED \\;(m104)"],
        contexto=("Este modelo es el complemento financiero de m110: si aquel "
                  "mostró el canal REAL del exterior (el cobre, las exportaciones), "
                  "este muestra el canal FINANCIERO, y su protagonista es la "
                  "Reserva Federal de Estados Unidos. La tasa de la FED es, en la "
                  "práctica, el precio del dinero global, y marca el pulso del "
                  "apetito por riesgo. Cuando la FED baja su tasa a casi cero —como "
                  "en 2009-2015 tras la crisis global, o en 2020-2021 por el COVID— "
                  "los inversionistas del mundo, insatisfechos con rendimientos "
                  "ínfimos en EE.UU., salen a buscar retorno en economías "
                  "emergentes; el capital fluye hacia el Perú, y el sol se aprecia "
                  "(entre 2009 y 2012 el tipo de cambio bajó de 3.01 a 2.64). "
                  "Cuando la FED sube agresivamente —como en 2022-2023, de 0 a más "
                  "de 5% para combatir la inflación post-COVID— el proceso se "
                  "invierte: el capital vuelve a EE.UU. atraído por tasas altas y "
                  "seguras, el dólar se fortalece globalmente y las monedas "
                  "emergentes, el sol incluido, se presionan. Y aquí aparece la "
                  "restricción profunda: el Perú NO puede fijar su tasa de interés "
                  "ignorando a la FED. Con una cuenta de capitales abierta, si el "
                  "BCRP mantuviera tasas muy por debajo de las de EE.UU., el capital "
                  "se iría y el sol colapsaría; por eso la tasa del BCRP sigue en "
                  "buena medida a la FED (correlación +0.54), y en 2022-2023 el BCRP "
                  "subió agresivamente en paralelo. Es el TRILEMA de la economía "
                  "abierta que construimos en m50: no se puede tener simultáneamente "
                  "tipo de cambio estable, libre movilidad de capitales y política "
                  "monetaria plenamente autónoma; el Perú, que eligió la movilidad "
                  "de capitales y una flotación administrada (m102), sacrifica parte "
                  "de su autonomía. Pero el modelo cierra con el matiz honesto de "
                  "m104: la FED no lo explica todo. En 2021 la FED seguía en cero y "
                  "sin embargo el sol se debilitó con fuerza, porque el riesgo "
                  "político interno (la incertidumbre electoral) provocó una fuga de "
                  "capitales que pesó más que el ciclo global. El destino financiero "
                  "del Perú lo escriben, en distintos momentos, Washington y Lima."),
        autores=("Datos: BCRP (PD04722MM tasa de referencia, PN01207PM tipo de "
                 "cambio) reales; tasa de la FED = dato público (Reserva "
                 "Federal/FRED), declarado ilustrativo (no descargado, FRED "
                 "bloqueado); el trilema: m50; el enfoque de activos y la fuga "
                 "idiosincrática: m104, m111 (conocimiento general)."),
        supuestos=[
            "La tasa de la FED se embebe como dato público ILUSTRATIVO (promedio anual de la funds rate efectiva): no se descargó (FRED bloqueado desde este entorno); los valores son de conocimiento público.",
            "La correlación FED-BCRP (+0.54) documenta la restricción del trilema (m50); no es una estimación estructural de la reacción del BCRP (que también responde a su propia inflación, m100).",
            "El canal opera vía la cuenta de capitales (m50): flujos que buscan rendimiento; se ilustra con tasas y tipo de cambio, no con la serie de flujos en sí.",
        ],
        ecuaciones=[
            Ecuacion("i_{FED}\\downarrow \\Rightarrow capital\\;entra \\Rightarrow e\\downarrow \\;(sol\\;se\\;aprecia)", "dinero barato global",
                     "con la FED en ≈0, el capital busca rendimiento en emergentes y fluye al Perú: el sol "
                     "se aprecia (2009-2012, 3.01→2.64) — el auge financiero externo (m88 financiero)."),
            Ecuacion("corr(i_{FED}, \\; i_{BCRP}) \\approx +0.54", "el trilema (m50)",
                     "con cuenta de capitales abierta, el BCRP no puede ignorar a la FED: debe seguirla en "
                     "parte para defender al sol — autonomía monetaria limitada (m50)."),
            Ecuacion("2021: \\;i_{FED}\\approx 0 \\;pero\\; e\\uparrow \\;(riesgo\\;político)", "no todo es la FED (m104)",
                     "en 2021 la FED estaba en cero y aun así el sol se debilitó: la fuga de capitales por "
                     "riesgo político interno pesó más que el ciclo global — el matiz idiosincrático de m104."),
        ],
        intuicion=("La imagen es la de dos tasas que se mueven casi en espejo con "
                   "un rezago: la FED marca el compás y el BCRP, aunque con su "
                   "propia agenda (la inflación peruana, m100), no puede alejarse "
                   "demasiado. Para un país emergente, esto es a la vez una fuente "
                   "de recursos y una vulnerabilidad. En los años de dinero barato "
                   "global, el capital abundante financia inversión y aprecia la "
                   "moneda —se siente como prosperidad—, pero es prestada: cuando la "
                   "FED gira, el mismo capital se va, y el país que se acostumbró al "
                   "flujo sufre. Por eso las economías emergentes prudentes "
                   "construyen defensas contra el ciclo de la FED: reservas "
                   "internacionales (que el Perú acumuló, m86), flotación que "
                   "absorbe el golpe (m102), baja deuda en dólares y credibilidad "
                   "(m108). El Perú capeó relativamente bien el giro de 2022-2023 "
                   "—subió su tasa a tiempo y el sol se mantuvo— justamente por esas "
                   "defensas. Y la lección de m104-m111 juntos: el tipo de cambio y "
                   "las condiciones financieras del Perú dependen de dos fuerzas —la "
                   "FED (global) y el riesgo país (local)—, y saber cuál manda en "
                   "cada momento es clave. En 2013 y 2022 mandó la FED; en 2021, la "
                   "política peruana. Culpar siempre a una sola es el error."),
        equilibrio=("No hay equilibrio que resolver: es la relación empírica entre "
                    "la FED, la tasa del BCRP y el tipo de cambio. El resultado es "
                    "que el Perú sigue en parte a la FED (corr +0.54, trilema m50) y "
                    "su moneda responde al ciclo global (corr FED-tipo de cambio "
                    "+0.42), salvo cuando el riesgo idiosincrático domina (2021, m104)."),
        limitaciones=[
            "Tasa de la FED ilustrativa (no descargada): los valores son públicos y bien conocidos, pero el modelo no los adquiere por conector (FRED bloqueado) — procedencia declarada.",
            "Sin la serie de flujos de capital: el canal (cuenta financiera) se INFIERE de tasas y tipo de cambio, no se mide directamente (la cuenta financiera del BCRP es trimestral desde 2012).",
            "La reacción del BCRP mezcla el trilema (seguir a la FED) con su propia regla de inflación (m100): la correlación +0.54 no separa ambos motivos.",
        ],
        evolucion=("Completa la dimensión externa: m110 el canal real (comercio), "
                   "m111 el financiero (capitales/FED). Retoma el trilema de m50 con "
                   "datos y el enfoque de activos de m104 (el tipo de cambio como "
                   "precio financiero), y motiva las defensas del Perú —reservas "
                   "(m86), flotación (m102), baja deuda (m108)—. Con el shock externo "
                   "en sus dos caras cubierto, el nivel avanza a los canales "
                   "sectoriales (m112 minería, m113 inflación importada) y al cierre "
                   "sintético (m115)."),
    ),
    escenarios=[
        Escenario("dinero_barato", "la FED en ≈0: capital entra (2009-2015)",
                  {"anio_foco": 2012.0},
                  "con la FED en casi cero tras la crisis global, el capital busca "
                  "rendimiento en emergentes: fluye al Perú, aprecia el sol "
                  "(3.01→2.64) y abarata el crédito. Prosperidad financiada por "
                  "dinero barato global — pero prestado.",
                  cadena=["la FED baja a ≈0 (crisis global, 2009+)", "el capital busca rendimiento en emergentes",
                          "fluye al Perú (cuenta de capitales abierta)", "el sol se aprecia (3.01→2.64), crédito barato",
                          "auge financiado por dinero global — reversible"]),
        Escenario("giro_2022", "la FED sube: capital sale (2022-2023)",
                  {"anio_foco": 2023.0},
                  "la FED sube de 0 a más de 5% para domar la inflación; el capital "
                  "vuelve a EE.UU., el dólar se fortalece y el BCRP debe subir su "
                  "tasa en paralelo (a 7.5%) para defender al sol. El trilema (m50) "
                  "en acción — autonomía limitada.",
                  cadena=["la FED sube agresivamente (2022-23, a 5%)", "el capital vuelve a EE.UU. (tasas altas y seguras)",
                          "el dólar se fortalece, presiona al sol", "el BCRP debe subir su tasa (a 7.5%) para defenderlo",
                          "el trilema (m50): no se ignora a la FED"]),
        Escenario("idiosincratico_2021", "cuando manda el riesgo local (2021, m104)",
                  {"anio_foco": 2021.0},
                  "2021: la FED seguía en cero, pero el sol se debilitó igual —la "
                  "incertidumbre política interna provocó fuga de capitales—. El "
                  "recordatorio de m104: a veces el riesgo país pesa más que la "
                  "FED; no todo lo financiero viene de afuera.",
                  cadena=["la FED aún en ≈0 (2021)", "pero crisis política interna (elección)",
                          "fuga de capitales por riesgo país (m104)", "el sol se debilita PESE a la FED laxa",
                          "el riesgo local pesó más que el global — no todo es la FED"]),
    ],
    verificaciones=[
        Verificacion("el Perú sigue en parte a la FED (trilema, m50)", _v_peru_sigue_fed),
        Verificacion("FED barata (2009-12) → capital entra, sol se aprecia", _v_fed_barato_capitales),
        Verificacion("FED al alza → sol presionado (2022-23)", _v_fed_sube_presiona),
        Verificacion("2021: el riesgo local pesó más que la FED (m104)", _v_2021_idiosincratico),
    ],
    notas="El canal financiero externo: la FED marca los flujos de capital y el Perú la sigue en parte (corr +0.54, trilema m50). FED≈0 → capital entra, sol↑; FED↑ → capital sale, sol↓. Salvo 2021: mandó el riesgo político local (m104).",
)
