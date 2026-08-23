# m104_cobre_tipo_cambio.py — el cobre y el tipo de cambio (nivel 12).
#
# La teoría (m43, m89) predice un canal claro: si sube el cobre, el Perú recibe
# más dólares, el sol se aprecia y el tipo de cambio (PEN/USD) BAJA — una
# correlación NEGATIVA. Pero los datos crudos del BCRP la desmienten: en niveles
# la correlación cobre-tipo de cambio es +0.12 (¡positiva!). ¿Falla la teoría?
# No: falla la lectura ingenua. El modelo muestra tres capas:
#   (1) en NIVELES la correlación es ~0 (engañosa: hay tendencias y confusores);
#   (2) en CAMBIOS (Δ) aparece el signo teórico, −0.19, pero débil;
#   (3) al EXCLUIR 2020-2021 (COVID + crisis política, años de fuga de capitales)
#       el canal se fortalece a −0.45 — en años normales el terms-of-trade manda.
# El año 2021 es el dato más informativo: cobre en RÉCORD (+51%) y sol DÉBIL
# (+11%). El tipo de cambio es un precio de ACTIVO: la cuenta de capitales (m111,
# fuga por riesgo político m74) puede vencer al canal comercial.
#
# Procedencia: datos BCRP PN01652XM (cobre) y PN01207PM (tipo de cambio), muestra
# 2004-2024. El canal comercial: m43/m89; el enfoque de activos (la cuenta de
# capitales domina en el corto plazo): m111 (conocimiento general). Correlación
# descriptiva, no causal (regla del pipeline).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _series():
    anos, cobre, tc = _datos_bcrp.alinear("cobre", "tipo_cambio")
    dc = np.diff(cobre) / cobre[:-1] * 100          # var% cobre
    dtc = np.diff(tc) / tc[:-1] * 100               # var% tipo de cambio
    return anos, cobre, tc, anos[1:], dc, dtc


def _corr_cambios(excluir_crisis):
    anos, cobre, tc, ax, dc, dtc = _series()
    if excluir_crisis:
        m = (ax != 2020) & (ax != 2021)             # años de fuga de capitales (COVID+política)
        return _datos_bcrp.correlacion(dc[m], dtc[m])
    return _datos_bcrp.correlacion(dc, dtc)


def _curvas(p):
    anos, cobre, tc, ax, dc, dtc = _series()
    excl = bool(int(p["excluir_crisis"]))
    corr = _corr_cambios(excl)
    corr_nivel = _datos_bcrp.correlacion(cobre, tc)
    return {"lineas": {"variación del precio del cobre (BCRP, %)": (ax, dc, config.DORADO),
                       "variación del tipo de cambio (BCRP, %)": (ax, dtc, config.ROJO)},
            "puntos": [(2021.0, float(dtc[ax == 2021][0]),
                        "2021: cobre récord, sol débil"),
                       (2015.0, float(dtc[ax == 2015][0]),
                        "2015: cobre cae, sol se debilita")],
            "anotacion": (f"cobre (PN01652XM) vs tipo de cambio (PN01207PM)\n"
                          f"corr en NIVELES = {corr_nivel:+.2f} (engañosa)\n"
                          f"corr en CAMBIOS = {corr:+.2f} "
                          f"({'sin 2020-21' if excl else 'todos los años'})")}


def _resultados(p):
    anos, cobre, tc, ax, dc, dtc = _series()
    return {"corr en niveles (cobre, TC)": float(_datos_bcrp.correlacion(cobre, tc)),
            "corr en cambios, todos los años": float(_corr_cambios(False)),
            "corr en cambios, sin 2020-21 (crisis)": float(_corr_cambios(True)),
            "Δcobre 2021 (%)": float(dc[ax == 2021][0]),
            "ΔTC 2021 (%)": float(dtc[ax == 2021][0]),
            "TC medio 2004-2024 (PEN/USD)": float(tc.mean())}


