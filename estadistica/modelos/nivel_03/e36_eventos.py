# e36_eventos.py — los eventos y sus operaciones (sección III, tema 36).
#
# Un EVENTO es un subconjunto del espacio muestral (e35): 'sacar par', 'suma ≥ 8',
# 'al menos un 6'. Sobre los eventos operan la teoría de conjuntos —unión (A o B),
# intersección (A y B), complemento (no A)— y sus probabilidades siguen reglas
# exactas. La central es la de INCLUSIÓN-EXCLUSIÓN: P(A∪B) = P(A)+P(B)−P(A∩B); si
# uno suma P(A)+P(B) a secas, cuenta DOS VECES la parte común y sobrestima. El
# modelo usa dos dados (Ω de 36 pares), fija B='al menos un 6' y deja mover el
# umbral de A='suma ≥ t' para ver la unión correcta contra la suma ingenua: la
# brecha entre ambas es exactamente P(A∩B).

import numpy as np
from itertools import product

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_OMEGA = list(product(range(1, 7), range(1, 7)))     # 36 pares (d1, d2)
_N = len(_OMEGA)                                      # 36


def _P(cond):
    return sum(1 for d in _OMEGA if cond(d)) / _N


def _A(t):
    return lambda d: (d[0] + d[1]) >= t              # suma ≥ t


def _B(d):
    return d[0] == 6 or d[1] == 6                     # al menos un 6


def _curvas(p):
    t = int(p["t"])
    ts = np.arange(2, 13)
    union = np.array([_P(lambda d, tt=tt: _A(tt)(d) or _B(d)) for tt in ts])
    naive = np.array([_P(_A(tt)) + _P(_B) for tt in ts])
    inter = np.array([_P(lambda d, tt=tt: _A(tt)(d) and _B(d)) for tt in ts])
    return {"lineas": {"P(A∪B) correcta (inclusión-exclusión)": (ts, union, config.AZUL2),
                       "P(A)+P(B) ingenua (sobrestima)": (ts, naive, config.ROJO),
                       "P(A∩B) (la parte contada dos veces)": (ts, inter, config.DORADO)},
            "puntos": [(t, _P(lambda d: _A(t)(d) or _B(d)),
                        f"t={t}: P(A∪B)={_P(lambda d: _A(t)(d) or _B(d)):.2f}")],
            "anotacion": (f"A = 'suma ≥ {t}', B = 'al menos un 6' (dos dados, |Ω|=36)\n"
                          f"P(A∪B) = P(A)+P(B)−P(A∩B) = {_P(_A(t)):.2f}+{_P(_B):.2f}−{_P(lambda d:_A(t)(d) and _B(d)):.2f} = {_P(lambda d:_A(t)(d) or _B(d)):.2f}\n"
                          "la suma ingenua cuenta la intersección DOS veces (la sobrestima)")}


def _resultados(p):
    t = int(p["t"])
    pa, pb = _P(_A(t)), _P(_B)
    pinter = _P(lambda d: _A(t)(d) and _B(d))
    punion = _P(lambda d: _A(t)(d) or _B(d))
    return {"umbral t (A = suma ≥ t)": float(t),
            "P(A)": pa, "P(B)": pb,
            "P(A∩B) (A y B)": pinter,
            "P(A∪B) correcta": punion,
            "P(A)+P(B) ingenua (sobrestima en P(A∩B))": pa + pb,
            "P(complemento de A) = 1−P(A)": 1 - pa}


def _ecuaciones_calibradas(p):
    t = int(p["t"])
    pa, pb = _P(_A(t)), _P(_B)
    pinter = _P(lambda d: _A(t)(d) and _B(d))
    return [f"P(A\\cup B) = P(A)+P(B)-P(A\\cap B) = {pa:.2f}+{pb:.2f}-{pinter:.2f} = {pa+pb-pinter:.2f}",
            f"P(A^c) = 1 - P(A) = 1 - {pa:.2f} = {1-pa:.2f}\\ \\text{{(complemento)}}"]


_P0 = {"t": 8}


