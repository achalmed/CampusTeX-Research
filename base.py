# base.py — NÚCLEO del laboratorio (capa de modelo, sin matplotlib).
#
# Separación de capas (observación de Edison, 2026-08-19):
#   base.py        → el MODELO: dataclasses, cálculo, verificación, sensibilidad
#   graficos.py    → el RENDER: dibujo matplotlib, figuras, demo de sensibilidad
#   laboratorio.py → la EXPERIENCIA: lámina de experimento, modos interactivos
#   reporte.py     → informe MD por modelo
# Así el mismo modelo alimenta CLI, láminas, reportes y (futuro) web/notebook
# sin duplicar ecuaciones.
#
# Un modelo une tres capas (diseño: docs/LABORATORIO_MACRO.md):
#   1. FICHA PEDAGÓGICA (Ficha): pregunta económica, contexto histórico,
#      autores, supuestos, variables, ecuaciones explicadas, derivación,
#      intuición, limitaciones y evolución.
#   2. MOTOR NUMÉRICO: curvas(params) -> dict graficable, y
#      resultados(params) -> dict de magnitudes de equilibrio.
#   3. CONTRATOS DE CALIDAD: escenarios (experimentos con mecanismo de
#      transmisión y lectura económica) y verificaciones (identidades exactas,
#      convergencias con tolerancia).
#
# curvas(params) devuelve un dict con claves opcionales:
#   "lineas":     {etiqueta: (x, y, color)}
#   "barras":     (categorias, valores, colores)
#   "puntos":     [(x, y, etiqueta)]
#   "equilibrio": (x, y)
#   "anotacion":  str

from dataclasses import dataclass, field


@dataclass
class Parametro:
    nombre: str
    valor: float
    minimo: float
    maximo: float
    paso: float = 0.1
    etiqueta: str = ""
    grupo: str = ""          # bloque temático ("mercado de bienes", "política fiscal", …)
    definicion: str = ""     # qué significa económicamente (para paneles/reportes)
    unidad: str = ""         # "%", "u.m.", "pp", …


@dataclass
class Ecuacion:
    latex: str          # p.ej. "C = C_0 + c \\, Y_d"
    nombre: str         # p.ej. "función de consumo"
    significado: str    # de dónde surge y qué representa cada término


@dataclass
class Ficha:
    """Ficha pedagógica estándar: el modelo como episodio de la historia del
    pensamiento macroeconómico, no solo como sistema de ecuaciones."""
    contexto: str                    # contexto histórico y problema que intentaba explicar
    autores: str                     # autores, años y escuelas de pensamiento
    supuestos: list                  # list[str] — supuestos teóricos explícitos
    ecuaciones: list                 # list[Ecuacion] — construcción paso a paso
    intuicion: str                   # la intuición económica detrás de las ecuaciones
    equilibrio: str = ""             # condición de equilibrio y estabilidad
    limitaciones: list = field(default_factory=list)   # críticas y problemas empíricos
    evolucion: str = ""              # qué modelo del currículo lo supera y por qué
    pregunta: str = ""               # la PREGUNTA ECONÓMICA que el modelo investiga
    variables: list = field(default_factory=list)      # [(símbolo, descripción endóg./exóg.)]
    derivacion: list = field(default_factory=list)     # pasos LaTeX de la derivación del equilibrio
    procedencia: str = "conocimiento macroeconómico general (manuales estándar de macro intermedia); NO verificado contra edición específica"
    referencias: list = field(default_factory=list)


@dataclass
class Escenario:
    nombre: str         # clave para la CLI (sin espacios)
    descripcion: str    # qué experimento es ("aumento del gasto público en 100")
    cambios: dict       # {parametro: nuevo_valor}
    lectura: str = ""   # interpretación económica del resultado ("¿por qué?")
    cadena: list = field(default_factory=list)  # mecanismo de transmisión paso a paso
                                                #   ["↑G", "↑DA", "IS→derecha", "↑Y", …]


@dataclass
class Verificacion:
    nombre: str
    fn: object          # fn() -> (bool, str detalle)


@dataclass
class Modelo:
    nombre: str
    parametros: list                       # list[Parametro]
    curvas: object                         # fn(dict) -> dict (ver cabecera)
    xlabel: str = "Producto ($Y$)"
    ylabel: str = "Tasa de interés ($r$)"
    notas: str = ""
    # --- capas del laboratorio (todas opcionales para compatibilidad) ---
    id: str = ""                           # posición curricular ("m03")
    nivel: int = 0                         # nivel del currículo (1..12)
    ficha: object = None                   # Ficha
    escenarios: list = field(default_factory=list)      # list[Escenario]
    resultados: object = None              # fn(dict) -> dict[str, float]
    verificaciones: list = field(default_factory=list)  # list[Verificacion]
    ecuaciones_calibradas: object = None   # fn(dict) -> list[str] — ecuaciones CON los
                                           #   valores vigentes en LaTeX ("C = 100 + 0.80(Y-100)")

    def dict_params(self):
        return {p.nombre: p.valor for p in self.parametros}

    def parametro(self, nombre):
        for p in self.parametros:
            if p.nombre == nombre:
                return p
        raise KeyError(f"parámetro '{nombre}' no existe en {self.id or self.nombre}")

    def escenario(self, nombre):
        for e in self.escenarios:
            if e.nombre == nombre:
                return e
        raise KeyError(f"escenario '{nombre}' no existe en {self.id or self.nombre} "
                       f"(disponibles: {', '.join(e.nombre for e in self.escenarios) or 'ninguno'})")

    def calcular(self, **cambios):
        """Resultados del modelo con los parámetros por defecto más `cambios`."""
        params = dict(self.dict_params(), **cambios)
        if self.resultados:
            return self.resultados(params)
        eq = self.curvas(params).get("equilibrio")
        return {"x*": eq[0], "y*": eq[1]} if eq else {}


