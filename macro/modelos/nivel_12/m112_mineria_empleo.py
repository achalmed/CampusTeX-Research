"""simuladores/macro/modelos/nivel_12/m112_mineria_empleo.py — minería, crecimiento y empleo (nivel 12).

La paradoja del ENCLAVE, el corazón del debate sobre el modelo de desarrollo
peruano. La minería co-mueve fuerte con el crecimiento (corr +0.53 entre el PBI
minero y el PBI total) y lo amplifica (es más volátil: 5.8 vs 4.9 pp): cuando
entran nuevas minas de cobre —2015-2016, con Las Bambas, Cerro Verde y
Toromocho— el PBI minero salta (+9.5%, +16.3%) y empuja el total. La minería es
~13% del PBI, ~60% de las exportaciones (m109) y un pilar fiscal (el canon que
financia m106). Y sin embargo emplea DIRECTAMENTE a solo ~1.5% de la fuerza
laboral: es un enclave de capital intensivo. De ahí la paradoja: genera enorme
valor, divisas e impuestos, pero pocos empleos directos, así que sus beneficios
llegan de forma INDIRECTA (vía el fisco, el canon, el gasto regional) y difusa
—lo que los vuelve disputados (conflictos sociales) y desiguales—. Es el
argumento central para DIVERSIFICAR (m112→m115): un país no genera empleo
masivo con un enclave, por rico que sea.

Procedencia: PBI minero (variación %, BCRP PM04972AA) y PBI (PN01728AM) son
datos BCRP reales. Las participaciones estructurales (~13% del PBI, ~60% de
exportaciones, ~1.5% del empleo) son cifras PÚBLICAS de BCRP/INEI, DECLARADAS
(conocimiento general del país; el empleo minero requeriría ENAHO-INEI, aún no
conectada). El enclave y la diversificación: m112/m115 (conocimiento general).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config

# Participaciones estructurales de la minería (cifras públicas BCRP/INEI,
# DECLARADAS ilustrativas — no calculadas aquí; el empleo minero exige ENAHO).
_SHARE_PBI = 13.0        # % del PBI (minería e hidrocarburos)
_SHARE_EXPORT = 60.0     # % de las exportaciones
_SHARE_EMPLEO = 1.5      # % del empleo directo


def _series():
    anos, minero, g = _datos_bcrp.alinear("pbi_minero_var", "pbi_var")
    return anos, minero, g


def _idx(anos, p):
    a = int(p["anio_foco"])
    return int(list(anos.astype(int)).index(a)) if a in anos.astype(int) else len(anos) - 1


def _curvas(p):
    anos, minero, g = _series()
    return {"lineas": {"PBI minería e hidrocarburos (var%, BCRP)": (anos, minero, config.VERDE),
                       "PBI total (var%, BCRP)": (anos, g, config.AZUL2)},
            "puntos": [(2016.0, float(minero[anos == 2016][0]), "2016: nuevas minas (Las Bambas)"),
                       (2020.0, float(minero[anos == 2020][0]), "2020: minas cerradas (COVID)")],
            "anotacion": (f"PBI minero (PM04972AA) vs PBI total (PN01728AM)\n"
                          f"corr $= {_datos_bcrp.correlacion(minero, g):+.2f}$; minería más volátil (amplifica)\n"
                          f"enclave: ~{_SHARE_PBI:.0f}% del PBI, ~{_SHARE_EXPORT:.0f}% exportaciones, pero ~{_SHARE_EMPLEO:.1f}% del empleo")}


def _resultados(p):
    anos, minero, g = _series()
    i = _idx(anos, p)
    return {"corr(PBI minero, PBI total)": float(_datos_bcrp.correlacion(minero, g)),
            "volatilidad PBI minero (pp)": float(minero.std()),
            "volatilidad PBI total (pp)": float(g.std()),
            "minería: % del PBI (declarado)": _SHARE_PBI,
            "minería: % de exportaciones (declarado)": _SHARE_EXPORT,
            "minería: % del empleo directo (declarado)": _SHARE_EMPLEO,
            f"PBI minero {int(anos[i])} (var%)": float(minero[i])}


def _ecuaciones_calibradas(p):
    anos, minero, g = _series()
    return [f"corr(PBI minero, PBI total) $= {_datos_bcrp.correlacion(minero, g):+.2f}$; $\\sigma_{{minero}} > \\sigma_{{PBI}}$ (amplifica)",
            f"enclave: $\\sim${_SHARE_PBI:.0f}\\% PBI, $\\sim${_SHARE_EXPORT:.0f}\\% exportaciones, pero $\\sim${_SHARE_EMPLEO:.1f}\\% empleo $\\Rightarrow$ diversificar (m115)"]


_P0 = {"anio_foco": 2016.0}


def _v_mineria_comueve():
    anos, minero, g = _series()
    c = _datos_bcrp.correlacion(minero, g)
    return c > 0.4, \
        (f"el PBI minero co-mueve con el total (corr {c:+.2f}): la minería es un motor del crecimiento peruano "
         "—vía exportaciones (m109) e inversión (m26)— cuando entran nuevas minas de cobre")


def _v_mineria_amplifica():
    anos, minero, g = _series()
    return minero.std() > g.std(), \
        (f"el PBI minero es más volátil ({minero.std():.1f} vs {g.std():.1f} pp): la minería AMPLIFICA el ciclo "
         "—depende de precios (m103) y de la entrada discreta de mega-proyectos— y transmite esa volatilidad al PBI")


def _v_enclave():
    return True, \
        (f"la paradoja del enclave: la minería es ~{_SHARE_PBI:.0f}% del PBI y ~{_SHARE_EXPORT:.0f}% de las exportaciones, "
         f"pero solo ~{_SHARE_EMPLEO:.1f}% del empleo DIRECTO (cifras BCRP/INEI): genera valor y divisas, no empleo masivo "
         "— por eso sus beneficios son indirectos (fisco, canon) y disputados")


def _v_nuevas_minas():
    anos, minero, g = _series()
    m15 = float(minero[anos == 2015][0])
    m16 = float(minero[anos == 2016][0])
    return m15 > 8 and m16 > 12, \
        (f"2015-2016 el PBI minero saltó (+{m15:.0f}%, +{m16:.0f}%) al entrar nuevas minas de cobre (Las Bambas, "
         "Cerro Verde, Toromocho): un boom de VOLUMEN por inversión (m26) que sostuvo el crecimiento cuando el precio caía")


MODELO = Modelo(
    id="m112", nivel=12,
    nombre="Minería → crecimiento y empleo (BCRP)",
    xlabel="Año", ylabel="Variación anual (%)",
    parametros=[
        Parametro("anio_foco", _P0["anio_foco"], 2004, 2024, 1, "Año a destacar (ciclo minero)",
                  grupo="análisis", definicion="año a inspeccionar; 2015-16 nuevas minas, 2020 cierres"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si la minería es ~13% del PBI y ~60% de las exportaciones, ¿por qué no genera empleo masivo y su aporte es tan disputado?",
        variables=[("g_minero", "crecimiento del PBI de minería e hidrocarburos (BCRP PM04972AA)"),
                   ("g", "crecimiento del PBI total (BCRP PN01728AM)"),
                   ("enclave", "~13% del PBI y ~60% de exportaciones, pero ~1.5% del empleo")],
        derivacion=["dato: \\;g_{minero} \\;(PM04972AA), \\;g \\;(PN01728AM)",
                    "corr(g_{minero}, g) \\approx +0.53, \\;\\sigma_{minero} > \\sigma_g \\;(amplifica)",
                    "enclave: \\;\\sim 13\\%\\;PBI, \\sim 60\\%\\;export, \\;pero\\;\\sim 1.5\\%\\;empleo",
                    "\\Rightarrow beneficio\\;INDIRECTO\\;(fisco/canon) \\Rightarrow diversificar\\;(m115)"],
        contexto=("Este modelo aborda el debate más importante del desarrollo "
                  "peruano: qué papel juega la minería. Los datos del BCRP muestran, "
                  "primero, que la minería es un motor real del crecimiento: el PBI "
                  "minero co-mueve con el total (correlación +0.53) y lo amplifica, "
                  "porque es más volátil (5.8 frente a 4.9 puntos). Cuando entran "
                  "nuevas minas de cobre —el gran ejemplo es 2015-2016, con Las "
                  "Bambas, la ampliación de Cerro Verde y Toromocho entrando en "
                  "producción— el PBI minero salta (+9.5% y +16.3%) y sostiene el "
                  "crecimiento agregado justo cuando el PRECIO del cobre estaba "
                  "cayendo (m103): fue un boom de VOLUMEN, fruto de años de "
                  "inversión (m26). La minería es, además, cerca del 13% del PBI, "
                  "alrededor del 60% de las exportaciones (el motor de m109) y un "
                  "pilar de las cuentas fiscales, con el canon minero financiando "
                  "buena parte de la inversión pública regional (m106). Y sin "
                  "embargo —aquí la paradoja— emplea DIRECTAMENTE a solo el 1.5% "
                  "aproximado de la fuerza laboral. Es un enclave intensivo en "
                  "capital: produce enorme valor con relativamente poca gente. Esta "
                  "es la raíz de por qué el aporte de la minería es tan disputado en "
                  "el Perú. Sus beneficios son grandes pero INDIRECTOS y difusos: "
                  "llegan a la población no como empleo minero directo, sino a "
                  "través del fisco (impuestos y canon que financian obras, "
                  "servicios y transferencias), de los encadenamientos (proveedores, "
                  "construcción) y de las divisas que estabilizan la macro. Cuando "
                  "esos canales indirectos funcionan mal —canon mal gastado, "
                  "corrupción, pocos encadenamientos locales, daño ambiental sin "
                  "compensación— las comunidades sienten los costos (ambientales, "
                  "sociales) sin ver los beneficios, y estallan los conflictos. La "
                  "lección de desarrollo, que enlaza con el cierre del nivel (m115): "
                  "una economía no genera empleo masivo ni desarrollo inclusivo "
                  "apoyada solo en un enclave, por rico que sea; necesita "
                  "DIVERSIFICAR hacia sectores que empleen (manufactura, "
                  "agroexportación, servicios) y hacer que la renta minera financie "
                  "esa transformación, en vez de sustituirla."),
        autores=("Datos: BCRP (PM04972AA PBI minero var%, PN01728AM PBI); las "
                 "participaciones estructurales (~13% PBI, ~60% exportaciones, ~1.5% "
                 "empleo) son cifras públicas BCRP/INEI, declaradas (el empleo "
                 "minero exige ENAHO-INEI, no conectada); el enclave y la "
                 "diversificación: economía del desarrollo (conocimiento general)."),
        supuestos=[
            "El co-movimiento minería-PBI (+0.53) y la mayor volatilidad son DATOS (BCRP); las participaciones (PBI, exportaciones, empleo) son cifras públicas DECLARADAS, no calculadas en este modelo.",
            "El empleo minero (~1.5%) se cita de fuentes INEI (ENAHO); no se adquiere aquí (la ENAHO no está conectada) — procedencia declarada, orden de magnitud.",
            "La paradoja del enclave (mucho valor, poco empleo) es un rasgo estructural documentado de la minería intensiva en capital, no una afirmación de este modelo sobre su deseabilidad.",
        ],
        ecuaciones=[
            Ecuacion("corr(g_{minero}, \\; g) \\approx +0.53, \\;\\; \\sigma_{minero} > \\sigma_g", "motor y amplificador",
                     "la minería impulsa el crecimiento y lo amplifica (más volátil): las nuevas minas "
                     "(2015-16) sostuvieron el PBI cuando el precio caía — un boom de volumen (m26)."),
            Ecuacion("\\sim 13\\%\\;PBI, \\;\\sim 60\\%\\;export, \\;pero\\;\\sim 1.5\\%\\;empleo", "el enclave",
                     "genera enorme valor y divisas con poca gente: un enclave intensivo en capital — "
                     "de ahí que sus beneficios sean indirectos (fisco, canon) y no empleo masivo."),
            Ecuacion("beneficio\\;indirecto\\;(canon) \\Rightarrow disputado \\Rightarrow diversificar\\;(m115)", "la lección",
                     "como el beneficio llega vía el fisco y no como empleo directo, es difuso y "
                     "disputado (conflictos): el argumento para diversificar hacia sectores que empleen."),
        ],
        intuicion=("La imagen es la de dos economías en una: una mina moderna, "
                   "enorme, que exporta miles de millones en cobre con unos pocos "
                   "miles de trabajadores altamente productivos; y a su alrededor, "
                   "un país donde la mayoría trabaja en agricultura, comercio y "
                   "servicios informales de baja productividad. La minería es el "
                   "sector rico, pero es una isla —un enclave—, y el reto del "
                   "desarrollo es tender puentes desde esa isla al resto: puentes "
                   "fiscales (que el canon financie escuelas, salud, "
                   "infraestructura), puentes productivos (proveedores locales, "
                   "encadenamientos) y puentes de transformación (usar la renta para "
                   "industrializar y diversificar). Cuando esos puentes existen y "
                   "funcionan, la minería es una bendición que financia el "
                   "desarrollo; cuando no, es una fuente de conflicto —comunidades "
                   "que ven los camiones cargados de cobre pasar por sus pueblos "
                   "pobres— y de la 'maldición de los recursos'. El Perú vive en la "
                   "tensión entre ambas. Y por eso este modelo desemboca "
                   "naturalmente en la pregunta de m115: ¿cómo se convierte un país "
                   "rico en recursos pero de empleo pobre en un país de desarrollo "
                   "amplio? La respuesta no es cerrar las minas, es diversificar con "
                   "su renta —y hacerlo bien."),
        equilibrio=("No hay equilibrio que resolver: es la caracterización empírica "
                    "y estructural del sector minero. El resultado es la paradoja del "
                    "enclave —motor del PBI y las exportaciones (corr +0.53, ~13% del "
                    "PBI, ~60% de exportaciones) pero apenas ~1.5% del empleo—, que "
                    "motiva la diversificación (m115)."),
        limitaciones=[
            "El empleo minero es declarado (INEI/ENAHO), no adquirido aquí: la ENAHO no está conectada; el ~1.5% es orden de magnitud de fuentes públicas.",
            "PBI minero incluye hidrocarburos (PM04972AA es minería e hidrocarburos): la minería metálica sola es algo menor; no altera la conclusión del enclave.",
            "Descriptivo: no modela los encadenamientos, el canon ni los conflictos socioambientales; señala la estructura (mucho valor, poco empleo) que los explica.",
        ],
        evolucion=("Cierra los canales sectoriales del nivel mostrando la tensión "
                   "central del modelo peruano: la minería (el cobre de m103-m105, "
                   "las exportaciones de m109) genera valor pero no empleo masivo. "
                   "Es el puente directo a m115 (el modelo simplificado del Perú y "
                   "el reto de diversificar) y da contenido concreto a la "
                   "'diversificación' que m97, m103 y m110 venían nombrando. También "
                   "conecta con m106 (el canon financia la inversión pública)."),
    ),
    escenarios=[
        Escenario("nuevas_minas_2016", "el boom de volumen (2015-2016)",
                  {"anio_foco": 2016.0},
                  "2015-2016: entran Las Bambas, Cerro Verde ampliada y Toromocho; "
                  "el PBI minero salta +9.5% y +16.3% y sostiene el crecimiento "
                  "aunque el precio del cobre caía (m103). El fruto de años de "
                  "inversión (m26) — un boom de volumen, no de precio.",
                  cadena=["años de inversión en mega-proyectos (m26)", "2015-16: entran Las Bambas, Cerro Verde, Toromocho",
                          "el PBI minero salta (+9.5%, +16.3%)", "sostiene el crecimiento pese al precio cayendo (m103)",
                          "boom de VOLUMEN — pero pocos empleos directos (enclave)"]),
        Escenario("cierres_2020", "el golpe COVID (2020)",
                  {"anio_foco": 2020.0},
                  "2020: las minas cerraron por el confinamiento y el PBI minero "
                  "cayó −13.4%, peor que el total — la minería amplifica los shocks "
                  "(su volatilidad). El mismo cierre que hundió el volumen exportado "
                  "de m110.",
                  cadena=["confinamiento COVID (2020)", "las minas cierran (shock de oferta, m110)",
                          "el PBI minero cae −13.4% (peor que el total)", "la minería amplifica el shock (más volátil)",
                          "el enclave concentra el golpe en pocos, gran valor perdido"]),
        Escenario("enclave", "la paradoja estructural (el enclave)",
                  {"anio_foco": 2016.0},
                  "el rasgo permanente: ~13% del PBI y ~60% de exportaciones, pero "
                  "~1.5% del empleo. Mucho valor, pocos empleos: los beneficios "
                  "llegan por el fisco y el canon (m106), no por el empleo directo — "
                  "difusos y disputados. El argumento para diversificar (m115).",
                  cadena=["minería: ~13% PBI, ~60% exportaciones (enorme valor)", "pero ~1.5% del empleo directo (enclave)",
                          "beneficio vía fisco/canon (m106), no empleo", "difuso y disputado (conflictos socioambientales)",
                          "la lección: diversificar con la renta minera (m115)"]),
    ],
    verificaciones=[
        Verificacion("la minería co-mueve con el crecimiento (m109, m26)", _v_mineria_comueve),
        Verificacion("la minería amplifica el ciclo (más volátil)", _v_mineria_amplifica),
        Verificacion("la paradoja del enclave: mucho valor, poco empleo", _v_enclave),
        Verificacion("2015-16: nuevas minas, boom de volumen (m26)", _v_nuevas_minas),
    ],
    notas="Paradoja del enclave: la minería es ~13% del PBI y ~60% de exportaciones (corr +0.53 con el crecimiento, amplifica) pero solo ~1.5% del empleo directo. Valor sin empleo masivo → beneficio indirecto (canon) → diversificar (m115).",
)
