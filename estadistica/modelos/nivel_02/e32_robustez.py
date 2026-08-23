# e32_robustez.py — medidas robustas y detección de atípicos (sección II, temas 32-33).
#
# La síntesis de la descriptiva: qué estadísticos resisten a un valor extremo y
# cuáles no. Al mover un dato atípico, la MEDIA y la DESVIACIÓN ESTÁNDAR lo
# persiguen sin límite (punto de ruptura 0%), mientras que la MEDIANA (e18) y la
# MAD (desviación absoluta mediana) ni se inmutan (punto de ruptura 50%). El
# modelo grafica cómo responde cada medida a la posición del outlier —las no
# robustas trepan, las robustas quedan planas— y usa la regla robusta (z
# modificado con MAD) para DETECTAR el atípico. La versión interactiva con slider
# es demos/robustez_interactiva.py.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_BASE = np.array([4, 5, 5, 6, 6, 6, 7, 7, 8], float)   # 9 datos "normales" (mediana=6)


def _mad(x):
    """Desviación absoluta mediana: median(|xᵢ − median(x)|). Dispersión robusta."""
    return float(np.median(np.abs(x - np.median(x))))


def _stats(outlier):
    x = np.append(_BASE, outlier)
    return {"media": float(x.mean()), "mediana": float(np.median(x)),
            "desv": float(x.std()), "mad": _mad(x)}


def _z_modificado(x, dato):
    """z robusto (Iglewicz-Hoaglin): 0.6745·(dato−mediana)/MAD. |z|>3.5 ⇒ atípico."""
    mad = _mad(x)
    return 0.6745 * (dato - np.median(x)) / mad if mad > 0 else 0.0


def _curvas(p):
    o = p["outlier"]
    grid = np.linspace(0, 40, 200)
    media = np.array([_stats(v)["media"] for v in grid])
    mediana = np.array([_stats(v)["mediana"] for v in grid])
    desv = np.array([_stats(v)["desv"] for v in grid])
    mad = np.array([_stats(v)["mad"] for v in grid])
    return {"lineas": {"media (NO robusta, la persigue)": (grid, media, config.AZUL2),
                       "desv. estándar (NO robusta, trepa)": (grid, desv, config.ROJO),
                       "mediana (robusta, plana)": (grid, mediana, config.DORADO),
                       "MAD (robusta, plana)": (grid, mad, config.VERDE)},
            "puntos": [(o, _stats(o)["media"], f"outlier = {o:.0f}")],
            "anotacion": (f"al alejar el dato extremo (eje x):\n"
                          f"media y desv. lo PERSIGUEN (ruptura 0%)\n"
                          f"mediana y MAD ni se mueven (ruptura 50%)")}


def _resultados(p):
    o = p["outlier"]
    s = _stats(o)
    x = np.append(_BASE, o)
    return {"dato extremo (outlier)": o,
            "media": s["media"],
            "mediana": s["mediana"],
            "desviación estándar": s["desv"],
            "MAD (dispersión robusta)": s["mad"],
            "z robusto del outlier": _z_modificado(x, o),
            "¿outlier detectado? (|z|>3.5)": 1.0 if abs(_z_modificado(x, o)) > 3.5 else 0.0}


def _ecuaciones_calibradas(p):
    o = p["outlier"]
    s = _stats(o)
    return [f"\\text{{outlier}}={o:.0f}:\\ \\text{{media}}={s['media']:.1f}\\ \\text{{(movida)}},\\ \\text{{mediana}}={s['mediana']:.1f}\\ \\text{{(firme)}}",
            f"\\mathrm{{MAD}} = \\mathrm{{med}}(|x_i-\\mathrm{{med}}(x)|)\\qquad z = 0.6745\\,(x-\\mathrm{{med}})/\\mathrm{{MAD}}"]


_P0 = {"outlier": 8.0}


def _v_media_persigue():
    lejos, cerca = _stats(38.0)["media"], _stats(8.0)["media"]
    return lejos > cerca + 2.5, \
        (f"la MEDIA persigue al outlier: al moverlo de 8 a 38 sube de {cerca:.1f} a {lejos:.1f} — punto de "
         "ruptura 0%, un solo dato la arrastra sin límite (e17); lo mismo la desviación estándar (e27)")