def _ecuaciones_calibradas(p):
    corr_t = _corr_cambios(False)
    corr_e = _corr_cambios(True)
    return [f"corr en niveles $= {_datos_bcrp.correlacion(*_datos_bcrp.alinear('cobre','tipo_cambio')[1:]):+.2f}$ "
            f"(engañosa) vs corr en cambios $= {corr_t:+.2f}$",
            f"sin 2020-21 (fuga de capitales): corr $= {corr_e:+.2f}$ — el canal comercial (m89) SÍ opera"]


_P0 = {"excluir_crisis": 0.0}


def _v_nivel_enganoso():
    corr = _datos_bcrp.correlacion(*_datos_bcrp.alinear("cobre", "tipo_cambio")[1:])
    return corr > -0.1, \
        (f"en NIVELES la correlación cobre-tipo de cambio es {corr:+.2f} (~0, incluso positiva): "
         "engañosa — la teoría (m43/m89) predice negativa, pero los niveles tienen tendencias y confusores")


def _v_cambios_signo_teorico():
    corr = _corr_cambios(False)
    return corr < 0, \
        (f"en CAMBIOS aparece el signo teórico (corr {corr:+.2f} < 0): cobre↑ → más dólares → sol se aprecia "
         "→ tipo de cambio BAJA (m43/m89) — pero el canal es débil en la muestra completa")


def _v_excluir_crisis_fortalece():
    todos = _corr_cambios(False)
    excl = _corr_cambios(True)
    return excl < todos and excl < -0.35, \
        (f"al excluir 2020-21 (fuga de capitales) el canal se fortalece: corr {excl:+.2f} < {todos:+.2f}: "
         "en años NORMALES el terms-of-trade (m89) sí manda sobre el tipo de cambio")


def _v_2021_contraejemplo():
    anos, cobre, tc, ax, dc, dtc = _series()
    d21 = float(dc[ax == 2021][0])
    t21 = float(dtc[ax == 2021][0])
    return d21 > 30 and t21 > 5, \
        (f"2021 es el contraejemplo: cobre {d21:+.0f}% (récord) y sol {t21:+.0f}% (débil) A LA VEZ — "
         "el tipo de cambio es un precio de ACTIVO: la fuga de capitales por riesgo político (m74, m111) venció al cobre")


