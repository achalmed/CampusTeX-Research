"""simuladores/macro/modelos/nivel_12/_datos_bcrp.py — lector de datos del BCRP para el laboratorio del Perú (nivel 12).

No es un modelo.

Dos fuentes, en orden de preferencia:
  (1) DATOS MENSUALES de 02 analysis/data/raw/bcrp/<categoría>/<código>_v…json
      (los descarga el conector connectors/bcrp; el archivo original es
      SAGRADO — solo se lee, nunca se modifica). Mayor resolución. Si 02 analysis
      está, se leen con su lector único (metodos/series/lectores.py: resuelve la
      ruta por el catálogo y omite los periodos sin dato); si no, con el lector
      propio de abajo.
  (2) SNAPSHOT ANUAL embebido en _series_bcrp.py (fallback autocontenido:
      data/ está en .gitignore, así el laboratorio funciona en un clon
      limpio y sus verificaciones son reproducibles).

Todas las series son AGREGADOS macro PÚBLICOS del BCRP (no microdatos
restringidos). Procedencia declarada en cada modelo: "dato BCRP <código>,
muestra 2004-2024". Las calibraciones DERIVADAS de estos datos son para
ilustración pedagógica del laboratorio, no pronósticos oficiales.
"""

import glob
import json
from pathlib import Path

import numpy as np

from modelos.nivel_12 import _series_bcrp

# raíz de datos crudos: 02 analysis/data/raw/bcrp, localizada por NOMBRE
# (core/env.py: ANALYSIS_DIR) porque el laboratorio vive en 10 Class desde el
# 2026-09-20; si core/ no está, se usa el snapshot embebido (_series_bcrp).
# Hasta el 2026-09-28 apuntaba a data/raw/peru/bcrp/<código>/, que dejó de existir
# el 2026-09-25 (el acervo se aplanó y se agrupó por categoría): el laboratorio cayó
# en silencio al snapshot anual durante tres días sin que ninguna verificación lo dijera.
def _analysis_dir():
    import importlib.util
    for carpeta in Path(__file__).resolve().parents:
        env = carpeta / "core" / "env.py"
        if env.is_file():
            spec = importlib.util.spec_from_file_location("core_env", env)
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            return Path(mod.ANALYSIS_DIR)
    return None                   # sin ecosistema: solo snapshot
_ANALYSIS = _analysis_dir()
_RAIZ_RAW = (_ANALYSIS / "data" / "raw" / "bcrp") if _ANALYSIS else Path("/nonexistent")


def _lector_unico():
    """`metodos.series.lectores` de 02 analysis si está disponible; None si no."""
    if _ANALYSIS is None or not (_ANALYSIS / "metodos" / "series" / "lectores.py").is_file():
        return None
    import sys
    if str(_ANALYSIS) not in sys.path:
        sys.path.append(str(_ANALYSIS))
    try:
        from metodos.series import lectores
        return lectores
    except Exception:             # un 02 analysis a medias no tumba el laboratorio
        return None


def _archivos(codigo):
    """Versiones del JSON de una serie en el acervo (cualquier categoría), ordenadas."""
    return sorted(glob.glob(str(_RAIZ_RAW / "*" / f"{codigo}_v*.json")))

_MES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}


def _leer_mensual(codigo):
    """Lee la última versión del JSON crudo de una serie MENSUAL; None si no existe o no es mensual."""
    lectores = _lector_unico()
    if lectores is not None:
        try:
            s = lectores.serie_bcrp(codigo, _ANALYSIS)
        except Exception:
            s = None
        if s is not None and s.frecuencia == "mensual":
            pares = [(p, v) for p, v, e in zip(s.periodos, s.valores, s.estados) if e == "dato"]
            if pares:
                return (np.array([p.anio + (p.sub - 1) / 12 for p, _ in pares]),
                        np.array([v for _, v in pares]))
        if s is not None:
            return None           # existe pero no es mensual: el snapshot anual manda
    archivos = _archivos(codigo)
    if not archivos:
        return None
    try:
        d = json.load(open(archivos[-1], encoding="utf-8"))
    except Exception:
        return None
    t, v = [], []
    for p in d.get("periods", []):
        try:
            mes3, ano = p["name"].split(".")
            t.append(int(ano) + (_MES[mes3] - 1) / 12)
            v.append(float(p["values"][0]))
        except (ValueError, KeyError):
            continue
    return (np.array(t), np.array(v)) if v else None


def serie(nombre, anual=False):
    """Devuelve (tiempo, valores) de una serie por nombre corto ('pbi_var',
    'cobre', 'tasa_ref', …). Mensual desde data/raw si está y anual=False;
    si no, el snapshot anual embebido. `tiempo` en años decimales."""
    if not anual:
        cod = _series_bcrp.CODIGOS.get(nombre)
        m = _leer_mensual(cod) if cod else None
        if m is not None:
            return m
    d = _series_bcrp.ANUAL[nombre]
    anos = np.array(sorted(d))
    return anos.astype(float), np.array([d[a] for a in anos])


def alinear(nombre_x, nombre_y, anual=True):
    """Dos series alineadas por año (para regresiones y correlaciones)."""
    dx, dy = _series_bcrp.ANUAL[nombre_x], _series_bcrp.ANUAL[nombre_y]
    if not anual:
        # alinear mensuales por su tiempo redondeado no es trivial: usar anual
        pass
    anos = sorted(set(dx) & set(dy))
    x = np.array([dx[a] for a in anos])
    y = np.array([dy[a] for a in anos])
    return np.array(anos, float), x, y


def ols(x, y):
    """Regresión lineal simple y = a + b·x. Devuelve (a, b, R²).
    Método: mínimos cuadrados ordinarios (conocimiento general).
    Objetivo: cuantificar una relación bivariada del laboratorio.
    Fundamento: b = cov(x,y)/var(x); R² = corr² . NO es inferencia causal."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    xm, ym = x.mean(), y.mean()
    sxx = np.sum((x - xm) ** 2)
    b = np.sum((x - xm) * (y - ym)) / sxx if sxx > 0 else 0.0
    a = ym - b * xm
    yhat = a + b * x
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - ym) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return a, b, r2


def correlacion(x, y):
    """Coeficiente de correlación de Pearson (conocimiento general)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def hay_datos_mensuales():
    """True si el detalle mensual de data/raw está disponible (vs snapshot)."""
    return any(_archivos(c) for c in _series_bcrp.CODIGOS.values())