def fmt(v):
    """Formato legible para magnitudes económicas (miles con coma, decimales cortos)."""
    if not isinstance(v, (int, float)):
        return str(v)
    if abs(v) >= 1000:
        return f"{v:,.1f}"
    if abs(v) >= 10:
        return f"{v:.1f}"
    if abs(v) >= 1:
        return f"{v:.2f}"
    return f"{v:.3f}"


def signo(delta, tolerancia=1e-9):
    """Dirección de un cambio: '↑', '↓' o '=' (para el modo experimento)."""
    if delta > tolerancia:
        return "↑"
    if delta < -tolerancia:
        return "↓"
    return "="


def comparar(modelo, nombres_escenarios):
    """Tabla de comparación de políticas: base vs cada escenario.
    Devuelve (magnitudes, {nombre_columna: dict_resultados})."""
    columnas = {"base": modelo.calcular()}
    for nombre in nombres_escenarios:
        esc = modelo.escenario(nombre)
        columnas[esc.nombre] = modelo.calcular(**esc.cambios)
    magnitudes = [k for k, v in columnas["base"].items() if isinstance(v, (int, float))]
    return magnitudes, columnas


def sensibilidad(modelo, nombre_param, magnitud=None, n=9):
    """Análisis de sensibilidad genérico: evalúa una magnitud de resultados()
    sobre una malla del parámetro (su rango declarado) y aproxima la derivada
    ∂magnitud/∂parámetro en el valor base (diferencia central con paso h=paso).

    Método: diferencias finitas centrales — (f(x+h)−f(x−h))/2h.
    Objetivo: estática comparativa numérica sin exigir derivadas analíticas
    por modelo. Fundamento: cálculo numérico elemental (conocimiento general).
    Alternativa: derivada analítica por modelo (más exacta; no generalizable).
    """
    par = modelo.parametro(nombre_param)
    res_base = modelo.calcular()
    if magnitud is None:
        magnitud = next(k for k, v in res_base.items() if isinstance(v, (int, float)))
    if magnitud not in res_base:
        raise KeyError(f"magnitud '{magnitud}' no está en resultados() "
                       f"(disponibles: {', '.join(res_base)})")
    malla, filas = [], []
    for i in range(n):
        v = par.minimo + i * (par.maximo - par.minimo) / (n - 1)
        malla.append(v)
        filas.append((v, modelo.calcular(**{nombre_param: v})[magnitud]))
    h = par.paso
    f_mas = modelo.calcular(**{nombre_param: par.valor + h})[magnitud]
    f_menos = modelo.calcular(**{nombre_param: par.valor - h})[magnitud]
    derivada = (f_mas - f_menos) / (2 * h)
    return {"magnitud": magnitud, "parametro": nombre_param, "base": par.valor,
            "filas": filas, "derivada": derivada}


def _verificar_coherencia(modelo):
    """Guardia estructural: los parámetros por defecto deben bastar para CALCULAR.
    Atrapa el bug de claves usadas en curvas/resultados pero no expuestas como
    Parametro (las verificaciones usan _P0 y no lo detectan; reportes y app sí
    fallan). Devuelve (ok, detalle)."""
    try:
        modelo.calcular()
        modelo.curvas(modelo.dict_params())
        return True, "los parámetros por defecto bastan para calcular y graficar"
    except KeyError as exc:
        return False, (f"parámetro huérfano {exc}: usado en el modelo pero no expuesto "
                       "como Parametro (dict_params no lo incluye)")
    except Exception as exc:
        return False, f"el cálculo base falla: {exc}"


def verificar(modelo):
    """Corre las verificaciones del modelo; devuelve [(nombre, ok, detalle)].
    Antepone un chequeo de coherencia estructural (parámetros completos)."""
    salida = [("coherencia (params completos)",) + _verificar_coherencia(modelo)]
    for v in modelo.verificaciones:
        try:
            ok, detalle = v.fn()
        except Exception as exc:            # una verificación que revienta = fallo
            ok, detalle = False, f"excepción: {exc}"
        salida.append((v.nombre, bool(ok), detalle))
    return salida
