# m75_sudden_stop.py — sudden stop: el freno súbito de capitales (nivel 10).
#
# Calvo (1998): cuando el financiamiento externo se corta de golpe, la cuenta
# corriente debe cerrarse por la fuerza. Si un país recibía flujos CF y
# absorbía  A = Y + CF  (gasto > producto, déficit corriente = CF), un corte
# a CF' obliga a  A' = Y + CF':
#   ajuste forzado del gasto:  ΔA = CF' − CF < 0
#   como los transables no bajan (hay que pagar deuda), el golpe cae sobre
#   los NO transables → colapso de su precio real → recesión y depreciación.
# El ajuste de la cuenta corriente = −ΔCF: brutal, involuntario, inmediato.
#
# Procedencia: Calvo (1998, "Capital Flows and Capital-Market Crises" — EN LA
# BIBLIOTECA de Edison, sin verificar; también su "Globalización financiera"
# 2002 está en biblioteca) — mención; conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _ajuste(p):
    absorcion0 = p["Y"] + p["CF"]                     # gasto = producto + financiamiento
    absorcion1 = p["Y"] + p["CF1"]
    dA = absorcion1 - absorcion0                       # < 0 si CF cae
    cc0, cc1 = -p["CF"], -p["CF1"]                     # CC = −CF (flotación, m43)
    ajuste_cc = cc1 - cc0                              # = −ΔCF > 0 (mejora forzada)
    # el golpe recae en no transables (fracción 1−α_t del gasto):
    caida_nt = -dA / (1 - p["alpha_t"]) if p["alpha_t"] < 1 else 0.0
    return dict(absorcion0=absorcion0, absorcion1=absorcion1, dA=dA,
                cc0=cc0, cc1=cc1, ajuste_cc=ajuste_cc, caida_nt=caida_nt)


def _curvas(p):
    a = _ajuste(p)
    cats = ["absorción\nantes", "absorción\ndespués", "ajuste CC\n$(-\\Delta CF)$",
            "golpe a no\ntransables"]
    vals = [a["absorcion0"], a["absorcion1"], a["ajuste_cc"], -a["caida_nt"]]
    cols = [config.AZUL2, config.DORADO, config.VERDE, config.ROJO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"financiamiento: {p['CF']:.0f} → {p['CF1']:.0f} (freno súbito)\n"
                          f"la CC salta {a['ajuste_cc']:+.0f} de golpe (= $-\\Delta CF$)\n"
                          f"el gasto cae {-a['dA']:.0f}: recesión y depreciación reales")}


def _resultados(p):
    a = _ajuste(p)
    return {"absorción antes (Y+CF)": a["absorcion0"],
            "absorción después (Y+CF')": a["absorcion1"],
            "ajuste forzado del gasto ΔA": a["dA"],
            "cuenta corriente antes (−CF)": a["cc0"],
            "cuenta corriente después": a["cc1"],
            "ajuste de la CC (= −ΔCF)": a["ajuste_cc"],
            "caída de no transables": a["caida_nt"]}


def _ecuaciones_calibradas(p):
    a = _ajuste(p)
    return [f"$A = Y + CF = {p['Y']:.0f} + {p['CF']:.0f} = {a['absorcion0']:.0f}$",
            f"$\\Delta A = CF' - CF = {p['CF1']:.0f} - {p['CF']:.0f} = {a['dA']:.0f}$",
            f"$\\Delta CC = -\\Delta CF = {a['ajuste_cc']:+.0f}$"]


_P0 = {"Y": 100.0, "CF": 30.0, "CF1": -10.0, "alpha_t": 0.4}


def _v_ajuste_cc():
    a = _ajuste(_P0)
    return abs(a["ajuste_cc"] - (-(_P0["CF1"] - _P0["CF"]))) < 1e-9, \
        (f"la CC mejora exactamente −ΔCF = {a['ajuste_cc']:+.0f}: el freno de capitales "
         "FUERZA el superávit — el ajuste no se elige, se sufre (Calvo)")


def _v_gasto_colapsa():
    a = _ajuste(_P0)
    return a["dA"] < 0 and abs(a["dA"] - (_P0["CF1"] - _P0["CF"])) < 1e-9, \
        (f"el gasto cae exactamente ΔCF = {a['dA']:.0f}: lo que financiaba el exterior "
         "hay que dejar de gastarlo de un día para otro")


