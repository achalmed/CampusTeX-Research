# m89_caida_cobre.py — caída del precio del cobre (nivel 11).
#
# El reverso de m88 y el PRELUDIO PERUANO de m103. Una caída del precio del
# cobre golpea a un exportador por TRES canales simultáneos:
#   (1) EXTERNO: ↓exportaciones → ↓CC → presión cambiaria (m43, m75)
#   (2) FISCAL: ↓recaudación minera → ↓ingresos → ajuste o déficit (m62)
#   (3) REAL: ↓inversión minera → ↓demanda agregada → recesión (m10)
# El daño depende de si el país AHORRÓ en el boom (m88): con fondo de
# estabilización, el golpe fiscal se amortigua; sin él, hay que recortar en
# recesión (prociclicidad). Es el shock que el Perú enfrenta recurrentemente
# — 2014-2016, 2020 — y el caso que m103 estimará con datos del BCRP.
#
# Procedencia: transmisión de términos de intercambio a un exportador (m105);
# los tres canales son m43/m62/m10 — conocimiento general; calibración
# didáctica que EVOCA la estructura peruana (NO datos oficiales).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _canales(p):
    caida = -abs(p["caida_precio"])                       # negativo
    externo = caida * p["peso_export"] / 100              # golpe a la CC
    fiscal_bruto = caida * p["peso_fiscal"] / 100         # golpe a ingresos
    fiscal_neto = fiscal_bruto * (1 - p["fondo"] / 100)   # amortiguado por el fondo
    real = caida * p["peso_inversion"] / 100              # golpe a la inversión
    total = externo + fiscal_neto + real
    return dict(externo=externo, fiscal_bruto=fiscal_bruto, fiscal_neto=fiscal_neto,
                real=real, total=total)


def _curvas(p):
    c = _canales(p)
    cats = ["externo\n(CC, m43)", "fiscal neto\n(m62)", "real\n(inversión, m10)",
            "impacto\ntotal"]
    vals = [c["externo"], c["fiscal_neto"], c["real"], c["total"]]
    cols = [config.AZUL2, config.DORADO, config.VERDE, config.ROJO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"cobre {p['caida_precio']:+.0f}% "
                          f"(shock a un exportador)\n"
                          f"fondo de estabilización: {p['fondo']:.0f}% amortigua el fiscal\n"
                          f"impacto total sobre Y: {c['total']:+.1f}% (los TRES canales)")}


def _resultados(p):
    c = _canales(p)
    return {"canal externo (CC)": c["externo"],
            "canal fiscal bruto": c["fiscal_bruto"],
            "canal fiscal neto (con fondo)": c["fiscal_neto"],
            "canal real (inversión)": c["real"],
            "impacto total sobre Y (%)": c["total"],
            "amortiguación del fondo": c["fiscal_bruto"] - c["fiscal_neto"]}


def _ecuaciones_calibradas(p):
    c = _canales(p)
    return [f"externo $= {p['caida_precio']:+.0f}\\%\\times{p['peso_export']:.0f}\\% = {c['externo']:.1f}$",
            f"fiscal neto $= bruto\\times(1-{p['fondo'] / 100:.2f}) = {c['fiscal_neto']:.1f}$",
            f"total $= {c['total']:+.1f}\\%$ de Y"]


_P0 = {"caida_precio": 30.0, "peso_export": 25.0, "peso_fiscal": 15.0,
       "peso_inversion": 10.0, "fondo": 40.0}


def _v_tres_canales():
    c = _canales(_P0)
    return c["externo"] < 0 and c["fiscal_neto"] < 0 and c["real"] < 0, \
        (f"la caída golpea por TRES canales a la vez (externo {c['externo']:.1f}, fiscal "
         f"{c['fiscal_neto']:.1f}, real {c['real']:.1f}): por eso un shock de cobre duele tanto")


def _v_fondo_amortigua():
    c_con = _canales(dict(_P0, fondo=70.0))
    c_sin = _canales(dict(_P0, fondo=0.0))
    return c_con["total"] > c_sin["total"], \
        (f"el fondo de estabilización amortigua el golpe fiscal (total {c_sin['total']:.1f}→"
         f"{c_con['total']:.1f}): lo ahorrado en el boom (m88) paga en la caída")


def _v_prociclicidad_sin_fondo():
    c = _canales(dict(_P0, fondo=0.0))
    return c["fiscal_neto"] == c["fiscal_bruto"], \
        ("sin fondo, el golpe fiscal es pleno: hay que recortar gasto en plena recesión — "
         "la prociclicidad que m68 advierte y m88 pudo evitar ahorrando")


def _v_estructura_amplifica():
    c_diversif = _canales(dict(_P0, peso_export=15.0, peso_fiscal=8.0))
    c_concentr = _canales(dict(_P0, peso_export=35.0, peso_fiscal=25.0))
    return abs(c_concentr["total"]) > abs(c_diversif["total"]), \
        (f"cuanto más concentrada la economía en el cobre, mayor el golpe "
         f"({c_diversif['total']:.1f} vs {c_concentr['total']:.1f}): la diversificación como seguro")


