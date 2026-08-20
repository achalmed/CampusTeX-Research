# _datos_bcrp.py — lector de datos del BCRP para el laboratorio del Perú
# (nivel 12). No es un modelo.
#
# Dos fuentes, en orden de preferencia:
#   (1) DATOS MENSUALES de data/raw/peru/bcrp/<código>/ (los descarga el
#       conector connectors/bcrp; el archivo original es SAGRADO — solo se
#       lee, nunca se modifica). Mayor resolución.
#   (2) SNAPSHOT ANUAL embebido en _series_bcrp.py (fallback autocontenido:
#       data/ está en .gitignore, así el laboratorio funciona en un clon
#       limpio y sus verificaciones son reproducibles).
#
# Todas las series son AGREGADOS macro PÚBLICOS del BCRP (no microdatos
# restringidos). Procedencia declarada en cada modelo: "dato BCRP <código>,
# muestra 2004-2024". Las calibraciones DERIVADAS de estos datos son para
# ilustración pedagógica del laboratorio, no pronósticos oficiales.

import glob
import json
from pathlib import Path

import numpy as np

from modelos.nivel_12 import _series_bcrp

# raíz de datos crudos (…/datafw/data/raw/peru/bcrp)
_RAIZ_RAW = Path(__file__).resolve().parents[3] / "data" / "raw" / "peru" / "bcrp"

_MES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}


def _leer_mensual(codigo):
    """Lee la última versión del JSON crudo de una serie; None si no existe."""
    archivos = sorted(glob.glob(str(_RAIZ_RAW / codigo / "*.json")))
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
    return any((_RAIZ_RAW / c).exists() for c in _series_bcrp.CODIGOS.values())