def _v_no_transables_sufren():
    a = _ajuste(_P0)
    return a["caida_nt"] > -a["dA"], \
        (f"los no transables caen {a['caida_nt']:.0f} > ajuste total {-a['dA']:.0f}: "
         "como los transables deben pagar deuda, TODO el golpe recae en lo doméstico")


def _v_reversion_es_peor():
    a1 = _ajuste(_P0)["dA"]
    a2 = _ajuste(dict(_P0, CF1=-30.0))["dA"]
    return a2 < a1, \
        (f"si el flujo se REVIERTE (de +30 a −30), el ajuste se duplica ({a1:.0f}→{a2:.0f}): "
         "no es que deje de entrar capital — es que además hay que devolverlo")


MODELO = Modelo(
    id="m75", nivel=10,
    nombre="Sudden stop (freno de capitales)",
    xlabel="", ylabel="Flujos y ajustes (u.m.)",
    parametros=[
        Parametro("CF", _P0["CF"], 0, 60, 5, "Financiamiento externo previo CF", grupo="antes",
                  definicion="el déficit corriente que el capital financiaba"),
        Parametro("CF1", _P0["CF1"], -40, 30, 5, "Financiamiento tras el freno CF'", grupo="freno",
                  definicion="negativo = reversión: el capital HUYE, no solo deja de entrar"),
        Parametro("Y", _P0["Y"], 60, 150, 10, "Producto Y", grupo="estructura"),
        Parametro("alpha_t", _P0["alpha_t"], 0.2, 0.7, 0.05, "Peso de transables α_t", grupo="estructura",
                  definicion="menor peso transable = golpe más concentrado en lo doméstico"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Qué le pasa a un país cuando el mundo deja de prestarle de un día para otro?",
        variables=[("A = Y + CF", "absorción — cuánto gasta un país sobre lo que produce"),
                   ("ΔCC = −ΔCF", "el ajuste forzado — no se elige, se sufre"),
                   ("no transables", "donde recae el golpe: recesión y depreciación reales")],
        derivacion=["A = Y + CF \\;\\;(gasto = producto + financiamiento)",
                    "corte: \\;CF \\to CF' \\Rightarrow \\Delta A = CF' - CF < 0",
                    "\\Delta CC = -\\Delta CF > 0 \\;\\;(superávit\\;forzado)"],
        contexto=("Calvo (1998, mención — su paper y su libro sobre globalización "
                  "financiera están en la biblioteca de Edison) nombró el fenómeno "
                  "que define las crisis emergentes: el sudden stop, cuando el "
                  "financiamiento externo se corta abruptamente. La aritmética es "
                  "implacable: un país que gastaba más de lo que producía "
                  "(absorción = Y + CF, con déficit corriente financiado por "
                  "capital) debe, de golpe, gastar solo lo que produce — y si el "
                  "flujo se REVIERTE (hay que devolver), gastar menos aún. Como los "
                  "transables tienen que seguir generando divisas para el servicio "
                  "de deuda, el ajuste recae íntegro sobre los no transables: su "
                  "precio real colapsa (depreciación) y su producción se hunde "
                  "(recesión). México 1994, Asia 1997, Argentina 2001: el mismo "
                  "guion."),
        autores=("Calvo (1998; y 'Globalización financiera y mercados emergentes' "
                 "2002 — ambos en biblioteca, sin verificar); Calvo-Izquierdo-"
                 "Mejía sobre determinantes; Dornbusch sobre el ajuste real — "
                 "menciones."),
        supuestos=[
            "Flotación: la CC iguala a −CF (m43); con paridad fija, el ajuste pasa por reservas y colapso (m74).",
            "Transables comprometidos con el servicio de deuda: por eso el ajuste se concentra en no transables (el mecanismo de Calvo).",
            "Corte exógeno: en la realidad el sudden stop es contagio (Rusia 1998 → Brasil) o reversión de apetito global (la FED, m86) — factores de m80.",
        ],
        ecuaciones=[
            Ecuacion("\\Delta CC = -\\Delta CF", "el ajuste que no se elige",
                     "la identidad de m43 con dientes: si el capital deja de financiar el "
                     "déficit, el déficit DEBE desaparecer — por las buenas o por las malas."),
            Ecuacion("golpe_{NT} = \\frac{-\\Delta A}{1 - \\alpha_t}", "la carga sobre lo doméstico",
                     "los transables pagan deuda; todo el recorte del gasto cae sobre los no "
                     "transables — recesión y depreciación real concentradas."),
        ],
        intuicion=("El sudden stop es un desalojo financiero: el país vivía en una "
                   "casa que pagaba a crédito, el crédito se acaba, y hay que mudarse "
                   "a lo que uno REALMENTE puede pagar — de inmediato, sin "
                   "transición. Lo cruel es que el ajuste no distingue mérito: un "
                   "país con fundamentos decentes puede sufrir un sudden stop por "
                   "contagio (Calvo llamó a esto la 'globalización de la "
                   "ignorancia' — mención). La defensa es acumular reservas y "
                   "reducir la deuda en dólares en las buenas — exactamente lo que "
                   "el Perú hizo tras los 90 (m50, m110), convirtiendo el trauma de "
                   "una generación en política de Estado."),
        equilibrio=("Contabilidad de un ajuste forzado (verificado exacto): el "
                    "'equilibrio' post-stop tiene la CC en el nuevo −CF', con el "
                    "peso del ajuste medido sobre los no transables. La dinámica "
                    "(cuánto dura la recesión) depende de la flexibilidad real."),
        limitaciones=[
            "Estático: la profundidad y duración de la recesión dependen de rigideces (los no transables no re-precian instantáneo) — el costo real es mayor.",
            "Sin balances en dólares: si la deuda es en dólares, la depreciación del ajuste QUIEBRA a los deudores (tercera generación, m71+m74) — el círculo mortal.",
            "Corte exógeno: el gatillo real es contagio y apetito global de riesgo (m80, m86) — el país a menudo es víctima, no culpable.",
        ],
        evolucion=("Es la crisis cambiaria (m74) por el lado de la cuenta de "
                   "capitales, y el detonante externo de la recesión financiera "
                   "(m79). Junto con m71 (balances en dólares) forma la tercera "
                   "generación. En el nivel 11, la salida de capitales de un "
                   "emergente (m87) y el alza de la FED (m86) son sudden stops "
                   "aplicados; para Perú, el shock externo es m110."),
    ),
    escenarios=[
        Escenario("freno_subito", "el financiamiento cae de +30 a −10",
                  {"CF1": -10.0},
                  "la absorción cae 40 y la CC salta +40 de golpe: el país pasa de "
                  "gastar 130 a gastar 90 en un trimestre — el desalojo financiero "
                  "de Calvo.",
                  cadena=["corte de financiamiento externo", "absorción DEBE caer a Y+CF'",
                          "la CC se fuerza al superávit (−ΔCF)", "los no transables absorben el golpe",
                          "recesión + depreciación real"]),
        Escenario("reversion_total", "el capital HUYE: CF de +30 a −30",
                  {"CF1": -30.0},
                  "el ajuste se duplica a 60: no solo deja de entrar capital, hay "
                  "que devolverlo — Argentina 2001 (mención), el peor de los casos.",
                  cadena=["pánico y fuga (no solo freno)", "CF se vuelve muy negativo",
                          "ΔA = −60: colapso del gasto", "el ajuste dobla al del simple freno",
                          "depresión, no recesión"]),
        Escenario("economia_diversificada", "más peso transable: α_t=0.6",
                  {"alpha_t": 0.6},
                  "el mismo freno golpea menos a los no transables: una base "
                  "exportadora amplia (el cobre peruano, mención) reparte mejor el "
                  "ajuste — resiliencia estructural.",
                  cadena=["freno de capitales", "mismo ajuste total",
                          "pero más sector transable para absorberlo",
                          "menor colapso de no transables", "la diversificación como seguro"]),
    ],
    verificaciones=[
        Verificacion("el ajuste de la CC = −ΔCF exacto", _v_ajuste_cc),
        Verificacion("el gasto colapsa exactamente ΔCF", _v_gasto_colapsa),
        Verificacion("el golpe se concentra en no transables", _v_no_transables_sufren),
        Verificacion("la reversión duplica el ajuste del freno", _v_reversion_es_peor),
    ],
    notas="El desalojo financiero: mudarse de golpe a lo que uno puede pagar. Calvo está en la biblioteca de Edison.",
)
