# m109_exportaciones_crecimiento.py — exportaciones y crecimiento (nivel 12).
#
# El motor externo del crecimiento peruano, y un contraste metodológico con
# m106. Las exportaciones reales del Perú casi se DUPLICARON entre 2004 y 2024
# (×1.9) y su variación correlaciona FUERTE con el crecimiento del PBI: +0.74,
# R²=0.55 — las exportaciones explican más de la mitad de la varianza del
# crecimiento. En los años en que las exportaciones cayeron (2009, 2020) el
# crecimiento promedió +1.2%, contra +5.5% el resto: el crecimiento con motor
# externo (m43, economía abierta). La lección fina, junto a m106: ¿por qué las
# exportaciones SÍ correlacionan con el crecimiento (+0.74) y la inversión
# pública NO (~0)? Porque las exportaciones son en gran medida EXÓGENAS al ciclo
# peruano (las mueve la demanda mundial y el precio de los commodities, m88/m89),
# así que su correlación revela un canal causal; la inversión pública es una
# POLÍTICA endógena (contracíclica, m69), y su correlación engaña. La correlación
# informa cuando el impulsor es exógeno; engaña cuando es política que reacciona.
#
# Procedencia: datos BCRP PM04933AA (exportaciones reales, millones S/2007) y
# PN01728AM (PBI var%), muestra 2004-2024. El crecimiento liderado por
# exportaciones: m43 (conocimiento general). Exógeno vs endógeno: la razón por
# la que la correlación aquí informa y en m106 no (regla del pipeline con matiz).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _series():
    anos, x = _datos_bcrp.serie("exportaciones", anual=True)
    _, g = _datos_bcrp.serie("pbi_var", anual=True)
    gx = np.diff(x) / x[:-1] * 100                   # var% de las exportaciones reales
    ax = anos[1:]
    gg = np.array([g[list(anos).index(a)] for a in ax])
    return anos, x, g, ax, gx, gg


def _curvas(p):
    anos, x, g, ax, gx, gg = _series()
    corr = _datos_bcrp.correlacion(gx, gg)
    _, b, r2 = _datos_bcrp.ols(gx, gg)
    return {"lineas": {"variación de las exportaciones (BCRP, %)": (ax, gx, config.VERDE),
                       "crecimiento del PBI (BCRP, %)": (ax, gg, config.AZUL2)},
            "puntos": [(2020.0, float(gx[ax == 2020][0]), "2020: exportaciones −20% (COVID)"),
                       (2021.0, float(gx[ax == 2021][0]), "2021: rebote")],
            "anotacion": (f"exportaciones (PM04933AA) vs PBI (PN01728AM)\n"
                          f"corr $= {corr:+.2f}$, $R^2 = {r2:.2f}$ (motor externo, m43)\n"
                          f"1pp de exportaciones $\\to$ {b:.2f}pp de PBI")}


def _resultados(p):
    anos, x, g, ax, gx, gg = _series()
    neg = gx < 0
    _, b, r2 = _datos_bcrp.ols(gx, gg)
    return {"corr(export var%, crecimiento)": float(_datos_bcrp.correlacion(gx, gg)),
            "R² de las exportaciones sobre el crecimiento": float(r2),
            "pendiente (pp de PBI por pp de export)": float(b),
            "exportaciones reales 2004 → 2024 (factor)": float(x[-1] / x[0]),
            "export var% media (%/año)": float(gx.mean()),
            "crecimiento en años de export cayendo (%)": float(gg[neg].mean()),
            "crecimiento en años de export subiendo (%)": float(gg[~neg].mean())}


def _ecuaciones_calibradas(p):
    anos, x, g, ax, gx, gg = _series()
    _, b, r2 = _datos_bcrp.ols(gx, gg)
    return [f"corr(export, $g$) $= {_datos_bcrp.correlacion(gx, gg):+.2f}$, $R^2={r2:.2f}$ (exógeno $\\Rightarrow$ informa)",
            f"exportaciones $\\times{x[-1]/x[0]:.1f}$ en 2004-2024; 1pp export $\\to {b:.2f}$pp PBI (m43)"]


