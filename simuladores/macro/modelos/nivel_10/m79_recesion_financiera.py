"""simuladores/macro/modelos/nivel_10/m79_recesion_financiera.py — recesión por shock financiero: el acelerador (nivel 10).

Cierra el lazo que m71 dejó abierto: el desapalancamiento que baja precios
que fuerzan más desapalancamiento. Cada ronda:
  ventas_n = λ·(pérdida de capital de la ronda)
  caída de precio = impacto_precio·ventas_n
  nueva pérdida de capital = λ·caída de precio  → alimenta la ronda n+1
El factor de amplificación de la espiral es geométrico:
  κ = λ·impacto_precio·λ = λ²·impacto_precio   (por ronda)
  pérdida total = shock_inicial / (1 − κ)   si κ < 1 (converge)
  si κ ≥ 1: espiral sin fondo (colapso) — el acelerador financiero de
  Bernanke-Gertler / Kiyotaki-Moore (menciones; Kiyotaki-Moore está en la
  biblioteca de Edison).

Procedencia: acelerador financiero (Bernanke-Gertler-Gilchrist; Kiyotaki-
Moore "Credit Cycles" 1997 — EN BIBLIOTECA, sin verificar) — menciones;
conocimiento general. Calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _kappa(p):
    return p["lam"] ** 2 * p["impacto"] / 100          # amplificación por ronda


def _rondas(p, N=None):
    N = int(round(N if N is not None else p["rondas"]))
    kappa = _kappa(p)
    perdida = np.empty(N + 1)
    perdida[0] = p["shock"]                             # pérdida inicial de capital
    for n in range(N):
        perdida[n + 1] = perdida[n] * kappa            # cada ronda es κ veces la anterior
    return np.arange(N + 1), perdida, np.cumsum(perdida)


def _curvas(p):
    n, ronda, acum = _rondas(p)
    kappa = _kappa(p)
    total = p["shock"] / (1 - kappa) if kappa < 1 else float("inf")
    tope = np.full_like(n, total, dtype=float) if np.isfinite(total) else acum
    return {"lineas": {"pérdida acumulada": (n, acum, config.AZUL2),
                       "pérdida de la ronda $n$": (n, ronda, config.ROJO),
                       "límite $shock/(1-\\kappa)$": (n, tope, config.GRIS)},
            "anotacion": (f"amplificación por ronda $\\kappa = \\lambda^2\\,impacto = {kappa:.2f}$\n"
                          + (f"converge a {total:.0f} (= {total / p['shock']:.1f}× el shock)"
                             if kappa < 1 else "$\\kappa \\geq 1$: ESPIRAL SIN FONDO (colapso)") + "\n"
                          "el desapalancamiento que se muerde la cola (m71 cerrado)")}


def _resultados(p):
    n, ronda, acum = _rondas(p, N=200)
    kappa = _kappa(p)
    total = p["shock"] / (1 - kappa) if kappa < 1 else float("inf")
    return {"amplificación por ronda κ = λ²·impacto": kappa,
            "multiplicador de crisis 1/(1−κ)": 1 / (1 - kappa) if kappa < 1 else 9999.0,
            "pérdida total (converge)": total if np.isfinite(total) else 9999.0,
            "pérdida directa (shock inicial)": p["shock"],
            "amplificación (total/directa)": total / p["shock"] if np.isfinite(total) else 9999.0,
            "¿espiral sin fondo? (κ≥1)": 1.0 if kappa >= 1 else 0.0}


def _ecuaciones_calibradas(p):
    kappa = _kappa(p)
    return [f"$\\kappa = \\lambda^2\\,impacto = {p['lam']:.0f}^2\\times{p['impacto'] / 100:.3f} = {kappa:.2f}$",
            (f"$total = {p['shock']:.0f}/(1-{kappa:.2f}) = {p['shock'] / (1 - kappa):.0f}$"
             if kappa < 1 else "$total = \\infty$ (espiral)")]


_P0 = {"lam": 5.0, "impacto": 2.0, "shock": 10.0, "rondas": 12.0}


def _v_suma_geometrica():
    n, ronda, acum = _rondas(dict(_P0, rondas=300))
    kappa = _kappa(_P0)
    teo = _P0["shock"] / (1 - kappa)
    return abs(float(acum[-1]) - teo) < 1e-6, \
        (f"la suma de rondas converge a shock/(1−κ) = {teo:.1f}: el acelerador es una "
         "serie geométrica (como el multiplicador de m04, pero destructivo)")


def _v_amplificacion():
    kappa = _kappa(_P0)
    mult = 1 / (1 - kappa)
    return mult > 1, \
        (f"el shock directo se amplifica ×{mult:.2f}: la crisis financiera es mucho mayor "
         "que su detonante — el acelerador de Bernanke-Gertler")


def _v_espiral():
    kappa = _kappa(dict(_P0, lam=8.0))
    return kappa >= 1, \
        (f"con λ=8, κ={kappa:.2f}≥1: la espiral no converge — colapso sin fondo (2008 sin rescate). "
         "El apalancamiento alto vuelve INESTABLE al sistema")


def _v_desapalancar_apaga():
    kappa = _kappa(dict(_P0, lam=2.0))
    return kappa < 0.3, \
        (f"con λ bajo (2), κ={kappa:.2f}: casi no hay amplificación — sistemas poco "
         "apalancados absorben shocks sin espiral (el argumento de Basilea, m71)")


MODELO = Modelo(
    id="m79", nivel=10,
    nombre="Recesión por shock financiero (acelerador)",
    xlabel="Ronda de la espiral $n$", ylabel="Pérdida de capital",
    parametros=[
        Parametro("lam", _P0["lam"], 1, 10, 0.5, "Apalancamiento λ (m71)", grupo="fragilidad",
                  definicion="entra al CUADRADO: es el amplificador de la espiral"),
        Parametro("impacto", _P0["impacto"], 0.5, 6, 0.5, "Impacto de ventas en precio (%)", grupo="mercado",
                  definicion="cuánto baja el precio por unidad vendida (fire sale)"),
        Parametro("shock", _P0["shock"], 2, 30, 2, "Shock inicial de capital", grupo="detonante"),
        Parametro("rondas", _P0["rondas"], 5, 30, 1, "Rondas mostradas", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué un shock financiero pequeño puede hundir la economía real — y cuándo la espiral no tiene fondo?",
        variables=[("κ = λ²·impacto", "la amplificación por ronda — el corazón del acelerador"),
                   ("1/(1−κ)", "el multiplicador de crisis — geométrico como m04, pero destructivo"),
                   ("κ≥1", "la frontera del colapso: la espiral sin fondo")],
        derivacion=["m71: \\;desapalancar \\Rightarrow vender \\Rightarrow precio\\downarrow",
                    "precio\\downarrow \\Rightarrow capital\\downarrow \\Rightarrow más\\;ventas",
                    "\\kappa = \\lambda^2\\,impacto; \\;\\; total = \\frac{shock}{1-\\kappa}"],
        contexto=("m71 dejó el lazo abierto: el desapalancamiento vende, vender "
                  "baja precios, precios bajos destruyen más capital. Este modelo "
                  "lo cierra y mide su fuerza. El acelerador financiero (Bernanke, "
                  "Gertler y Gilchrist; y el 'Credit Cycles' de Kiyotaki y Moore, "
                  "1997 — que está en la biblioteca de Edison) explica por qué las "
                  "recesiones con crisis financiera son tan profundas y largas: un "
                  "shock modesto al capital se amplifica en una serie geométrica de "
                  "ventas y caídas de precio. Si el factor κ = λ²·impacto es menor "
                  "que uno, la espiral converge a una pérdida finita pero "
                  "amplificada; si κ ≥ 1, no hay fondo — el sistema colapsa hasta "
                  "que alguien externo (el banco central como comprador de última "
                  "instancia) rompe el lazo. Es 2008 en una ecuación: el "
                  "apalancamiento que multiplicaba ganancias multiplicó el "
                  "derrumbe."),
        autores=("Bernanke, Gertler y Gilchrist (acelerador financiero — mención); "
                 "Kiyotaki y Moore ('Credit Cycles' 1997 — EN BIBLIOTECA, sin "
                 "verificar); Brunnermeier-Sannikov sobre la inestabilidad "
                 "endógena — mención."),
        supuestos=[
            "Impacto de precio lineal en las ventas: la realidad es peor (los mercados en pánico tienen demanda que se evapora).",
            "λ constante durante la espiral: en la crisis λ salta (todos quieren desapalancar), lo que agrava κ.",
            "Sin backstop: agregar un comprador de última instancia (el banco central) TRUNCA la serie — el punto de política.",
        ],
        ecuaciones=[
            Ecuacion("\\kappa = \\lambda^2\\,\\cdot impacto", "la amplificación",
                     "el apalancamiento entra al CUADRADO: una vez porque amplifica la pérdida "
                     "inicial (m71), otra porque amplifica la respuesta a la caída de precio — "
                     "por eso los sistemas muy apalancados son explosivos."),
            Ecuacion("pérdida_{total} = \\frac{shock}{1 - \\kappa}", "el multiplicador de crisis",
                     "geométrico como el keynesiano (m04) pero con signo trágico: κ<1 amplifica, "
                     "κ≥1 colapsa (verificado en ambos regímenes)."),
        ],
        intuicion=("El acelerador financiero es el multiplicador de m04 con el alma "
                   "invertida: allí el gasto de uno era el ingreso de otro (virtuoso), "
                   "aquí la venta de uno es la pérdida de otro (vicioso). La frontera "
                   "κ=1 es la diferencia entre una recesión y una depresión: por "
                   "debajo, el sistema absorbe el golpe amplificado pero finito; por "
                   "encima, cae sin fondo hasta que un actor SIN restricción de "
                   "balance (el banco central, que no puede quebrar) compra los "
                   "activos y corta la espiral. Esto justifica los rescates de "
                   "2008-2009 no como generosidad sino como la única forma de bajar "
                   "κ bajo 1 — y explica por qué la regulación (Basilea, m71) apunta "
                   "a λ: reducir el apalancamiento es reducir κ al cuadrado."),
        equilibrio=("κ<1: convergencia geométrica a shock/(1−κ) (verificada). "
                    "κ≥1: divergencia — no hay equilibrio interno, solo "
                    "intervención externa. La frontera κ=1 es el umbral "
                    "recesión/colapso."),
        limitaciones=[
            "Lineal: los mercados reales en pánico tienen no linealidades (la liquidez desaparece de golpe) que hacen la espiral más abrupta.",
            "λ e impacto constantes: en la crisis ambos empeoran (todos desapalancan, nadie compra) — κ real crece durante el evento.",
            "Sin el canal a la economía real explícito: aquí el 'capital' es financiero; el puente al empleo y la inversión (crédito que se corta) es el paso siguiente (Bernanke, mención).",
        ],
        evolucion=("Cierra el mecanismo que m71 abrió y m72-m73 detonaron: la "
                   "espiral precio-balance. Solo falta ponerla en RED — cuando el "
                   "colapso de un nodo contagia a los demás (m80). La Gran "
                   "Recesión (m81, nivel 11) es este acelerador a escala global."),
    ),
    escenarios=[
        Escenario("recesion_amplificada", "λ=5, impacto 2%: κ=0.5",
                  {"lam": 5.0, "impacto": 2.0},
                  "el shock se duplica (×2): una pérdida de 10 se vuelve 20 vía la "
                  "espiral — recesión financiera típica, profunda pero finita.",
                  cadena=["shock al capital", "desapalancar: vender (m71)",
                          "el precio cae (fire sale)", "más pérdida de capital",
                          "otra ronda × κ", "converge a shock/(1−κ) = 2× el shock"]),
        Escenario("colapso_sin_fondo", "apalancamiento alto: λ=8 (κ>1)",
                  {"lam": 8.0, "impacto": 2.0},
                  "la espiral NO converge: cada ronda es mayor que la anterior — "
                  "2008 sin rescate, la depresión que el TARP y la Fed evitaron "
                  "(mención).",
                  cadena=["λ muy alto", "κ = λ²·impacto ≥ 1", "cada ronda amplifica",
                          "la serie diverge", "colapso hasta que el banco central compra",
                          "el backstop trunca la espiral"]),
        Escenario("sistema_resiliente", "poco apalancamiento: λ=2",
                  {"lam": 2.0},
                  "κ=0.08: el shock casi no se amplifica — un sistema con capital "
                  "sólido absorbe golpes sin espiral, el objetivo de Basilea III "
                  "(mención).",
                  cadena=["λ bajo (mucho capital, m71)", "κ pequeño",
                          "la espiral se apaga rápido", "shock apenas amplificado",
                          "la resiliencia se compra con capital"]),
    ],
    verificaciones=[
        Verificacion("suma de rondas = shock/(1−κ) (geométrica)", _v_suma_geometrica),
        Verificacion("el shock se amplifica (acelerador)", _v_amplificacion),
        Verificacion("κ≥1: espiral sin fondo (colapso)", _v_espiral),
        Verificacion("λ bajo apaga la espiral (Basilea)", _v_desapalancar_apaga),
    ],
    notas="El multiplicador de m04 con el alma invertida: la venta de uno es la pérdida de otro. κ=1 separa recesión de depresión.",
)