def _v_mediana_resiste():
    valores = [_stats(v)["mediana"] for v in (0.0, 8.0, 20.0, 40.0)]
    return max(valores) - min(valores) < 1e-9, \
        (f"la MEDIANA no se inmuta: con el outlier en 0, 8, 20 o 40 sigue valiendo {valores[0]:.0f} — punto de "
         "ruptura 50% (e18); a ella solo le importa el LADO del dato, no cuán lejos")


def _v_mad_robusta():
    desv_lejos, desv_cerca = _stats(38.0)["desv"], _stats(8.0)["desv"]
    mad_lejos, mad_cerca = _stats(38.0)["mad"], _stats(8.0)["mad"]
    return desv_lejos > 3 * desv_cerca and abs(mad_lejos - mad_cerca) < 1e-9, \
        (f"la desviación estándar EXPLOTA (de {desv_cerca:.1f} a {desv_lejos:.1f}) pero la MAD queda igual "
         f"({mad_cerca:.1f}): la MAD es la dispersión robusta, análoga a la mediana — resiste al atípico")


def _v_deteccion():
    x_lejos = np.append(_BASE, 38.0)
    x_cerca = np.append(_BASE, 8.0)
    z_lejos = abs(_z_modificado(x_lejos, 38.0))
    z_cerca = abs(_z_modificado(x_cerca, 8.0))
    return z_lejos > 3.5 and z_cerca < 3.5, \
        (f"la regla robusta DETECTA el atípico: el dato en 38 tiene z modificado {z_lejos:.1f} > 3.5 (atípico), "
         f"el dato en 8 tiene {z_cerca:.1f} < 3.5 (normal) — se usa la MAD, no la desviación (que el propio outlier infla)")