def _v_inclusion_exclusion():
    t = 8
    pa, pb = _P(_A(t)), _P(_B)
    pinter = _P(lambda d: _A(t)(d) and _B(d))
    punion = _P(lambda d: _A(t)(d) or _B(d))
    return abs(punion - (pa + pb - pinter)) < 1e-12, \
        (f"regla de inclusión-exclusión: P(A∪B) = P(A)+P(B)−P(A∩B) = {pa:.2f}+{pb:.2f}−{pinter:.2f} = {punion:.2f}. "
         "Restar P(A∩B) corrige el doble conteo de la parte común — sumar a secas sobrestima")


def _v_sobrestima_naive():
    t = 8
    pa, pb = _P(_A(t)), _P(_B)
    punion = _P(lambda d: _A(t)(d) or _B(d))
    return (pa + pb) > punion, \
        (f"la suma ingenua P(A)+P(B) = {pa+pb:.2f} SOBRESTIMA la unión real ({punion:.2f}): cuenta dos veces los "
         "resultados que están en A y en B a la vez (suma ≥8 CON un 6) — el error clásico de olvidar la intersección")


def _v_complemento():
    t = 8
    pa = _P(_A(t))
    p_no_a = _P(lambda d: not _A(t)(d))
    return abs(p_no_a - (1 - pa)) < 1e-12, \
        (f"complemento: P(no A) = 1 − P(A) = 1 − {pa:.2f} = {1-pa:.2f}. A veces es MUCHO más fácil calcular lo "
         "contrario y restar (P(al menos uno) = 1 − P(ninguno)) — el truco del complemento")


def _v_mutuamente_excluyentes():
    # A='suma=2' y C='suma=12' son mutuamente excluyentes: P(A∪C)=P(A)+P(C) (sin restar)
    pa = _P(lambda d: d[0] + d[1] == 2)
    pc = _P(lambda d: d[0] + d[1] == 12)
    punion = _P(lambda d: d[0] + d[1] in (2, 12))
    return abs(punion - (pa + pc)) < 1e-12, \
        (f"si A y B son MUTUAMENTE EXCLUYENTES (no pueden ocurrir juntos, A∩B=∅), entonces P(A∪B)=P(A)+P(B) sin "
         f"restar: P(suma=2 o 12)={punion:.3f}={pa:.3f}+{pc:.3f} — la inclusión-exclusión se simplifica")


