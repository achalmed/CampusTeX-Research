"""simuladores/estadistica/modelos/nivel_02/e26_rango.py — el rango (sección II, tema 26).

La medida de dispersión más simple: rango = máximo − mínimo. Se calcula de un
vistazo, pero tiene dos defectos graves que este modelo hace visibles. Primero,
NO es robusto: depende SOLO de los dos valores extremos, así que un único
atípico lo cambia por completo (punto de ruptura 0%). Segundo, y menos obvio,
CRECE con el tamaño de la muestra: cuantos más datos observas, más chances hay
de ver un valor muy alto o muy bajo, así que el rango se estira sin parar —a
diferencia del IQR (e23) o la desviación (e27), que se estabilizan—. Por eso el
rango describe el peor caso observado, no la dispersión típica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_POB = np.random.default_rng(5).normal(50.0, 10.0, 200000)   # población normal (σ=10)


def _muestral(n, reps=4000, semilla=2024):
    rng = np.random.default_rng(semilla)
    idx = rng.integers(0, len(_POB), size=(reps, int(n)))
    m = _POB[idx]
    rango = m.max(axis=1) - m.min(axis=1)
    iqr = np.percentile(m, 75, axis=1) - np.percentile(m, 25, axis=1)
    return float(rango.mean()), float(iqr.mean())


def _curvas(p):
    ns = np.array([2, 5, 10, 20, 50, 100, 200, 400])
    rangos = np.array([_muestral(n)[0] for n in ns])
    iqrs = np.array([_muestral(n)[1] for n in ns])
    n0 = int(p["n"])
    r0, i0 = _muestral(n0)
    return {"lineas": {"rango medio (máx − mín): CRECE con n": (ns, rangos, config.ROJO),
                       "IQR medio (50% central): se ESTABILIZA": (ns, iqrs, config.AZUL2)},
            "puntos": [(n0, r0, f"n={n0} → rango {r0:.1f}")],
            "anotacion": (f"población normal, σ = 10 (n = {n0})\n"
                          f"rango medio = {r0:.1f} (sigue subiendo con n)\n"
                          f"IQR medio = {i0:.1f} (estable ≈ 1.35·σ): el rango depende de n, el IQR no")}


def _resultados(p):
    n0 = int(p["n"])
    r0, i0 = _muestral(n0)
    r_chico = _muestral(10)[0]
    r_grande = _muestral(400)[0]
    return {"tamaño de muestra n": float(n0),
            "rango medio (máx − mín)": r0,
            "IQR medio (comparación, estable)": i0,
            "rango con n=10 (chico)": r_chico,
            "rango con n=400 (grande)": r_grande,
            "cuánto crece el rango de n=10 a n=400": r_grande - r_chico}


def _ecuaciones_calibradas(p):
    n0 = int(p["n"])
    r0, i0 = _muestral(n0)
    return [f"\\mathrm{{rango}} = x_{{\\max}} - x_{{\\min}} = {r0:.1f}\\ \\text{{(depende de los dos extremos)}}",
            f"\\text{{crece con }} n;\\ \\mathrm{{IQR}} = {i0:.1f}\\ \\text{{se estabiliza}};\\ \\mathrm{{rango}} \\geq \\mathrm{{IQR}}"]


_P0 = {"n": 20}


def _v_definicion():
    x = np.array([3, 7, 5, 12, 4, 9], float)
    return abs((x.max() - x.min()) - 9.0) < 1e-9, \
        (f"el rango es máximo − mínimo = {x.max():.0f} − {x.min():.0f} = {x.max()-x.min():.0f}: la medida de "
         "dispersión más simple, calculable de un vistazo — pero usa solo dos datos, ignora todos los del medio")


def _v_no_robusto():
    x = np.array([3, 7, 5, 12, 4, 9], float)
    r0 = x.max() - x.min()
    x2 = np.append(x, 200.0)
    r1 = x2.max() - x2.min()
    return r1 > 15 * r0, \
        (f"el rango NO es robusto: un solo atípico (200) lo lleva de {r0:.0f} a {r1:.0f} — punto de ruptura 0%, "
         "porque depende SOLO de los extremos; el IQR (e23), en cambio, ni se inmuta")


def _v_crece_con_n():
    r10 = _muestral(10)[0]
    r400 = _muestral(400)[0]
    return r400 > r10 * 1.3, \
        (f"el rango CRECE con el tamaño de muestra: de {r10:.1f} (n=10) a {r400:.1f} (n=400) — más datos = más "
         "chances de ver un extremo. Por eso el rango no es comparable entre muestras de distinto tamaño (el IQR sí)")


def _v_rango_mayor_iqr():
    for n in (10, 50, 200):
        r, i = _muestral(n)
        if r < i:
            return False, f"con n={n} el rango ({r:.1f}) resultó menor que el IQR ({i:.1f})"
    return True, \
        ("el rango SIEMPRE es ≥ el IQR: abarca el 100% de los datos, el IQR solo el 50% central — el rango es la "
         "dispersión máxima observada, el IQR la típica y robusta")


MODELO = Modelo(
    id="e26", nivel=2,
    nombre="El rango",
    xlabel="tamaño de muestra  n", ylabel="dispersión",
    parametros=[
        Parametro("n", _P0["n"], 2, 400, 2, "Tamaño de muestra n",
                  grupo="descriptiva", definicion="el rango medio crece con n (más chances de extremos); el IQR no"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="La dispersión más fácil de calcular es máx − mín. ¿Por qué los estadísticos casi nunca la usan?",
        variables=[("rango", "máximo − mínimo"),
                   ("n", "tamaño de muestra"),
                   ("IQR", "rango intercuartílico (e23), la alternativa robusta y estable")],
        derivacion=["\\mathrm{rango} = x_{\\max} - x_{\\min} \\;(\\text{solo los dos extremos})",
                    "\\text{depende de 2 datos} \\Rightarrow \\text{punto de ruptura } 0\\% \\;(\\text{no robusto})",
                    "\\text{más } n \\Rightarrow \\text{más chances de extremos} \\Rightarrow E[\\mathrm{rango}] \\uparrow",
                    "\\mathrm{rango} \\ge \\mathrm{IQR} \\;(100\\% \\text{ vs } 50\\% \\text{ central})"],
        contexto=("El rango es la medida de dispersión que cualquiera inventaría "
                  "primero: la distancia entre el valor más alto y el más bajo. Su "
                  "única virtud es la simplicidad —se calcula de un vistazo, sin "
                  "fórmulas— y por eso se usa en control de calidad rápido y en "
                  "reportes informales ('las temperaturas fueron de 12 a 28 "
                  "grados'). Pero tiene dos defectos que lo descalifican como medida "
                  "seria de dispersión, y este modelo los hace visibles. El primero "
                  "es que NO es robusto: el rango depende exclusivamente de los dos "
                  "valores extremos e ignora todos los demás, así que un solo "
                  "atípico —un error de tipeo, un caso raro— lo cambia por completo. "
                  "Su punto de ruptura es 0%, el peor posible, igual que el de la "
                  "media y la desviación (e32). El segundo defecto es más sutil y "
                  "más grave para comparar: el rango CRECE sistemáticamente con el "
                  "tamaño de la muestra. La razón es intuitiva una vez que se ve: "
                  "cuantas más observaciones tomas, más oportunidades hay de "
                  "toparte con un valor excepcionalmente alto o bajo, así que el "
                  "máximo tiende a subir y el mínimo a bajar sin límite. Una muestra "
                  "de 10 tiene un rango típico; una de 1000 de la MISMA población "
                  "tiene un rango bastante mayor, aunque la población no cambió. "
                  "Esto significa que el rango NO es comparable entre muestras de "
                  "distinto tamaño —un defecto fatal—, mientras que el IQR (e23) y "
                  "la desviación estándar (e27) se estabilizan en un valor que "
                  "refleja la dispersión real de la población, sin importar n. La "
                  "lección: el rango describe el PEOR CASO observado (útil a veces: "
                  "el margen de un puente, el rango de temperaturas de diseño), pero "
                  "no la dispersión TÍPICA. Para eso, casi siempre, el IQR o la "
                  "desviación son las respuestas correctas."),
        autores=("El rango como estadístico de dispersión es tan viejo como la "
                 "medición; su dependencia de n y su uso en control de calidad "
                 "(cartas de rango) son de la estadística industrial (Shewhart) — "
                 "menciones. Conocimiento estadístico general."),
        supuestos=[
            "Datos cuantitativos ordenables; el rango solo necesita el máximo y el mínimo.",
            "Su crecimiento con n vale para poblaciones sin cota (normales, etc.): en poblaciones acotadas el rango se satura al acercarse a los límites — pero igual crece con n hasta ahí.",
            "El rango informa del PEOR caso observado, no de la dispersión típica: útil cuando importan los extremos (tolerancias, márgenes), engañoso como resumen general.",
        ],
        ecuaciones=[
            Ecuacion("\\mathrm{rango} = x_{\\max} - x_{\\min}", "el rango",
                     "la distancia entre los dos extremos: la dispersión más simple, pero que usa solo dos "
                     "datos e ignora todos los del medio."),
            Ecuacion("\\text{punto de ruptura} = 0\\%", "no es robusto",
                     "depende exclusivamente de los extremos, así que un solo atípico lo cambia por completo — "
                     "tan frágil como la media (e32)."),
            Ecuacion("E[\\mathrm{rango}] \\uparrow \\text{ con } n \\quad ; \\quad \\mathrm{rango} \\ge \\mathrm{IQR}", "crece con n",
                     "más datos, más chances de extremos, mayor rango: no es comparable entre muestras de "
                     "distinto tamaño (el IQR y la desviación sí). Y siempre ≥ IQR (100% vs 50% central)."),
        ],
        intuicion=("El rango es la dispersión 'de titular': fácil de decir, fácil de "
                   "entender, y casi siempre engañosa. Su problema profundo —que "
                   "crece con n— es una de esas verdades estadísticas que, una vez "
                   "vistas, no se olvidan: si mides la altura de 10 personas al azar "
                   "y luego de 10.000, el rango de las 10.000 será mucho mayor, no "
                   "porque la gente sea más diversa, sino porque con más gente es "
                   "casi seguro que aparezca alguien muy alto y alguien muy bajito. "
                   "El rango, entonces, mide en parte cuántos datos tienes, no solo "
                   "cuán dispersos están —y por eso no sirve para comparar—. Es el "
                   "reflejo perfecto de por qué la estadística prefiere medidas que "
                   "convergen a una propiedad de la POBLACIÓN (como el IQR o la "
                   "desviación, que se estabilizan) sobre las que dependen de la "
                   "muestra. Dicho esto, el rango tiene su nicho honesto: cuando lo "
                   "que importa es literalmente el extremo —la tolerancia máxima de "
                   "una pieza, la temperatura de diseño de un material, la peor "
                   "pérdida posible—, el peor caso ES la pregunta, y el rango la "
                   "responde. La sabiduría está en no confundir 'el peor caso "
                   "observado' con 'la dispersión típica': son preguntas distintas, "
                   "y usar el rango para la segunda es el error."),
        equilibrio=("El rango es único (máx − mín), no robusto (ruptura 0%), y su "
                    "valor esperado CRECE monótonamente con n (sin límite en "
                    "poblaciones no acotadas), mientras el IQR y la desviación se "
                    "estabilizan. Siempre rango ≥ IQR. No 'converge' a un parámetro "
                    "poblacional: por eso no es una buena medida de dispersión."),
        limitaciones=[
            "No robusto (ruptura 0%): un atípico lo determina; usa solo 2 de los n datos, desperdiciando toda la información del centro.",
            "Depende del tamaño de muestra: crece con n, así que NO es comparable entre muestras distintas — su defecto más descalificante como resumen.",
            "Solo informa de los extremos: no dice nada de cómo se distribuyen los datos en el medio (para eso, IQR e23, desviación e27, o la forma completa).",
        ],
        evolucion=("Es la dispersión más simple y la puerta a entender por qué se "
                   "necesitan medidas mejores: el IQR (e23, robusto y estable) y la "
                   "varianza/desviación (e27, que usa todos los datos). Su "
                   "dependencia de n es una primera lección de que un estadístico "
                   "muestral debe converger a una propiedad poblacional (idea que "
                   "madura en el muestreo, sección VI, y en la consistencia de "
                   "estimadores, e86). Con el IQR (e23) y la desviación (e27) "
                   "completa las medidas de dispersión; sigue la dispersión RELATIVA "
                   "(coeficiente de variación, e29) y la FORMA (e30-e31)."),
    ),
    escenarios=[
        Escenario("muestra_chica", "muestra pequeña (n = 10)",
                  {"n": 10},
                  "con n=10 el rango es moderado: pocas observaciones, pocas "
                  "chances de ver un extremo. Pero este número no es comparable con "
                  "el de una muestra mayor de la misma población.",
                  cadena=["muestra pequeña (n=10)", "pocas chances de valores extremos",
                          "rango moderado", "pero no comparable con otra n"]),
        Escenario("muestra_grande", "muestra grande (n = 400): el rango se estira",
                  {"n": 400},
                  "con n=400, el rango medio es bastante mayor que con n=10 —aunque "
                  "la población es idéntica—: más datos = más extremos. El IQR, en "
                  "cambio, es casi el mismo. Esto descalifica al rango para comparar.",
                  cadena=["muestra grande (n=400)", "muchas chances de un máximo alto y un mínimo bajo",
                          "el rango medio crece (vs n=10)", "el IQR no cambia — el rango depende de n, mal"]),
    ],
    verificaciones=[
        Verificacion("rango = máximo − mínimo", _v_definicion),
        Verificacion("el rango NO es robusto (un atípico lo cambia)", _v_no_robusto),
        Verificacion("el rango crece con el tamaño de muestra n", _v_crece_con_n),
        Verificacion("el rango siempre es ≥ el IQR", _v_rango_mayor_iqr),
    ],
    notas="Rango = máx − mín: la dispersión más simple. Dos defectos: NO robusto (un atípico lo cambia, ruptura 0%) y CRECE con n (más datos → más extremos), así que no es comparable entre muestras. El IQR (e23) y la desviación (e27) se estabilizan. Útil solo para el peor caso.",
)