MODELO = Modelo(
    id="m89", nivel=11,
    nombre="Caída del precio del cobre",
    xlabel="", ylabel="Impacto sobre el producto (% PIB)",
    parametros=[
        Parametro("caida_precio", _P0["caida_precio"], 5, 60, 5, "Caída del precio del cobre (%)",
                  grupo="shock", definicion="reversión del ciclo de commodities (m105)"),
        Parametro("fondo", _P0["fondo"], 0, 100, 10, "Fondo de estabilización disponible (%)",
                  grupo="defensa", definicion="lo ahorrado en el boom (m88): amortigua el fiscal"),
        Parametro("peso_export", _P0["peso_export"], 10, 40, 5, "Peso del cobre en exportaciones (%)",
                  grupo="estructura", definicion="canal externo (m43)"),
        Parametro("peso_fiscal", _P0["peso_fiscal"], 5, 30, 5, "Peso minero en ingresos fiscales (%)",
                  grupo="estructura", definicion="canal fiscal (m62)"),
        Parametro("peso_inversion", _P0["peso_inversion"], 3, 20, 1, "Peso de la inversión minera (%)",
                  grupo="estructura", definicion="canal real (m10)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué una caída del precio del cobre golpea al Perú por tres frentes a la vez — y qué lo amortigua?",
        variables=[("externo, fiscal, real", "los TRES canales simultáneos del shock"),
                   ("fondo", "lo ahorrado en el boom (m88): el amortiguador"),
                   ("estructura", "cuánto pesa el cobre: la concentración como vulnerabilidad")],
        derivacion=["cobre\\downarrow \\Rightarrow (1)\\;X\\downarrow\\;(CC, m43) + (2)\\;ingresos\\downarrow\\;(m62) + (3)\\;inversión\\downarrow\\;(m10)",
                    "fiscal\\;neto = fiscal\\;bruto\\times(1 - fondo)",
                    "total = externo + fiscal\\;neto + real"],
        contexto=("La caída del precio del cobre es el shock externo que el Perú "
                  "enfrenta recurrentemente — y el reverso exacto del boom de m88. "
                  "Golpea por tres canales simultáneos, lo que explica por qué duele "
                  "tanto: el canal EXTERNO (menos exportaciones deterioran la cuenta "
                  "corriente y presionan el tipo de cambio, m43/m75), el canal "
                  "FISCAL (la recaudación minera cae y obliga a ajustar o "
                  "endeudarse, m62) y el canal REAL (la inversión minera se frena y "
                  "contrae la demanda agregada, m10). El daño total depende "
                  "críticamente de si el país AHORRÓ durante el boom: con un fondo "
                  "de estabilización (m88), el golpe fiscal se amortigua y el "
                  "gobierno puede sostener el gasto en la caída; sin él, hay que "
                  "recortar en plena recesión — la prociclicidad que m68 advierte. "
                  "El Perú vivió este shock en 2014-2016 (fin del superciclo) y en "
                  "2020, con resultados mixtos: reservas y reglas fiscales "
                  "amortiguaron, pero la dependencia estructural del cobre sigue "
                  "siendo la vulnerabilidad de fondo. Este es el modelo que m103 "
                  "estimará con datos reales del BCRP: la elasticidad del "
                  "crecimiento peruano al precio del cobre."),
        autores=("Transmisión de términos de intercambio (m105); los tres canales "
                 "son m43/m62/m10; el ángulo peruano es conocimiento general — los "
                 "datos oficiales entran en m103 (nivel 12)."),
        supuestos=[
            "Los tres canales son aditivos y lineales: la realidad tiene interacciones (la presión cambiaria puede gatillar salida de capitales, m87).",
            "El fondo amortigua solo el canal fiscal: en la práctica las reservas también amortiguan el externo (m50).",
            "Calibración que EVOCA la estructura peruana (pesos del cobre) pero NO son datos oficiales — esos entran en m103 bajo la política solo-ejemplos.",
        ],
        ecuaciones=[
            Ecuacion("impacto = externo + fiscal_{neto} + real", "los tres canales sumados",
                     "un shock de commodities no es UN golpe sino tres coordinados — por eso los "
                     "exportadores concentrados son tan cíclicos (verificado)."),
            Ecuacion("fiscal_{neto} = fiscal_{bruto}\\times(1 - fondo)", "el amortiguador",
                     "lo ahorrado en el boom (m88) paga en la caída: el fondo convierte un ajuste "
                     "procíclico en uno suave — la conexión m88↔m89↔m68 (verificado)."),
        ],
        intuicion=("La caída del cobre enseña que la vulnerabilidad de un exportador "
                   "de commodities no es un evento sino una ESTRUCTURA: mientras el "
                   "cobre pese un cuarto de las exportaciones, un sexto de los "
                   "ingresos fiscales y una parte grande de la inversión, el ciclo "
                   "del precio internacional ES el ciclo económico del país. Hay "
                   "dos defensas, una de corto y una de largo plazo. La de corto es "
                   "el fondo de estabilización (m88): ahorrar en las vacas gordas "
                   "para no recortar en las flacas — romper la prociclicidad. La de "
                   "largo es la DIVERSIFICACIÓN: reducir el peso del cobre para que "
                   "su precio importe menos, lo que exige desarrollar otros "
                   "transables (agroexportación, manufactura) — precisamente lo que "
                   "la enfermedad holandesa del boom (m88) dificulta. Es el dilema "
                   "estructural del Perú: el mismo recurso que lo enriquece lo hace "
                   "vulnerable, y salir de esa dependencia es la tarea de desarrollo "
                   "de fondo (m97, m112)."),
        equilibrio=("El impacto total es la suma de los tres canales, amortiguada "
                    "por el fondo (verificado). La diferencia entre una economía "
                    "con fondo y sin fondo es la diferencia entre un ajuste suave y "
                    "una recesión con recorte fiscal procíclico."),
        limitaciones=[
            "Estático: la dinámica (cuánto dura la recesión, si gatilla salida de capitales m87) exige el aparato completo — aquí es el impacto.",
            "Calibración ilustrativa, NO datos peruanos: la elasticidad real cobre→PIB es m103 con series del BCRP.",
            "Sin política monetaria: el BCRP responde (baja la tasa, m38; deja depreciar, m86) — aquí el shock es 'puro'.",
        ],
        evolucion=("Es el reverso de m88 y el preludio directo de m103 (el modelo "
                   "peruano del cobre con datos). Combina m43 (externo), m62 "
                   "(fiscal) y m10 (real) en un shock estructural, y muestra por "
                   "qué el fondo de m88/m68 importa. En el nivel 12: m103 (cobre→"
                   "crecimiento), m104 (cobre→tipo de cambio), m105 (términos de "
                   "intercambio)."),
    ),
    escenarios=[
        Escenario("fin_del_superciclo", "caída del 30% con fondo moderado (40%)",
                  {"caida_precio": 30.0, "fondo": 40.0},
                  "los tres canales golpean pero el fondo amortigua el fiscal: el "
                  "shock de 2014-2016 con colchón — recesión suave, no crisis.",
                  cadena=["fin del boom del cobre (m105)", "↓X (externo) + ↓ingresos (fiscal) + ↓inversión (real)",
                          "el fondo amortigua el canal fiscal (m88)", "ajuste manejable",
                          "sin recorte procíclico brutal"]),
        Escenario("sin_ahorro_previo", "la misma caída sin fondo (0%)",
                  {"caida_precio": 30.0, "fondo": 0.0},
                  "el golpe fiscal es pleno: hay que recortar gasto en recesión — la "
                  "prociclicidad que convierte el shock en crisis (la lección de "
                  "no ahorrar en el boom).",
                  cadena=["caída del cobre", "sin fondo de estabilización",
                          "el golpe fiscal es pleno", "recorte de gasto en recesión",
                          "prociclicidad: el shock amplificado (m68)"]),
        Escenario("colapso_2020", "caída severa del 45% (crisis global)",
                  {"caida_precio": 45.0, "fondo": 40.0},
                  "un shock grande pone a prueba el colchón: incluso con fondo, una "
                  "caída severa golpea fuerte — el límite de la amortiguación.",
                  cadena=["shock global severo (COVID, m81)", "cobre se desploma",
                          "los tres canales golpean fuerte", "el fondo ayuda pero no basta",
                          "recesión significativa pese al colchón"]),
        Escenario("economia_diversificada", "menor peso del cobre (export 15%, fiscal 8%)",
                  {"peso_export": 15.0, "peso_fiscal": 8.0},
                  "el mismo shock de precio golpea mucho menos: la diversificación "
                  "reduce la exposición estructural — la defensa de largo plazo "
                  "(m97, m112).",
                  cadena=["misma caída del precio", "pero menor peso del cobre en la economía",
                          "los tres canales golpean menos", "shock amortiguado por estructura",
                          "la diversificación como seguro permanente"]),
    ],
    verificaciones=[
        Verificacion("golpea por tres canales a la vez", _v_tres_canales),
        Verificacion("el fondo amortigua el golpe fiscal (m88)", _v_fondo_amortigua),
        Verificacion("sin fondo: prociclicidad (recorte en recesión)", _v_prociclicidad_sin_fondo),
        Verificacion("más concentración = mayor golpe", _v_estructura_amplifica),
    ],
    notas="El mismo recurso que enriquece hace vulnerable. Preludio de m103 (cobre→crecimiento con datos del BCRP).",
)