MODELO = Modelo(
    id="e36", nivel=3,
    nombre="Los eventos y sus operaciones",
    xlabel="umbral t  (A = 'suma ≥ t')", ylabel="probabilidad",
    parametros=[
        Parametro("t", _P0["t"], 2, 12, 1, "Umbral del evento A (suma ≥ t)",
                  grupo="probabilidad", definicion="A='suma≥t'; la brecha entre P(A)+P(B) y P(A∪B) es la intersección P(A∩B)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuál es la probabilidad de A o B? (No es P(A)+P(B) — a menos que no puedan pasar juntos.)",
        variables=[("A, B", "eventos: subconjuntos del espacio muestral"),
                   ("A∪B, A∩B, Aᶜ", "unión (A o B), intersección (A y B), complemento (no A)"),
                   ("inclusión-exclusión", "P(A∪B)=P(A)+P(B)−P(A∩B)")],
        derivacion=["\\text{evento} = \\text{subconjunto de } \\Omega \\;(e35)",
                    "\\text{unión } A\\cup B,\\ \\text{intersección } A\\cap B,\\ \\text{complemento } A^c",
                    "P(A\\cup B) = P(A) + P(B) - P(A\\cap B) \\;(\\text{inclusión-exclusión})",
                    "P(A^c) = 1 - P(A);\\quad A\\cap B = \\varnothing \\Rightarrow P(A\\cup B)=P(A)+P(B)"],
        contexto=("Un evento es cualquier subconjunto del espacio muestral: una "
                  "colección de resultados que nos interesa agrupar bajo una "
                  "pregunta ('¿salió par?', '¿la suma pasa de 8?', '¿hubo al menos "
                  "un 6?'). Como los eventos son conjuntos, se combinan con las "
                  "operaciones de la teoría de conjuntos —la UNIÓN A∪B ('A o B, o "
                  "ambos'), la INTERSECCIÓN A∩B ('A y B a la vez') y el COMPLEMENTO "
                  "Aᶜ ('no A')— y sus probabilidades siguen reglas exactas que son "
                  "el álgebra básica de la incertidumbre. La regla más importante, y "
                  "la que más se equivoca la gente, es la de la unión: P(A∪B) NO es "
                  "P(A)+P(B). Sumar las dos probabilidades cuenta DOS VECES los "
                  "resultados que pertenecen a ambos eventos, así que sobrestima. La "
                  "corrección es la regla de INCLUSIÓN-EXCLUSIÓN: P(A∪B) = P(A) + "
                  "P(B) − P(A∩B), donde se resta una vez la parte común para "
                  "compensar el doble conteo. Solo cuando A y B son MUTUAMENTE "
                  "EXCLUYENTES —no pueden ocurrir juntos, su intersección es vacía— "
                  "la resta desaparece y P(A∪B) = P(A)+P(B). La otra regla "
                  "imprescindible es la del COMPLEMENTO: P(Aᶜ) = 1 − P(A), que "
                  "parece trivial pero es una de las herramientas más poderosas del "
                  "cálculo de probabilidades, porque muchísimas veces es dramáticamente "
                  "más fácil calcular la probabilidad de lo CONTRARIO. La pregunta "
                  "'¿probabilidad de al menos un 6 en varios lanzamientos?' es "
                  "engorrosa por inclusión-exclusión (hay muchos casos que se "
                  "solapan), pero trivial por complemento: P(al menos uno) = 1 − "
                  "P(ninguno), y 'ninguno' es un simple producto (e41). Dominar "
                  "estas operaciones —unión con su corrección, complemento como "
                  "atajo, intersección como 'y'— es saber traducir preguntas del "
                  "lenguaje ('o', 'y', 'al menos', 'ninguno') al álgebra de la "
                  "probabilidad, que es de lo que trata buena parte del oficio."),
        autores=("El álgebra de eventos y la probabilidad como medida sobre "
                 "conjuntos: Kolmogórov (1933); la inclusión-exclusión es "
                 "combinatoria clásica — menciones. Conocimiento estadístico general."),
        supuestos=[
            "Los eventos son subconjuntos del mismo espacio muestral (e35); las operaciones (∪, ∩, ᶜ) son las de conjuntos.",
            "La inclusión-exclusión P(A∪B)=P(A)+P(B)−P(A∩B) vale SIEMPRE; se simplifica a P(A)+P(B) solo si A∩B=∅ (mutuamente excluyentes).",
            "Mutuamente excluyente (no ocurren juntos) NO es lo mismo que independiente (e41, no se influyen): son conceptos distintos que se confunden a menudo.",
        ],
        ecuaciones=[
            Ecuacion("P(A\\cup B) = P(A) + P(B) - P(A\\cap B)", "inclusión-exclusión",
                     "la probabilidad de 'A o B': se restan una vez los casos comunes para no contarlos dos "
                     "veces — sumar a secas sobrestima."),
            Ecuacion("P(A^c) = 1 - P(A)", "complemento",
                     "la probabilidad de 'no A' es 1 menos la de A: el atajo que convierte 'al menos uno' en "
                     "'1 − ninguno', a menudo mucho más fácil."),
            Ecuacion("A\\cap B = \\varnothing \\Rightarrow P(A\\cup B) = P(A)+P(B)", "mutuamente excluyentes",
                     "si los eventos no pueden ocurrir juntos, la unión es la suma simple: la "
                     "inclusión-exclusión sin término de corrección."),
        ],
        intuicion=("Los eventos son la gramática de la probabilidad: 'o' es unión, "
                   "'y' es intersección, 'no' es complemento, y traducir bien las "
                   "preguntas a esta gramática es la mitad del trabajo. El error "
                   "estrella —sumar P(A)+P(B) para la unión— nace de olvidar que las "
                   "cosas pueden solaparse: la probabilidad de 'que llueva o que "
                   "haga viento' no es la suma, porque los días de lluvia Y viento "
                   "se contarían dos veces. La imagen del diagrama de Venn lo hace "
                   "obvio: al sumar los dos círculos, la lente central va doble, y "
                   "hay que restarla una vez. El truco del complemento es la otra "
                   "gran arma: siempre que veas 'al menos uno', piensa en '1 menos "
                   "ninguno', porque 'ninguno' suele ser un caso único y limpio "
                   "mientras que 'al menos uno' es un enredo de casos solapados. Y "
                   "una distinción que salva de muchos errores: mutuamente "
                   "excluyente (no pueden pasar juntos) NO es independiente (no se "
                   "influyen). Sacar un rey y sacar una reina en UNA carta son "
                   "mutuamente excluyentes (una carta no es ambas) pero no "
                   "independientes; la altura y el peso de una persona son "
                   "'compatibles' pero no independientes. Confundirlos es de los "
                   "errores más comunes, y la probabilidad condicional (e39) es "
                   "quien los separa con precisión."),
        equilibrio=("Las operaciones de eventos obedecen: P(A∪B)=P(A)+P(B)−P(A∩B) "
                    "(siempre), P(Aᶜ)=1−P(A), y P(A∪B)=P(A)+P(B) solo si A∩B=∅. La "
                    "suma ingenua siempre sobrestima (o iguala) la unión real. No "
                    "hay 'equilibrio': es el álgebra de la incertidumbre."),
        limitaciones=[
            "La inclusión-exclusión se complica con muchos eventos: para tres, P(A∪B∪C) suma singles, resta pares y vuelve a sumar el triple — crece en complejidad (por eso el complemento suele ser mejor para 'al menos uno').",
            "Mutuamente excluyente vs independiente: confundirlos lleva a aplicar la fórmula equivocada; son propiedades distintas (e41).",
            "Estas reglas dan probabilidades de combinaciones, pero NO capturan cómo un evento cambia la probabilidad de otro: eso es la probabilidad condicional (e39).",
        ],
        evolucion=("Construye el álgebra de eventos sobre el espacio muestral (e35): "
                   "unión, intersección, complemento e inclusión-exclusión. La "
                   "distinción mutuamente-excluyente vs independiente prepara la "
                   "probabilidad condicional (e39) y la independencia (e41). El "
                   "cálculo de P(evento) por conteo lleva a la probabilidad clásica "
                   "(e37). Estas operaciones son la base para combinar "
                   "probabilidades en toda la sección y en la inferencia."),
    ),
    escenarios=[
        Escenario("solapados", "eventos que se solapan (suma ≥ 8 y un 6)",
                  {"t": 8},
                  "A='suma≥8' y B='al menos un 6' se solapan (hay tiradas con un 6 "
                  "y suma ≥8): sumar P(A)+P(B) sobrestima, hay que restar P(A∩B). El "
                  "caso general de la inclusión-exclusión.",
                  cadena=["A='suma≥8', B='al menos un 6'", "se solapan (un 6 puede dar suma ≥8)",
                          "P(A)+P(B) cuenta el solapamiento dos veces", "restar P(A∩B) lo corrige (inclusión-exclusión)"]),
        Escenario("excluyentes", "eventos incompatibles (suma extrema)",
                  {"t": 12},
                  "A='suma≥12' (solo 12) y 'suma=2' no pueden ocurrir juntos: son "
                  "mutuamente excluyentes, y ahí sí P(A∪B)=P(A)+P(B) sin restar nada "
                  "(la intersección es vacía).",
                  cadena=["eventos incompatibles (suma=12 vs suma=2)", "no pueden ocurrir en la misma tirada",
                          "intersección vacía (A∩B=∅)", "P(A∪B)=P(A)+P(B) sin corrección"]),
    ],
    verificaciones=[
        Verificacion("inclusión-exclusión: P(A∪B)=P(A)+P(B)−P(A∩B)", _v_inclusion_exclusion),
        Verificacion("la suma ingenua P(A)+P(B) sobrestima la unión", _v_sobrestima_naive),
        Verificacion("complemento: P(Aᶜ)=1−P(A)", _v_complemento),
        Verificacion("mutuamente excluyentes: P(A∪B)=P(A)+P(B)", _v_mutuamente_excluyentes),
    ],
    notas="Evento = subconjunto de Ω. Operaciones: ∪(o), ∩(y), ᶜ(no). Inclusión-exclusión P(A∪B)=P(A)+P(B)−P(A∩B): sumar a secas cuenta dos veces la intersección. Complemento P(Aᶜ)=1−P(A): el atajo para 'al menos uno'=1−'ninguno'. Excluyente (no juntos) ≠ independiente (no se influyen, e41).",
)
