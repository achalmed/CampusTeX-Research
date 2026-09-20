"""simuladores/macro/modelos/nivel_12/m98_pib_potencial.py — PIB potencial vs observado del Perú (nivel 12).

m16 (brecha del producto) con DATOS. Toma el índice del PBI real del BCRP
(PN01770AM, 2007=100) y separa TENDENCIA (potencial) de CICLO (brecha)
con un filtro simple: una media móvil centrada o una tendencia suavizada.
  brecha_t = (PBI_t − PBI*_t) / PBI*_t
El resultado muestra los mismos episodios que m97 pero como DESVIACIONES
del potencial: el sobrecalentamiento del boom, la brecha negativa del
COVID. Ilustra por qué el potencial NO es observable (depende del filtro) —
la limitación de m16 hecha evidencia.

Procedencia: dato BCRP PN01770AM (PBI índice 2007=100), muestra 2004-2024.
El filtro de tendencia es un suavizado didáctico (media móvil / tendencia
exponencial), NO el filtro Hodrick-Prescott oficial — la brecha resultante
es ilustrativa.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _potencial(indice, suavizado):
    """Tendencia por media móvil centrada de ventana `suavizado` (años)."""
    n = len(indice)
    w = int(round(suavizado))
    pot = np.empty(n)
    for i in range(n):
        lo, hi = max(0, i - w // 2), min(n, i + w // 2 + 1)
        pot[i] = indice[lo:hi].mean()
    # ajuste de tendencia log-lineal para los extremos (evita sesgo de borde)
    t = np.arange(n)
    a, b = np.polyfit(t, np.log(indice), 1)
    tendencia = np.exp(a * t + b)
    # mezcla: media móvil en el centro, tendencia log en general
    return 0.5 * pot + 0.5 * tendencia


def _serie(p):
    anos, indice = _datos_bcrp.serie("pbi_indice", anual=True)
    pot = _potencial(indice, p["suavizado"])
    brecha = 100 * (indice - pot) / pot
    return anos, indice, pot, brecha


def _curvas(p):
    anos, indice, pot, brecha = _serie(p)
    return {"lineas": {"PBI observado (índice, BCRP)": (anos, indice, config.AZUL2),
                       "PBI potencial (tendencia estimada)": (anos, pot, config.GRIS)},
            "puntos": [(2020.0, float(indice[anos == 2020][0]),
                        f"COVID: brecha {float(brecha[anos == 2020][0]):+.1f}%")],
            "anotacion": (f"PBI índice 2007=100 (BCRP PN01770AM)\n"
                          f"brecha COVID {float(brecha[anos == 2020][0]):+.1f}%, "
                          f"máx sobrecalentamiento {float(brecha.max()):+.1f}%\n"
                          "el potencial NO es observable: depende del filtro (m16)")}


def _resultados(p):
    anos, indice, pot, brecha = _serie(p)
    return {"brecha COVID 2020 (%)": float(brecha[anos == 2020][0]),
            "brecha máxima positiva (sobrecalentamiento, %)": float(brecha.max()),
            "brecha mínima (recesión, %)": float(brecha.min()),
            "brecha promedio (~0 por construcción, %)": float(brecha.mean()),
            "volatilidad de la brecha (pp)": float(brecha.std()),
            "años con brecha positiva": float(np.sum(brecha > 0))}


def _ecuaciones_calibradas(p):
    anos, indice, pot, brecha = _serie(p)
    return [f"$brecha_t = (PBI_t - PBI^*_t)/PBI^*_t$",
            f"$brecha_{{COVID}} = {float(brecha[anos == 2020][0]):+.1f}\\%$ "
            f"(ventana {int(p['suavizado'])} años)"]


_P0 = {"suavizado": 5.0}


def _v_covid_brecha_negativa():
    anos, indice, pot, brecha = _serie(_P0)
    return float(brecha[anos == 2020][0]) < -3, \
        (f"la brecha del COVID es fuertemente negativa ({float(brecha[anos == 2020][0]):+.1f}%): "
         "el producto muy por debajo del potencial — la recesión de m16 con datos")


def _v_brecha_centrada():
    anos, indice, pot, brecha = _serie(_P0)
    return abs(float(brecha.mean())) < 2, \
        (f"la brecha promedia cerca de cero ({float(brecha.mean()):+.1f}%): por construcción, "
         "el ciclo oscila alrededor del potencial (m16) — sube y baja, no se va")


def _v_potencial_depende_filtro():
    _, _, _, b3 = _serie(dict(_P0, suavizado=3.0))
    _, _, _, b7 = _serie(dict(_P0, suavizado=7.0))
    return abs(float(b3.std()) - float(b7.std())) > 0.1, \
        ("la brecha CAMBIA con el filtro (ventana 3 vs 7 años): el potencial NO es "
         "observable, se estima — la limitación central de m16, con datos peruanos")


def _v_sobrecalentamiento_boom():
    anos, indice, pot, brecha = _serie(_P0)
    boom = brecha[(anos >= 2007) & (anos <= 2013)]
    return float(boom.max()) > 0, \
        (f"el superciclo tuvo brecha positiva (sobrecalentamiento hasta {float(boom.max()):+.1f}%): "
         "crecer sobre el potencial presiona precios (m18) — el boom no fue gratis")


MODELO = Modelo(
    id="m98", nivel=12,
    nombre="PIB potencial vs observado del Perú",
    xlabel="Año", ylabel="PBI (índice 2007=100)",
    parametros=[
        Parametro("suavizado", _P0["suavizado"], 3, 9, 1, "Ventana del filtro (años)",
                  grupo="método", definicion="cambia la brecha: el potencial no es observable (m16)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto de las oscilaciones del PBI peruano es ciclo (recuperable) y cuánto es cambio de tendencia?",
        variables=[("PBI observado", "índice real del BCRP (PN01770AM)"),
                   ("PBI potencial", "la tendencia estimada — NO observable"),
                   ("brecha", "la desviación: ciclo (m16) con datos peruanos")],
        derivacion=["dato: \\;PBI_t\\;índice\\;(BCRP\\;PN01770AM)",
                    "PBI^*_t = filtro(PBI_t) \\;(tendencia\\;suavizada)",
                    "brecha_t = (PBI_t - PBI^*_t)/PBI^*_t \\;(m16)"],
        contexto=("m16 introdujo la brecha del producto como concepto; este modelo "
                  "la calcula con el PBI real del Perú (índice 2007=100, BCRP "
                  "PN01770AM). Separar el PBI observado en TENDENCIA (potencial, lo "
                  "que la economía puede producir de forma sostenible) y CICLO "
                  "(brecha, la desviación transitoria) es una de las tareas más "
                  "importantes y difíciles de la macroeconomía aplicada, porque el "
                  "potencial NO es observable: hay que estimarlo con un filtro, y "
                  "el resultado depende del filtro elegido — exactamente la "
                  "limitación que m16 advertía, ahora hecha evidencia. El "
                  "laboratorio usa un suavizado simple (media móvil + tendencia "
                  "log-lineal), no el filtro Hodrick-Prescott oficial que usa el "
                  "BCRP, así que la brecha resultante es ILUSTRATIVA, no la cifra "
                  "oficial. Aun así, los episodios son claros y coinciden con m97: "
                  "el superciclo (2004-2013) muestra brecha POSITIVA "
                  "(sobrecalentamiento, la economía produciendo sobre su potencial, "
                  "lo que presiona precios — m18), y el COVID (2020) muestra una "
                  "brecha fuertemente NEGATIVA (el producto muy por debajo del "
                  "potencial). La lección metodológica es la de m16: como el "
                  "potencial se estima, la brecha se revisa mucho, y la política "
                  "monetaria (m38, m100) que responde a la brecha lo hace con una "
                  "variable incierta — una fuente de error real."),
        autores=("Dato: BCRP (PN01770AM); el concepto de brecha: m16; el filtro "
                 "oficial es Hodrick-Prescott (mención) — aquí un suavizado "
                 "didáctico."),
        supuestos=[
            "El potencial se estima con un filtro de suavizado (media móvil + tendencia log): NO es el HP oficial, la brecha es ilustrativa.",
            "La tendencia log-lineal corrige el sesgo de borde del filtro (el problema de fin de muestra del HP, mención).",
            "La brecha es descriptiva del ciclo, no una medida de holgura para política (esa exige el filtro oficial y juicio).",
        ],
        ecuaciones=[
            Ecuacion("brecha_t = \\frac{PBI_t - PBI^*_t}{PBI^*_t}", "la brecha (m16)",
                     "positiva = sobrecalentamiento (presión de precios, m18); negativa = "
                     "recursos ociosos (recesión) — el ciclo separado de la tendencia."),
            Ecuacion("PBI^*_t = filtro(PBI_t), \\;\\; brecha\\;depende\\;del\\;filtro",
                     "la incertidumbre del potencial",
                     "distintas ventanas dan distintas brechas (verificado): el potencial NO es "
                     "observable — la limitación de m16 que la política debe manejar."),
        ],
        intuicion=("Calcular la brecha del PBI peruano enseña, con datos, la lección "
                   "más humilde de la macro aplicada: no sabemos con certeza cuánto "
                   "puede crecer una economía. El potencial es una construcción "
                   "estadística que cambia con el método, y sin embargo la política "
                   "monetaria (m38, m100) y la fiscal (m66, déficit estructural) "
                   "dependen de él. En el Perú, la pregunta práctica es si la "
                   "desaceleración post-2013 fue CICLO (brecha negativa, "
                   "recuperable con estímulo) o CAÍDA DEL POTENCIAL (fin del boom "
                   "del cobre bajó la capacidad, m89-m90) — y la respuesta, que el "
                   "filtro no resuelve del todo, determina si la política correcta "
                   "es contracíclica o de reformas estructurales (el dilema de "
                   "m90). El COVID es más claro: una brecha negativa transitoria "
                   "que el rebote recuperó. Pero incluso ahí, ¿el confinamiento "
                   "dañó el potencial (histéresis, m16) o no? El dato ayuda pero no "
                   "zanja — y esa honestidad sobre la incertidumbre es parte de la "
                   "buena política."),
        equilibrio=("La brecha oscila alrededor de cero por construcción "
                    "(verificado): el ciclo sube y baja en torno al potencial. Su "
                    "nivel exacto depende del filtro (verificado) — la "
                    "incertidumbre es estructural, no un defecto del cálculo."),
        limitaciones=[
            "Filtro didáctico, no el HP oficial del BCRP: la brecha es ilustrativa, no la cifra de política.",
            "Problema de fin de muestra: la brecha de los años más recientes es la MENOS confiable (el filtro no ve el futuro) — corregido parcialmente con la tendencia log.",
            "Ciclo vs tendencia es indistinguible en tiempo real: si la desaceleración post-boom fue ciclo o caída del potencial (m90) sigue en debate — el filtro no lo resuelve.",
        ],
        evolucion=("Aterriza m16 (brecha) con datos peruanos y prepara m100 (la "
                   "regla del BCRP responde a esta brecha) y m99 (la inflación se "
                   "relaciona con ella vía Phillips). La incertidumbre del "
                   "potencial conecta con m90 (¿ciclo o productividad?) — el dilema "
                   "de diagnóstico aplicado al Perú post-boom."),
    ),
    escenarios=[
        Escenario("filtro_corto", "ventana de 3 años (más ciclo)",
                  {"suavizado": 3.0},
                  "un filtro corto atribuye más al ciclo: la brecha es más "
                  "volátil, la tendencia sigue de cerca al dato — un extremo del "
                  "dilema tendencia/ciclo.",
                  cadena=["ventana corta", "el potencial sigue de cerca al PBI",
                          "más variación atribuida al ciclo", "brecha volátil",
                          "el potencial 'absorbe' menos"]),
        Escenario("filtro_largo", "ventana de 7 años (más tendencia)",
                  {"suavizado": 7.0},
                  "un filtro largo atribuye más a cambios de tendencia: la brecha "
                  "es más suave, los episodios más marcados — el otro extremo, y "
                  "otra brecha para la misma serie.",
                  cadena=["ventana larga", "el potencial es más suave",
                          "más variación atribuida a la tendencia", "brecha marcada en los episodios",
                          "la MISMA serie, distinta brecha: m16"]),
    ],
    verificaciones=[
        Verificacion("brecha COVID fuertemente negativa (m16)", _v_covid_brecha_negativa),
        Verificacion("la brecha oscila alrededor de cero", _v_brecha_centrada),
        Verificacion("la brecha depende del filtro (no observable)", _v_potencial_depende_filtro),
        Verificacion("el superciclo tuvo sobrecalentamiento (m18)", _v_sobrecalentamiento_boom),
    ],
    notas="m16 con datos: el potencial no es observable. La lección más humilde de la macro aplicada.",
)