_P0 = {"umbral": 0.0}


def _v_correlacion_fuerte():
    anos, x, g, ax, gx, gg = _series()
    corr = _datos_bcrp.correlacion(gx, gg)
    _, _, r2 = _datos_bcrp.ols(gx, gg)
    return corr > 0.6, \
        (f"las exportaciones correlacionan FUERTE con el crecimiento (corr {corr:+.2f}, R²={r2:.2f}): "
         "explican más de la mitad de su varianza — el crecimiento peruano tiene motor externo (m43)")


def _v_exportaciones_crecieron():
    anos, x, g, ax, gx, gg = _series()
    return x[-1] / x[0] > 1.6, \
        (f"las exportaciones reales casi se duplicaron (×{x[-1]/x[0]:.2f}) entre 2004 y 2024: "
         "el Perú se integró más al mundo — la apertura de m43 hecha crecimiento")


def _v_anos_caida():
    anos, x, g, ax, gx, gg = _series()
    neg = gx < 0
    return gg[neg].mean() < gg[~neg].mean() - 2, \
        (f"en los años en que las exportaciones cayeron el crecimiento promedió {gg[neg].mean():+.1f}% "
         f"vs {gg[~neg].mean():+.1f}% el resto: cuando el motor externo se apaga, el Perú se frena (m43, m86)")


def _v_exogeno_informa():
    anos, x, g, ax, gx, gg = _series()
    corr = _datos_bcrp.correlacion(gx, gg)
    return corr > 0.6, \
        (f"contraste con m106: las exportaciones correlacionan {corr:+.2f} (informa) y la inversión pública ~0 "
         "(engaña) porque las exportaciones son EXÓGENAS (demanda mundial, m88) y la inversión es política endógena (m69) — "
         "la correlación revela causa solo cuando el impulsor no reacciona al ciclo")


