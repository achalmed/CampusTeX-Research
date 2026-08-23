# m82_shock_petrolero.py — shock petrolero (nivel 11).
#
# El shock de oferta arquetípico: un salto del precio del petróleo encarece
# producir TODO (energía es insumo universal). Aplica m19/m24 con el dilema
# de política en su forma más pura. Distingue países IMPORTADORES (el shock
# es puro costo: estanflación) de EXPORTADORES (el shock es ingreso: booms —
# el ángulo peruano NO es petrolero pero sí cobre/gas, m88-m89).
# Compara las tres respuestas históricas (acomodar/resistir/nada) sobre el
# motor de m52.
#
# Procedencia: OPEP 1973/1979 (mención) sobre AD-AS dinámico (m52); Hamilton
# sobre petróleo y recesiones (mención) — conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_11 import _episodio
import config


def _episodio_petroleo(p):
    T = int(round(p["T"]))
    # el shock de costos entra por la oferta, con persistencia
    s = _episodio.pulso(T, 2, p["shock_precio"], decae=p["decae"])
    # la respuesta de política entra por la demanda (acomodar>0, resistir<0)
    d = _episodio.pulso(T, 2, p["respuesta"], decae=p["decae"])
    t, pi, Y = _episodio.simular(d, s, p["alpha"], p["lam"])
    return t, pi, Y, d, s


def _curvas(p):
    t, pi, Y, d, s = _episodio_petroleo(p)
    return {"lineas": {"producto $Y_t$ (índice)": (t, Y, config.AZUL2),
                       "inflación $\\pi_t$ (%)": (t, pi, config.ROJO),
                       "potencial / meta": (t, np.full(len(t), 100.0), config.GRIS)},
            "anotacion": (f"shock de precio {p['shock_precio']:+.1f} desde $t{{=}}2$\n"
                          f"respuesta {p['respuesta']:+.1f} "
                          f"({'acomodar' if p['respuesta'] > 0 else 'resistir' if p['respuesta'] < 0 else 'pasiva'})\n"
                          f"π pico {float(pi.max()):.1f}% · Y mín {float(Y.min()):.1f}: estanflación")}


def _resultados(p):
    t, pi, Y, d, s = _episodio_petroleo(p)
    return {"pico de inflación (%)": float(pi.max()),
            "caída de producto (índice)": float(Y.min()) - 100,
            "desempleo Okun (Δu máx)": float(_episodio.okun(Y).max()),
            "π final": float(pi[-1]),
            "Y final": float(Y[-1]),
            "área de estanflación (π×|ΔY|)": float(pi.max() * abs(Y.min() - 100))}


def _ecuaciones_calibradas(p):
    return [f"$s_t = {p['shock_precio']:+.1f}$ (costos energía) decae a {1 - p['decae']:.2f}",
            f"respuesta $d_t = {p['respuesta']:+.1f}$"]


_P0 = {"shock_precio": 3.0, "respuesta": 0.0, "decae": 0.25, "alpha": 1.0, "lam": 0.5, "T": 16.0}


def _v_estanflacion():
    t, pi, Y, d, s = _episodio_petroleo(_P0)
    return float(pi.max()) > 2.0 and float(Y.min()) < 100, \
        (f"π sube ({float(pi.max()):.1f}%) Y Y cae ({float(Y.min()):.1f}): la estanflación "
         "arquetípica del shock de oferta (m19/m24)")


def _v_acomodar_infla():
    p_nada = dict(_P0, respuesta=0.0)
    p_acom = dict(_P0, respuesta=3.0)
    pi_nada = float(_episodio_petroleo(p_nada)[1].max())
    pi_acom = float(_episodio_petroleo(p_acom)[1].max())
    # "recuperar producto" = elevar el PATH de Y (media), no el mínimo puntual,
    # que la inflación acumulada puede desplazar de período
    Y_acom = float(_episodio_petroleo(p_acom)[2].mean())
    Y_nada = float(_episodio_petroleo(p_nada)[2].mean())
    return pi_acom > pi_nada and Y_acom > Y_nada, \
        (f"acomodar eleva el producto (media {Y_nada:.1f}→{Y_acom:.1f}) pero infla más "
         f"(π {pi_nada:.1f}→{pi_acom:.1f}%): la Fed de Burns — convalidar el shock")