MODELO = Modelo(
    id="m104", nivel=12,
    nombre="Precio del cobre → tipo de cambio (BCRP)",
    xlabel="Año", ylabel="Variación anual (%)",
    parametros=[
        Parametro("excluir_crisis", _P0["excluir_crisis"], 0, 1, 1,
                  "Excluir 2020-21 (años de fuga de capitales)",
                  grupo="análisis",
                  definicion="COVID + crisis política: años en que la cuenta de capitales (m111) rompió el canal comercial"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si el cobre alto trae dólares y fortalece al sol, ¿por qué en 2021 el cobre estuvo en récord y el sol se debilitó?",
        variables=[("cobre_t", "precio del cobre, ¢US$/lb (BCRP PN01652XM)"),
                   ("e_t", "tipo de cambio PEN/USD (BCRP PN01207PM)"),
                   ("2021", "el contraejemplo: cobre récord + sol débil = fuga de capitales (m111)")],
        derivacion=["teoría (m43/m89): \\;cobre\\uparrow \\to dólares\\uparrow \\to sol\\;se\\;aprecia \\to e\\downarrow \\;(corr<0)",
                    "datos\\;en\\;niveles: \\;corr \\approx +0.12 \\;(engañosa)",
                    "en\\;cambios\\;sin\\;2020\\text{-}21: \\;corr \\approx -0.45 \\;(el\\;canal\\;SÍ\\;opera)"],
        contexto=("Este modelo es una de las lecciones econométricas más valiosas "
                  "del laboratorio, y nace de una paradoja en los datos. La teoría "
                  "de la economía abierta (m43) y del canal del cobre (m89) predice "
                  "algo intuitivo: cuando sube el precio del cobre, el Perú exporta "
                  "por más valor, entran más dólares, el sol se fortalece y el tipo "
                  "de cambio (soles por dólar) BAJA. Es decir, cobre y tipo de "
                  "cambio deberían correlacionar NEGATIVAMENTE. Pero al mirar los "
                  "datos crudos del BCRP en niveles, la correlación es +0.12: "
                  "positiva, el signo equivocado. ¿Se equivoca la teoría? No — se "
                  "equivoca la lectura ingenua, y desenredarlo enseña tres cosas. "
                  "PRIMERO, en niveles casi todo correlaciona con casi todo por "
                  "tendencias comunes y confusores (el dólar global, la inflación de "
                  "EE.UU.): la correlación de niveles es tramposa, como ya enseñó "
                  "m101. SEGUNDO, al mirar los CAMBIOS año a año aparece el signo "
                  "teórico, −0.19, aunque débil. TERCERO, y decisivo: al excluir "
                  "2020 y 2021 —los años de COVID y la crisis política, cuando hubo "
                  "fuga masiva de capitales— la correlación se fortalece a −0.45. "
                  "Esto revela que en años NORMALES el canal comercial del cobre sí "
                  "gobierna el tipo de cambio, pero en años de estrés otra fuerza lo "
                  "domina. El año 2021 es el dato más informativo de toda la serie: "
                  "el cobre estuvo en RÉCORD (+51%) y aun así el sol se DEBILITÓ "
                  "(+11%), porque la incertidumbre política (elección de 2021) "
                  "provocó una salida de capitales (m74, m111) que superó con creces "
                  "la entrada de dólares del cobre. La lección de fondo: el tipo de "
                  "cambio NO es solo un precio comercial, es un precio de ACTIVO "
                  "financiero. En el corto plazo lo mueve la cuenta de capitales "
                  "—las expectativas, el riesgo, el dólar global (m111)— más que la "
                  "balanza comercial. El cobre importa, pero un país puede tener "
                  "términos de intercambio excelentes y una moneda débil si el "
                  "capital huye."),
        autores=("Datos: BCRP (PN01652XM cobre, PN01207PM tipo de cambio); el canal "
                 "comercial: m43/m89; el enfoque de activos del tipo de cambio (la "
                 "cuenta de capitales domina en el corto plazo): m111 / Dornbusch "
                 "(conocimiento general); niveles vs cambios: m101."),
        supuestos=[
            "La correlación es descriptiva, no un modelo estructural del tipo de cambio (que necesitaría el diferencial de tasas, el dólar global, el riesgo país).",
            "2020-21 se marcan como años de 'fuga de capitales' (COVID + crisis política): es una lectura histórica razonable, no una prueba econométrica de quiebre estructural.",
            "El tipo de cambio nominal PEN/USD (no el real): el canal de términos de intercambio opera en rigor sobre el real, pero la lección de niveles-vs-cambios y del rol del capital es válida.",
        ],
        ecuaciones=[
            Ecuacion("corr_{niveles}(cobre, e) \\approx +0.12 \\;\\neq\\; teoría", "la paradoja",
                     "en niveles la correlación tiene el signo equivocado: tendencias y confusores "
                     "(el dólar global) dominan — la trampa de correlacionar niveles (m101)."),
            Ecuacion("corr_{cambios,\\;sin\\;2020\\text{-}21}(cobre, e) \\approx -0.45", "el canal recuperado",
                     "en cambios y sin los años de crisis aparece el signo teórico y fuerte: cobre↑ → "
                     "sol se aprecia → e↓ (m43/m89) — el canal comercial sí opera en años normales."),
            Ecuacion("2021: \\;\\Delta cobre = +51\\%, \\;\\Delta e = +11\\%", "el capital vence al comercio",
                     "cobre récord con sol débil: el tipo de cambio es un precio de activo, la fuga "
                     "de capitales por riesgo político (m74, m111) superó la entrada de dólares del cobre."),
        ],
        intuicion=("La imagen que queda es la del año 2021: los titulares decían "
                   "'cobre en máximos históricos' y al mismo tiempo 'el dólar sube, "
                   "el sol se debilita'. Para el lector ingenuo, contradictorio; "
                   "para el economista, la lección central de la macro financiera. "
                   "El tipo de cambio no es el precio de la balanza comercial de "
                   "este mes, es el precio de un ACTIVO —tener soles versus tener "
                   "dólares— y ese precio lo fija sobre todo la expectativa: si el "
                   "capital cree que el Perú se volvió más riesgoso, vende soles hoy "
                   "aunque el cobre esté regalando dólares. Por eso el canal del "
                   "cobre sobre el tipo de cambio es real (−0.45 en años normales) "
                   "pero frágil: cualquier shock a la cuenta de capitales (una "
                   "elección, la Fed subiendo tasas m111, un pánico global m88) lo "
                   "puede invertir. Es también, una vez más, la lección de "
                   "niveles-vs-cambios de m101: la correlación cruda de niveles "
                   "(+0.12) mentía; había que mirar los cambios y pensar en los "
                   "confusores. El estudiante que internaliza este modelo ya no lee "
                   "'el cobre subió, entonces el sol se fortalecerá' como una ley — "
                   "sabe preguntar qué está haciendo el capital."),
        equilibrio=("No hay equilibrio que resolver: es la relación empírica entre "
                    "el precio del cobre y el tipo de cambio. El resultado es que el "
                    "canal comercial (cobre↑→e↓) existe pero es débil en la muestra "
                    "completa (−0.19) y fuerte solo en años normales (−0.45): en las "
                    "crisis la cuenta de capitales (m111) lo domina."),
        limitaciones=[
            "Bivariado: un modelo serio del tipo de cambio incluye el diferencial de tasas (m111), el dólar global (DXY) y el riesgo país — el cobre es un factor, no el modelo.",
            "La exclusión de 2020-21 es una decisión de lectura histórica, no un test formal de quiebre estructural (Chow, etc.): ilustra, no prueba.",
            "Tipo de cambio nominal, muestra anual: el canal de términos de intercambio opera sobre el real y a mayor frecuencia; aquí se ve la idea, no la magnitud precisa.",
        ],
        evolucion=("Complementa m103 (cobre→crecimiento, donde el canal es fuerte) "
                   "mostrando que sobre el TIPO DE CAMBIO el mismo cobre pesa menos "
                   "y se rompe en las crisis — porque el tipo de cambio es un precio "
                   "de activo (m111). Prepara m105 (términos de intercambio "
                   "completos) y, sobre todo, m111 (FED → flujo de capitales), donde "
                   "la cuenta de capitales que aquí rompió el canal es la "
                   "protagonista."),
    ),
    escenarios=[
        Escenario("todos", "correlación en cambios, todos los años",
                  {"excluir_crisis": 0.0},
                  "con toda la muestra la correlación es −0.19: el signo teórico "
                  "aparece, pero débil — los años de crisis (2020-21) lo diluyen.",
                  cadena=["mirar los cambios de todos los años", "corr −0.19 (signo teórico, débil)",
                          "2020-21 (fuga de capitales) diluyen el canal", "la balanza comercial no es toda la historia"]),
        Escenario("sin_crisis", "excluir 2020-21 (años de fuga de capitales)",
                  {"excluir_crisis": 1.0},
                  "al quitar los dos años de fuga de capitales la correlación salta "
                  "a −0.45: en años NORMALES el cobre sí gobierna el tipo de cambio "
                  "(m89) — la crisis, no el comercio, era la excepción.",
                  cadena=["excluir 2020-21 (COVID + crisis política)", "corr salta a −0.45 (canal fuerte)",
                          "en años normales el terms-of-trade manda (m89)", "en crisis la cuenta de capitales domina (m111)"]),
    ],
    verificaciones=[
        Verificacion("en niveles la correlación es engañosa (~0)", _v_nivel_enganoso),
        Verificacion("en cambios aparece el signo teórico (<0)", _v_cambios_signo_teorico),
        Verificacion("excluir 2020-21 fortalece el canal a −0.45", _v_excluir_crisis_fortalece),
        Verificacion("2021: cobre récord + sol débil (m111)", _v_2021_contraejemplo),
    ],
    notas="El tipo de cambio es un precio de ACTIVO: el canal del cobre (m89) opera en años normales (−0.45) pero la fuga de capitales (m111) lo rompe (2021). Niveles engañan (m101).",
)