MODELO = Modelo(
    id="e32", nivel=2,
    nombre="Medidas robustas y detección de atípicos",
    xlabel="posición del dato extremo (outlier)", ylabel="valor del estadístico",
    parametros=[
        Parametro("outlier", _P0["outlier"], 0.0, 40.0, 1.0, "Posición del dato extremo",
                  grupo="robustez", definicion="al alejarlo, las medidas no robustas lo persiguen; las robustas resisten"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando un dato está claramente fuera de lugar, ¿qué estadísticos siguen siendo confiables — y cómo se detecta ese atípico?",
        variables=[("punto de ruptura", "% de datos que hay que corromper para arruinar la medida"),
                   ("media, desv. estándar", "NO robustas (ruptura 0%)"),
                   ("mediana, MAD, IQR", "robustas (ruptura 50%)"),
                   ("z modificado", "0.6745·(x−mediana)/MAD; |z|>3.5 marca atípico")],
        derivacion=["\\text{robustez} \\leftrightarrow \\text{punto de ruptura: } \\% \\text{ de datos que la arruinan}",
                    "\\text{media, } \\sigma: 0\\% \\;(\\text{un dato basta}) \\;;\\; \\text{mediana, MAD}: 50\\%",
                    "\\mathrm{MAD} = \\mathrm{med}(|x_i - \\mathrm{med}(x)|) \\;(\\text{dispersión robusta})",
                    "\\text{atípico si } |0.6745\\,(x-\\mathrm{med})/\\mathrm{MAD}| > 3.5"],
        contexto=("Este modelo cierra la estadística descriptiva juntando todo lo "
                  "anterior bajo una sola pregunta práctica: ¿qué pasa cuando los "
                  "datos están sucios? Casi nunca lo están del todo —hay errores de "
                  "tipeo, sensores que fallan, casos genuinamente atípicos—, y la "
                  "diferencia entre un análisis honesto y uno engañoso suele estar "
                  "en cómo se tratan esos valores extremos. La herramienta "
                  "conceptual es el PUNTO DE RUPTURA: qué fracción de los datos hay "
                  "que corromper para arruinar una medida. La media y la desviación "
                  "estándar tienen punto de ruptura 0% —un solo dato extremo las "
                  "arrastra sin límite, porque ambas se apoyan en el cuadrado de las "
                  "desviaciones (e17, e27)—. La mediana (e18) y su prima de "
                  "dispersión, la MAD (desviación absoluta mediana = la mediana de "
                  "las distancias a la mediana), tienen punto de ruptura 50%: harían "
                  "falta corromper la MITAD de los datos para moverlas. El "
                  "laboratorio lo hace visible: al deslizar un dato atípico cada vez "
                  "más lejos, la media y la desviación lo persiguen (trepan sin "
                  "freno) mientras la mediana y la MAD quedan perfectamente planas. "
                  "De ahí sale también cómo DETECTAR un atípico de forma confiable: "
                  "no con la desviación estándar (que el propio outlier ya infló, "
                  "enmascarándose a sí mismo), sino con una regla ROBUSTA —el z "
                  "modificado, que mide la distancia a la mediana en unidades de "
                  "MAD, y marca como atípico todo |z|>3.5—. La lección de fondo no "
                  "es 'la mediana es mejor que la media', sino que cada medida tiene "
                  "un dominio: con datos limpios y simétricos, la media y la "
                  "desviación son más eficientes; con datos sucios o asimétricos, "
                  "las robustas son las honestas. Un buen analista mira AMBAS: si "
                  "coinciden, los datos están limpios; si divergen, hay atípicos que "
                  "investigar —nunca borrar a ciegas, sino entender por qué están—."),
        autores=("Estadística robusta: John Tukey (introdujo 'robustez' y el "
                 "boxplot, años 1970), Peter Huber, Frank Hampel (punto de "
                 "ruptura); la MAD y el z modificado: Iglewicz-Hoaglin (1993) — "
                 "menciones. Conocimiento estadístico general."),
        supuestos=[
            "El punto de ruptura mide robustez ante contaminación arbitraria: no supone ninguna distribución, es una propiedad del estimador.",
            "La MAD se escala por 1/0.6745 ≈ 1.4826 para estimar σ en datos normales; el z modificado usa 0.6745 para que el umbral 3.5 sea comparable a ~3.5 desviaciones.",
            "Detectar un atípico NO es lo mismo que eliminarlo: la regla señala candidatos a investigar; borrar datos exige justificación sustantiva, no estadística.",
        ],
        ecuaciones=[
            Ecuacion("\\text{media}, \\sigma: \\;\\text{ruptura } 0\\% \\;;\\; \\text{mediana, MAD}: \\;50\\%", "el punto de ruptura",
                     "cuántos datos hay que corromper para arruinar la medida: a la media/desviación les "
                     "basta uno; a la mediana/MAD, la mitad — la definición operativa de robustez."),
            Ecuacion("\\mathrm{MAD} = \\mathrm{med}\\,(|x_i - \\mathrm{med}(x)|)", "dispersión robusta",
                     "la mediana de las distancias a la mediana: mide dispersión como la desviación estándar, "
                     "pero resistiendo a los atípicos (es a σ lo que la mediana es a la media)."),
            Ecuacion("|0.6745\\,(x-\\mathrm{med})/\\mathrm{MAD}| > 3.5 \\Rightarrow \\text{atípico}", "detección robusta",
                     "distancia a la mediana en unidades de MAD: usa medidas robustas para no dejar que el "
                     "propio outlier infle la referencia y se esconda (lo que pasaría con la desviación)."),
        ],
        intuicion=("La imagen es la de una foto de grupo en la que se cuela una "
                   "jirafa: si describes la 'estatura promedio', la jirafa la "
                   "dispara y el número no representa a nadie; si describes la "
                   "estatura MEDIANA, la jirafa es irrelevante y el número sigue "
                   "describiendo a las personas. Lo mismo con la dispersión: la "
                   "desviación estándar 've' la jirafa y estalla; la MAD la ignora. "
                   "Y para DETECTAR a la jirafa, el truco fino es no medir su rareza "
                   "con una regla que ella misma ya deformó —usar la desviación "
                   "estándar para cazar outliers es como preguntarle al sospechoso "
                   "si es culpable: el outlier infla σ y así se hace parecer normal—; "
                   "por eso se mide con la MAD, que él no pudo mover. La lección que "
                   "un analista se lleva para siempre: reportar SIEMPRE media y "
                   "mediana juntas. Si están cerca, los datos son limpios y "
                   "simétricos, usa la media (más eficiente). Si divergen, hay algo "
                   "—asimetría, atípicos, dos poblaciones mezcladas— que entender "
                   "antes de resumir. La robustez no es paranoia; es la humildad de "
                   "no dejar que un solo dato dicte la conclusión."),
        equilibrio=("No hay equilibrio: hay una jerarquía de robustez medida por el "
                    "punto de ruptura. Media/desviación: 0% (un outlier las rompe). "
                    "Mediana/MAD/IQR: 50% (el máximo posible). El z modificado con "
                    "MAD detecta atípicos sin que estos enmascaren la referencia."),
        limitaciones=[
            "Robustez cuesta eficiencia: con datos limpios y normales, la media y la desviación aprovechan mejor los datos que la mediana y la MAD — robustez y eficiencia son un trade-off.",
            "El umbral 3.5 del z modificado (y el 1.5·IQR del boxplot, e15) son convenciones razonables, no leyes: marcan candidatos, no veredictos.",
            "Detectar ≠ eliminar: un atípico puede ser un error (corregir/quitar con justificación) o el dato más importante (un fraude, una crisis) — la estadística lo señala, el juicio sustantivo decide.",
        ],
        evolucion=("Cierra la descriptiva sintetizando centro (media e17 / mediana "
                   "e18) y dispersión (desviación e27 / MAD) bajo la lente de la "
                   "robustez, y conecta con el boxplot (e15, la regla 1.5·IQR) y los "
                   "cuartiles (e23). La idea de 'no dejar que un dato dicte la "
                   "conclusión' reaparece en la regresión robusta (diagnóstico e148, "
                   "distancia de Cook e151) y en toda la estadística aplicada. Con "
                   "esto, la sección II queda completa: sabemos describir un conjunto "
                   "de datos —su centro, su dispersión, su forma y sus rarezas—."),
    ),
    escenarios=[
        Escenario("dato_normal", "el dato extremo cerca del grupo (outlier = 8)",
                  {"outlier": 8.0},
                  "con el dato en 8 (pegado al resto) todas las medidas coinciden: "
                  "media ≈ mediana, desviación pequeña, MAD pequeña, y la regla "
                  "robusta NO lo marca. Datos limpios: da igual qué medida uses.",
                  cadena=["dato extremo en 8 (dentro del grupo)", "media ≈ mediana (datos simétricos)",
                          "desviación y MAD pequeñas y parecidas", "z robusto < 3.5: no es atípico"]),
        Escenario("outlier_lejano", "el dato se aleja (outlier = 38)",
                  {"outlier": 38.0},
                  "al llevar el dato a 38, la media y la desviación lo persiguen "
                  "(suben mucho) mientras la mediana y la MAD quedan clavadas: las "
                  "robustas resisten. Y la regla del z robusto lo detecta (|z|>3.5).",
                  cadena=["dato extremo en 38 (lejos)", "media y desviación trepan (ruptura 0%)",
                          "mediana y MAD no se mueven (ruptura 50%)", "z robusto > 3.5: ATÍPICO detectado"]),
    ],
    verificaciones=[
        Verificacion("media y desviación persiguen al outlier (ruptura 0%)", _v_media_persigue),
        Verificacion("la mediana resiste (ruptura 50%)", _v_mediana_resiste),
        Verificacion("la MAD es robusta; la desviación explota", _v_mad_robusta),
        Verificacion("la regla robusta (z con MAD) detecta el atípico", _v_deteccion),
    ],
    notas="Robustez = punto de ruptura. Media/desviación: 0% (un outlier las arrastra). Mediana/MAD: 50% (resisten). Detectar atípicos con z modificado (MAD), no con la desviación (que el outlier ya infló). Vista interactiva: demos/robustez_interactiva.py.",
)