def _v_resistir_recesa():
    p_res = dict(_P0, respuesta=-3.0)
    Y_res = float(_episodio_petroleo(p_res)[2].mean())
    Y_nada = float(_episodio_petroleo(_P0)[2].mean())
    pi_res = float(_episodio_petroleo(p_res)[1].max())
    return Y_res < Y_nada and pi_res < float(_episodio_petroleo(_P0)[1].max()), \
        (f"resistir contiene la inflación profundizando la recesión (Y medio {Y_nada:.1f}→{Y_res:.1f}): "
         "Volcker — no hay respuesta gratis")


def _v_transitorio_vs_persistente():
    pi_trans = float(_episodio_petroleo(dict(_P0, decae=0.6))[1].sum())
    pi_pers = float(_episodio_petroleo(dict(_P0, decae=0.1))[1].sum())
    return pi_pers > pi_trans, \
        (f"un shock persistente cuesta mucho más en inflación acumulada que uno "
         "transitorio: la persistencia del precio es lo que ancla o desancla expectativas")


MODELO = Modelo(
    id="m82", nivel=11,
    nombre="Shock petrolero",
    xlabel="Período $t$ (trimestres)", ylabel="Índices y tasas",
    parametros=[
        Parametro("shock_precio", _P0["shock_precio"], 0, 6, 0.5, "Salto del precio (costos)",
                  grupo="shock", definicion="energía es insumo universal: encarece TODO (m19)"),
        Parametro("respuesta", _P0["respuesta"], -4, 4, 0.5, "Respuesta de política",
                  grupo="política", definicion=">0 acomodar (Burns); <0 resistir (Volcker)"),
        Parametro("decae", _P0["decae"], 0.05, 0.7, 0.05, "Velocidad de reversión del shock",
                  grupo="shock", definicion="transitorio (alto) vs persistente (bajo)"),
        Parametro("alpha", _P0["alpha"], 0.3, 2, 0.1, "Dureza de la regla α", grupo="estructura"),
        Parametro("lam", _P0["lam"], 0.2, 1, 0.05, "Pendiente de Phillips λ", grupo="estructura"),
        Parametro("T", _P0["T"], 10, 24, 1, "Trimestres simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué un salto del petróleo sube la inflación Y hunde el producto a la vez — y qué puede hacer la política?",
        variables=[("s_t", "shock de costos energéticos — el insumo universal"),
                   ("Y, π", "estanflación: caen y suben juntos (m24)"),
                   ("respuesta", "acomodar (Burns) o resistir (Volcker): el dilema")],
        derivacion=["petróleo\\uparrow \\Rightarrow costos\\;de\\;TODO\\uparrow \\Rightarrow s_t > 0",
                    "SRAS\\;se\\;desplaza: \\;\\pi\\uparrow, Y\\downarrow \\;(m19)",
                    "respuesta: \\;acomodar\\;(d>0)\\;o\\;resistir\\;(d<0)"],
        contexto=("El shock petrolero es el shock de oferta arquetípico y el que "
                  "definió la macroeconomía de los 70. La energía es un insumo "
                  "universal: cuando su precio salta, producir cualquier cosa "
                  "cuesta más, la oferta agregada se desplaza (m19) y llega la "
                  "estanflación — inflación con recesión, la combinación que la "
                  "Phillips original (m13) declaraba imposible. Los shocks de 1973 "
                  "(OPEP) y 1979 (Irán) enseñaron el dilema de política en carne "
                  "propia: acomodar (bajar tasas para sostener el empleo) "
                  "convalidaba la inflación (la Fed de Burns), mientras resistir "
                  "(subir tasas para domar precios) profundizaba la recesión "
                  "(Volcker, 1979-82). Hamilton (mención) documentó que casi todas "
                  "las recesiones de EE.UU. de posguerra fueron precedidas por "
                  "shocks petroleros. Para el Perú el análogo no es el petróleo "
                  "(importador neto modesto) sino los términos de intercambio del "
                  "cobre (m88-m89, m105)."),
        autores=("OPEP 1973/1979 (menciones); Hamilton sobre petróleo y recesiones; "
                 "el dilema Burns/Volcker es de m24 — conocimiento general."),
        supuestos=[
            "El país es IMPORTADOR neto de energía: el shock es puro costo (para exportadores es ingreso, m88).",
            "El shock entra por la oferta (m19); su persistencia (decae) decide si contamina expectativas.",
            "La respuesta de política se resume en un shock de demanda (acomodar/resistir) — el detalle es m56.",
        ],
        ecuaciones=[
            Ecuacion("s_t > 0 \\Rightarrow \\pi\\uparrow \\land Y\\downarrow", "la estanflación",
                     "el shock de costos sube precios y baja producto a la vez: la firma que "
                     "separa oferta de demanda (m18 vs m19), verificada."),
            Ecuacion("acomodar: Y\\uparrow, \\pi\\uparrow\\uparrow \\;;\\; resistir: \\pi\\downarrow, Y\\downarrow\\downarrow",
                     "el menú sin salida gratis",
                     "ninguna respuesta recupera producto Y precios: el shock de oferta solo se "
                     "REPARTE entre inflación y recesión (verificado en ambas ramas)."),
        ],
        intuicion=("El shock petrolero es una transferencia de riqueza forzada "
                   "hacia los productores de energía: el país importador es más "
                   "pobre, y la política solo decide en qué moneda paga — inflación "
                   "o desempleo. La lección de los 70, cara: sin ancla de "
                   "expectativas (m40), acomodar repetidamente desancla la "
                   "inflación y hace falta una recesión brutal (Volcker) para "
                   "re-anclarla. Con ancla creíble (metas, m40), un shock petrolero "
                   "transitorio se puede 'mirar pasar' — la respuesta moderna, que "
                   "el Perú aplicó a los shocks de alimentos (m83, m113)."),
        equilibrio=("Trayectoria de estanflación que revierte al disiparse el "
                    "shock; la persistencia (decae) decide el costo acumulado "
                    "(verificado). La respuesta óptima depende de la credibilidad "
                    "del ancla (m40-m41)."),
        limitaciones=[
            "Importador puro: no captura el efecto ingreso de los exportadores (Rusia, Arabia, y el análogo cobre para Perú — m88).",
            "Un solo canal: el petróleo también afecta vía tipo de cambio y balanza comercial (m43-m46), aquí resumidos en el costo.",
            "Sin efectos de segunda ronda explícitos: la indexación salarial (los 70) amplifica — aquí vive en λ y la persistencia.",
        ],
        evolucion=("Es el shock de oferta puro del nivel. m83 lo repite con "
                   "alimentos (más relevante para emergentes), m85 añade el canal "
                   "cambiario (inflación importada), y m88-m89 muestran la cara "
                   "EXPORTADORA (el cobre peruano). El episodio de los 70 completo "
                   "es m93."),
    ),
    escenarios=[
        Escenario("opep_1973", "shock de 3 sin respuesta (política pasiva)",
                  {"shock_precio": 3.0, "respuesta": 0.0},
                  "estanflación limpia: π sube y Y cae, la economía absorbe el golpe "
                  "sin que la política elija bando.",
                  cadena=["precio del petróleo salta", "costos de todo suben (m19)",
                          "SRAS a la izquierda", "π↑ con Y↓", "estanflación"]),
        Escenario("acomodar_burns", "la Fed baja tasas para salvar el empleo",
                  {"shock_precio": 3.0, "respuesta": 3.0},
                  "el producto se recupera pero la inflación se duplica: convalidar "
                  "el shock — el camino que enquistó la inflación de los 70.",
                  cadena=["shock + acomodo monetario", "la demanda sube",
                          "Y recupera", "π se convalida y sube más", "inflación persistente"]),
        Escenario("resistir_volcker", "la Fed sube tasas para domar precios",
                  {"shock_precio": 3.0, "respuesta": -3.0},
                  "la inflación cede al precio de una recesión más honda: la doctrina "
                  "Volcker — restaurar la credibilidad cuesta producto.",
                  cadena=["shock + apretón monetario", "la demanda se contrae",
                          "π contenida", "Y↓↓ recesión más honda", "el precio de la credibilidad"]),
        Escenario("shock_transitorio", "salto que revierte rápido (decae 0.6)",
                  {"decae": 0.6},
                  "con ancla creíble, un shock transitorio se puede mirar pasar: la "
                  "inflación acumulada es mucho menor — la respuesta moderna (m40).",
                  cadena=["shock transitorio", "expectativas ancladas no se mueven (m40)",
                          "π sube y baja rápido", "sin desanclaje", "mirar pasar el shock"]),
    ],
    verificaciones=[
        Verificacion("estanflación: π↑ y Y↓ juntos", _v_estanflacion),
        Verificacion("acomodar recupera Y pagando inflación (Burns)", _v_acomodar_infla),
        Verificacion("resistir contiene π profundizando recesión (Volcker)", _v_resistir_recesa),
        Verificacion("persistente cuesta más que transitorio", _v_transitorio_vs_persistente),
    ],
    notas="El shock de oferta arquetípico: una transferencia forzada. La política solo elige la moneda del pago.",
)