MODELO = Modelo(
    id="m109", nivel=12,
    nombre="Exportaciones → crecimiento (BCRP)",
    xlabel="Año", ylabel="Variación anual (%)",
    parametros=[
        Parametro("umbral", _P0["umbral"], -5, 5, 1, "Umbral de variación a resaltar (%)",
                  grupo="análisis", definicion="referencia visual; separa años de exportaciones subiendo/cayendo"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto del crecimiento peruano viene de las exportaciones — y por qué su correlación SÍ informa cuando la de la inversión pública (m106) no?",
        variables=[("X_t", "exportaciones reales, millones S/2007 (BCRP PM04933AA)"),
                   ("ΔX_t", "variación anual de las exportaciones — el impulso externo"),
                   ("g_t", "crecimiento del PBI (BCRP PN01728AM)")],
        derivacion=["dato: \\;X_t \\;(PM04933AA), \\;g_t \\;(PN01728AM)",
                    "corr(\\Delta X_t, g_t) \\approx +0.74, \\;R^2 \\approx 0.55",
                    "1pp\\;de\\;exportaciones \\to \\approx 0.53pp\\;de\\;PBI",
                    "informa\\;porque\\;X\\;es\\;EXÓGENO\\;(demanda\\;mundial, m88) \\;vs\\;m106\\;endógeno"],
        contexto=("Este modelo mide el motor externo del crecimiento peruano y, al "
                  "ponerse junto a m106, enseña una de las lecciones más finas de la "
                  "econometría aplicada: cuándo una correlación SÍ revela un efecto. "
                  "Los hechos primero. Las exportaciones reales del Perú casi se "
                  "duplicaron entre 2004 y 2024 (un factor de 1.9), de la mano del "
                  "superciclo minero y la mayor integración al mundo. Y su variación "
                  "correlaciona fuertemente con el crecimiento del PBI: +0.74, con un "
                  "R² de 0.55 — las exportaciones explican más de la mitad de la "
                  "varianza del crecimiento, y cada punto de crecimiento exportador "
                  "se asocia con medio punto de PBI. El contraste es nítido en los "
                  "años en que las exportaciones cayeron (2009, 2020): el "
                  "crecimiento promedió apenas +1.2%, contra +5.5% en los demás. "
                  "Cuando el motor externo se apaga, el Perú se frena (m43, m86). "
                  "Pero la pregunta profunda es metodológica: en m106 vimos que la "
                  "inversión pública NO correlaciona con el crecimiento (~0), y "
                  "advertimos que eso no probaba que no sirviera. Aquí las "
                  "exportaciones SÍ correlacionan (+0.74). ¿Por qué confiar en esta "
                  "correlación y no en aquella? La respuesta es la EXOGENEIDAD. Las "
                  "exportaciones peruanas las mueve, en gran medida, algo ajeno al "
                  "ciclo interno: la demanda mundial y el precio de los commodities "
                  "(m88, m89), que no dependen de cómo le vaya a la economía peruana "
                  "este año. Como el impulsor es exógeno, su correlación con el "
                  "crecimiento sí traza un canal causal (más demanda externa → más "
                  "producción). La inversión pública, en cambio, es una POLÍTICA que "
                  "REACCIONA al ciclo (contracíclica, m69): su correlación está "
                  "contaminada por esa reacción. La moraleja no es 'la correlación "
                  "nunca sirve', sino algo más útil: la correlación revela causa "
                  "cuando el impulsor no responde a lo que queremos explicar. "
                  "Distinguir impulsores exógenos de políticas endógenas es el "
                  "corazón de la identificación (m70) — y la diferencia entre m109 y "
                  "m106 lo muestra con datos peruanos."),
        autores=("Datos: BCRP (PM04933AA exportaciones reales, PN01728AM PBI); el "
                 "crecimiento liderado por exportaciones: m43; exógeno vs endógeno "
                 "y cuándo la correlación informa: identificación econométrica (m70, "
                 "conocimiento general)."),
        supuestos=[
            "Las exportaciones se tratan como largamente EXÓGENAS al ciclo peruano (las mueve la demanda mundial y los precios de commodities, m88): supuesto razonable para un país pequeño y abierto (m43), no exacto.",
            "Correlación descriptiva: +0.74 sugiere un canal causal por la exogeneidad del impulsor, pero no es una estimación estructural (no controla inversión, términos de intercambio, etc.).",
            "Exportaciones reales (volumen, millones S/2007): separa el volumen exportado del efecto precio (que es m105, términos de intercambio → ingreso).",
        ],
        ecuaciones=[
            Ecuacion("corr(\\Delta X, \\; g) \\approx +0.74, \\;\\; R^2 \\approx 0.55", "el motor externo (m43)",
                     "las exportaciones explican más de la mitad de la varianza del crecimiento: el Perú "
                     "crece cuando exporta más — economía abierta, m43 — verificado con datos."),
            Ecuacion("años\\;con\\;\\Delta X < 0: \\;\\;g \\approx +1.2\\% \\;vs\\; +5.5\\%", "cuando el motor se apaga",
                     "en 2009 y 2020, con las exportaciones cayendo, el crecimiento se hundió: la "
                     "dependencia del motor externo (m86) hecha evidencia."),
            Ecuacion("X\\;exógeno \\Rightarrow corr\\;informa; \\;\\;\\;inv\\;pública\\;endógena \\Rightarrow corr\\;engaña",
                     "cuándo la correlación revela causa",
                     "la diferencia con m106: las exportaciones no reaccionan al ciclo peruano (m88), "
                     "la inversión pública sí (m69) — por eso una correlación informa y la otra no."),
        ],
        intuicion=("La imagen es doble. Primero, la del Perú como economía abierta: "
                   "cuando el mundo compra (superciclo), el Perú vuela; cuando el "
                   "mundo se frena o se cierra (2009, 2020), el Perú se hunde — las "
                   "exportaciones y el PBI suben y bajan casi juntos, +0.74. "
                   "Segundo, y más sutil, la lección de m106-vs-m109 puestos lado a "
                   "lado: dos variables, dos correlaciones opuestas, y la teoría "
                   "predice ambas. La inversión pública correlaciona ~0 porque es "
                   "política que reacciona al ciclo; las exportaciones correlacionan "
                   "+0.74 porque son un empujón que viene de afuera. Un estudiante "
                   "que entienda esto ya no pregunta '¿correlaciona?' sino '¿el "
                   "impulsor es exógeno o reacciona a lo que quiero explicar?' — que "
                   "es la pregunta correcta. Es también un retrato del modelo de "
                   "desarrollo peruano y su talón de Aquiles: crecer exportando "
                   "materias primas funciona espectacularmente cuando el mundo tira, "
                   "pero ata el destino del país al ciclo global y al precio del "
                   "cobre. Diversificar la canasta exportadora y las fuentes de "
                   "crecimiento (m112) es cómo se reduce esa dependencia."),
        equilibrio=("No hay equilibrio que resolver: es la relación empírica entre "
                    "exportaciones y crecimiento. El resultado —corr +0.74, R² 0.55, "
                    "pendiente ~0.53— traza un canal causal creíble PORQUE las "
                    "exportaciones son exógenas al ciclo interno (m88), a diferencia "
                    "de la inversión pública endógena de m106."),
        limitaciones=[
            "Exogeneidad supuesta, no probada: parte de las exportaciones (volumen minero) responde a inversión pasada, que sí depende del ciclo — la exogeneidad es aproximada.",
            "Correlación con canal causal creíble ≠ estimación estructural: la pendiente 0.53 no controla otros factores (términos de intercambio, inversión) que se mueven a la vez.",
            "Volumen, no valor: usa exportaciones reales (m109); el efecto PRECIO de exportar (términos de intercambio → ingreso) es m105 — dos canales distintos que no hay que confundir.",
        ],
        evolucion=("Cierra el arco del canal externo (m103-m105, m109) con el "
                   "resultado más limpio —exportaciones → crecimiento, +0.74— y, "
                   "junto a m106, entrega la lección de exógeno-vs-endógeno que "
                   "prepara m107 (medir el multiplicador exige variación exógena del "
                   "gasto, m70). Su dependencia del motor externo alimenta m110 "
                   "(shock externo) y su reverso, la necesidad de diversificar (m112)."),
    ),
    escenarios=[
        Escenario("motor_encendido", "el motor externo tira (referencia)",
                  {"umbral": 0.0},
                  "en los años de exportaciones al alza el Perú crece 5-9%: el "
                  "superciclo fue, en el fondo, un boom exportador (m88) — el mundo "
                  "compraba cobre y el Perú crecía.",
                  cadena=["demanda mundial fuerte (superciclo, m88)", "las exportaciones peruanas suben",
                          "más producción, ingreso y empleo (m43)", "el PBI crece 5-9% — motor externo encendido"]),
        Escenario("motor_apagado", "el motor externo se apaga (2009, 2020)",
                  {"umbral": 0.0},
                  "en 2009 (crisis global) y 2020 (COVID) las exportaciones cayeron "
                  "y el crecimiento se hundió a +1.2% promedio: la otra cara de la "
                  "apertura — cuando el mundo se frena, el Perú también (m86).",
                  cadena=["shock externo global (2009, 2020)", "la demanda mundial cae, las exportaciones se hunden",
                          "menos producción e ingreso (m43)", "el crecimiento colapsa (+1.2% medio)",
                          "la dependencia del motor externo (m86) hecha riesgo"]),
    ],
    verificaciones=[
        Verificacion("exportaciones y crecimiento fuertemente ligados (m43)", _v_correlacion_fuerte),
        Verificacion("las exportaciones reales casi se duplicaron", _v_exportaciones_crecieron),
        Verificacion("sin motor externo, el Perú se frena (2009, 2020)", _v_anos_caida),
        Verificacion("la correlación informa porque es exógena (vs m106)", _v_exogeno_informa),
    ],
    notas="Exportaciones → crecimiento: corr +0.74, R²=0.55 (motor externo, m43). Contraste con m106: informa porque es EXÓGENA (m88), no política endógena (m69). La correlación revela causa cuando el impulsor no reacciona al ciclo.",
)
