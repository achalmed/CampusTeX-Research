"""simuladores/macro/modelos/nivel_10/m80_crisis_sistemica.py — crisis sistémica: contagio en red (nivel 10, cierre).

La quiebra de un banco no se queda en él: sus deudas impagas son activos de
OTROS bancos (exposición interbancaria). Un shock a un nodo se propaga por
la red — el contagio de m79 entre instituciones, no entre rondas.
Red circular de N bancos, cada uno con capital E y exposición cruzada w:
  si el banco i quiebra, transmite (1−recup)·deuda al siguiente;
  el siguiente quiebra si esa pérdida supera su capital E.
Emergen dos regímenes (Gai-Kapadia; Acemoglu et al. — menciones):
  red MÁS conectada = más robusta a shocks pequeños (reparte)…
  …pero más FRÁGIL a shocks grandes (propaga todo): robust-yet-fragile.
El "too connected to fail" y el riesgo sistémico nacen aquí.

Procedencia: modelos de contagio en redes financieras (Gai-Kapadia 2010;
Acemoglu-Ozdaglar-Tahbaz-Salehi 2015 — menciones) — conocimiento general.
Calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _cascada(p):
    """Propaga la quiebra por una red circular; devuelve cuántos bancos caen."""
    N = int(round(p["N"]))
    E = p["E"]                                          # capital de cada banco
    exposicion = p["w"] * (1 - p["recup"] / 100)        # pérdida transmitida por quiebra
    quebrados = [False] * N
    # shock inicial: el banco 0 quiebra
    frontera = [0]
    quebrados[0] = True
    while frontera:
        i = frontera.pop()
        vecino = (i + 1) % N
        # el vecino recibe la exposición; quiebra si supera su capital (y no es el origen)
        if not quebrados[vecino] and exposicion > E:
            quebrados[vecino] = True
            frontera.append(vecino)
    return sum(quebrados), exposicion


def _curvas(p):
    caidos, exposicion = _cascada(p)
    N = int(round(p["N"]))
    # barras: capital de un banco vs exposición recibida; y el conteo de la cascada
    cats = ["capital $E$\nde un banco", "pérdida transmitida\n$(1{-}rec)w$",
            "bancos caídos\n(de " + str(N) + ")"]
    vals = [p["E"], exposicion, float(caidos)]
    cols = [config.AZUL2, config.ROJO, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"exposición transmitida = {exposicion:.1f} "
                          f"{'>' if exposicion > p['E'] else '≤'} capital {p['E']:.1f}\n"
                          f"cascada: {caidos} de {N} bancos "
                          f"({'SISTÉMICA' if caidos > N / 2 else 'contenida'})\n"
                          "la quiebra de uno es el activo impago de otro")}


def _resultados(p):
    caidos, exposicion = _cascada(p)
    N = int(round(p["N"]))
    return {"bancos caídos": float(caidos),
            "de un total de": float(N),
            "fracción del sistema (%)": 100 * caidos / N,
            "capital por banco E": p["E"],
            "exposición transmitida (1−rec)·w": exposicion,
            "¿supera el capital? (contagia)": 1.0 if exposicion > p["E"] else 0.0}


def _ecuaciones_calibradas(p):
    _, exposicion = _cascada(p)
    return [f"$exposición = (1-{p['recup'] / 100:.2f})\\times{p['w']:.0f} = {exposicion:.1f}$",
            f"$contagia \\iff {exposicion:.1f} > E = {p['E']:.0f}$"]


_P0 = {"N": 8.0, "E": 10.0, "w": 25.0, "recup": 40.0}


def _v_contagio_condicion():
    caidos, exposicion = _cascada(_P0)
    contagia = exposicion > _P0["E"]
    return (contagia and caidos > 1) or (not contagia and caidos == 1), \
        (f"el contagio ocurre sii la exposición ({exposicion:.1f}) supera el capital ({_P0['E']:.0f}): "
         f"cayeron {caidos} bancos — el umbral de quiebra en cadena")


def _v_capital_frena():
    c1, _ = _cascada(dict(_P0, E=10.0))
    c2, _ = _cascada(dict(_P0, E=20.0))
    return c2 < c1, \
        (f"más capital por banco frena la cascada ({c1}→{c2} caídos): el colchón "
         "individual protege al SISTEMA — el argumento del capital contracíclico (Basilea III)")


def _v_recuperacion_aisla():
    c1, _ = _cascada(dict(_P0, recup=40.0))
    c2, _ = _cascada(dict(_P0, recup=80.0))
    return c2 < c1, \
        (f"mayor recuperación de activos quebrados (40%→80%) contiene el contagio "
         f"({c1}→{c2}): resolver quiebras ORDENADAMENTE (no fire sale) protege la red")


def _v_shock_aislado():
    c, exposicion = _cascada(dict(_P0, w=8.0))          # exposición baja
    return c == 1, \
        ("con poca exposición cruzada, la quiebra queda AISLADA (1 banco): las redes "
         "poco conectadas contienen shocks — pero pierden los beneficios de compartir riesgo")


MODELO = Modelo(
    id="m80", nivel=10,
    nombre="Crisis sistémica (contagio en red)",
    xlabel="", ylabel="Capital, exposición y cascada",
    parametros=[
        Parametro("w", _P0["w"], 5, 50, 5, "Exposición interbancaria w", grupo="conectividad",
                  definicion="cuánto se deben los bancos entre sí: el canal del contagio"),
        Parametro("E", _P0["E"], 5, 30, 2.5, "Capital por banco E", grupo="resiliencia",
                  definicion="el colchón que decide si el contagio se detiene"),
        Parametro("recup", _P0["recup"], 20, 90, 10, "Recuperación de quiebras (%)", grupo="resolución",
                  definicion="cuánto se salva de un banco quebrado (resolución ordenada)"),
        Parametro("N", _P0["N"], 4, 16, 1, "Número de bancos N", grupo="red"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué la quiebra de UN banco puede tumbar al sistema entero — y por qué estar más conectado es a la vez más seguro y más peligroso?",
        variables=[("w", "exposición cruzada — el canal del contagio"),
                   ("E", "capital por banco — el cortafuegos"),
                   ("cascada", "cuántos caen: contenida o sistémica")],
        derivacion=["quiebra\\;de\\;i \\Rightarrow pérdida\\;(1-rec)w\\;al\\;vecino",
                    "vecino\\;quiebra \\iff (1-rec)w > E",
                    "cascada \\Rightarrow contagio\\;en\\;cadena\\;por\\;la\\;red"],
        contexto=("El nivel de crisis culmina donde los riesgos individuales se "
                  "vuelven sistémicos: la quiebra de un banco no es su problema "
                  "privado, porque sus deudas impagas son activos de otros bancos. "
                  "Un shock a un nodo (m71-m79) se propaga por la red de "
                  "exposiciones — el acelerador de m79, ahora entre instituciones. "
                  "Los modelos de contagio (Gai-Kapadia 2010; Acemoglu et al. 2015 "
                  "— menciones) revelan una propiedad contraintuitiva: las redes "
                  "MÁS conectadas son más ROBUSTAS a shocks pequeños (reparten la "
                  "pérdida entre muchos) pero más FRÁGILES a shocks grandes "
                  "(propagan todo) — 'robust-yet-fragile'. Lehman Brothers (2008) "
                  "fue el nodo cuya caída amenazó con derribar la red; AIG fue "
                  "rescatado no por sí mismo sino por su conectividad ('too "
                  "connected to fail'). El riesgo sistémico — la externalidad de "
                  "estar conectado — es la justificación de toda la regulación "
                  "macroprudencial moderna (menciones)."),
        autores=("Gai y Kapadia (2010, cascadas en redes financieras); Acemoglu, "
                 "Ozdaglar y Tahbaz-Salehi (2015, estabilidad y contagio); Allen y "
                 "Gale (contagio financiero) — menciones."),
        supuestos=[
            "Red circular simple: la topología real (nodos centrales, clusters) cambia los detalles pero no el mensaje robust-yet-fragile.",
            "Contagio solo por exposición directa (deudas impagas): el contagio por INFORMACIÓN (pánico, m73) y por precios comunes (fire sale, m79) son canales adicionales.",
            "Capital homogéneo: los bancos reales difieren, y el más débil o más central detona la cascada.",
        ],
        ecuaciones=[
            Ecuacion("(1 - rec)\\,w > E \\Rightarrow contagio", "el umbral de la cascada",
                     "el vecino cae si la pérdida heredada supera su capital: el contagio es "
                     "digital (se detiene o arrasa) según ese umbral (verificado)."),
            Ecuacion("robusta\\;a\\;shocks\\;chicos, \\;frágil\\;a\\;los\\;grandes",
                     "robust-yet-fragile",
                     "más conexiones reparten mejor los golpes pequeños Y propagan mejor los "
                     "grandes: la conectividad es seguro y contagio a la vez."),
        ],
        intuicion=("La crisis sistémica enseña la lección más profunda del nivel: "
                   "en un sistema conectado, la estabilidad es un bien PÚBLICO que "
                   "nadie produce individualmente. Cada banco elige su "
                   "apalancamiento (m71) y sus exposiciones pensando solo en sí "
                   "mismo, pero la fragilidad que crea la paga todo el sistema — "
                   "una externalidad, como la contaminación. Por eso la regulación "
                   "microprudencial (banco por banco) no basta: hace falta "
                   "macroprudencial (vigilar la red, exigir más capital a los nodos "
                   "sistémicos, romper las cadenas de exposición). Y por eso los "
                   "rescates sistémicos, por impopulares que sean, tienen una "
                   "lógica que los rescates individuales no: no salvan al banco, "
                   "salvan la RED. El Perú, con un sistema bancario concentrado "
                   "pero bien capitalizado y poco expuesto al exterior (mención), "
                   "vive en la esquina robusta — por diseño regulatorio, no por "
                   "suerte."),
        equilibrio=("Cascada determinista: se detiene (contenida) o arrasa "
                    "(sistémica) según el umbral (1−rec)w vs E, verificado en ambos "
                    "regímenes. La transición entre 'contenida' y 'sistémica' es "
                    "abrupta — la marca de los sistemas en red."),
        limitaciones=[
            "Un solo canal de contagio (exposición directa): los otros dos — pánico informacional (m73) y precios comunes/fire sale (m79) — amplifican y a menudo dominan.",
            "Topología simple: las redes reales tienen nodos súper-conectados (too-connected-to-fail) cuya caída es catastrófica — el detalle importa para la política.",
            "Estático: la propagación real toma tiempo, y la intervención (el banco central rompiendo la cadena) puede detenerla a mitad — el propósito del backstop.",
        ],
        evolucion=("Cierra el nivel de crisis integrando todos sus mecanismos: "
                   "balance frágil (m71), detonante (m72), pánico (m73-m76), ajuste "
                   "externo (m75, m77), trampa (m78) y acelerador (m79), ahora en "
                   "RED. El nivel 11 aplica todo esto a episodios reales (COVID "
                   "m81, salida de capitales m87), y el 12 al Perú (shock externo "
                   "m110). Es el último modelo puramente teórico del currículo "
                   "troncal."),
    ),
    escenarios=[
        Escenario("cascada_sistemica", "alta exposición (w=25) con capital normal",
                  {"w": 25.0, "E": 10.0},
                  "la quiebra de un banco arrastra a la mayoría: la exposición "
                  "transmitida (15) supera el capital (10) y el contagio no se "
                  "detiene — Lehman 2008 sin cortafuegos.",
                  cadena=["un banco quiebra (m71-m79)", "su deuda impaga golpea al vecino",
                          "(1−rec)w > E: el vecino cae", "que golpea al siguiente",
                          "cascada por la red", "crisis sistémica"]),
        Escenario("cortafuegos_de_capital", "más capital por banco (E=20)",
                  {"E": 20.0},
                  "la cascada se detiene en el primer banco: capital suficiente para "
                  "absorber la exposición heredada — el objetivo del capital "
                  "sistémico de Basilea III (mención).",
                  cadena=["un banco quiebra", "el vecino hereda la pérdida",
                          "pero E > exposición: aguanta", "el contagio se detiene",
                          "el colchón individual salva al sistema"]),
        Escenario("resolucion_ordenada", "recuperación alta (80%): sin fire sale",
                  {"recup": 80.0},
                  "resolver la quiebra ordenadamente (no rematar activos) transmite "
                  "poca pérdida y contiene el contagio: el valor de un régimen de "
                  "resolución bancaria (mención).",
                  cadena=["banco quiebra", "resolución ordenada (no fire sale, m79)",
                          "se recupera el 80% de sus activos", "poca pérdida transmitida",
                          "el vecino aguanta", "contagio contenido"]),
        Escenario("sistema_desconectado", "baja exposición cruzada (w=8)",
                  {"w": 8.0},
                  "la quiebra queda aislada: redes poco conectadas contienen "
                  "shocks… pero también pierden los beneficios de compartir riesgo "
                  "— el dilema robust-yet-fragile.",
                  cadena=["poca exposición interbancaria", "la quiebra no transmite lo suficiente",
                          "queda en 1 banco", "sistema seguro ante shocks",
                          "pero sin las ventajas de la interconexión (trade-off)"]),
    ],
    verificaciones=[
        Verificacion("contagio sii exposición > capital", _v_contagio_condicion),
        Verificacion("más capital frena la cascada (Basilea III)", _v_capital_frena),
        Verificacion("resolución ordenada aísla el contagio", _v_recuperacion_aisla),
        Verificacion("poca conexión contiene el shock (trade-off)", _v_shock_aislado),
    ],
    notas="La estabilidad es un bien público que nadie produce solo. Cierre teórico del currículo troncal: robust-yet-fragile.",
)
