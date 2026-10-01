"""simuladores/fuentes.py — comprobar las citas de un modelo contra la edición (MOTOR, sin matplotlib).

Objetivo: que «página verificada» sea una aserción y no una promesa. Una `base.Fuente` dice qué libro
(`calibre_id`), qué página impresa, qué hoja del PDF y qué pasaje literal; aquí se pide el texto de esa
hoja al resolutor único de la biblioteca (`core/py-common/biblioteca.py › texto`) y se comprueba:
  1. que el pasaje está en esa hoja (si no, la cita FALLA);
  2. que el folio impreso aparece en la cabecera o el pie de la hoja (si no se ve, es un AVISO: hay PDF
     sin folio en el texto, y entonces la página impresa la confirma una persona).
Método: normalización NFKC (ligaduras ﬁ → fi), guiones de corte de línea unidos, y comparación sobre
  la secuencia de letras y dígitos en minúscula (robusta a espacios y saltos de pdftotext, estricta en
  el contenido).
Fundamento: Método Documental, regla 1 (`prompts/00 metodo/METODO_DOCUMENTAL.md`): el libro se referencia
  por `calibre_id` y la ruta se pide al resolutor; nada se copia. Diagnóstico: DIAGNOSTICO_SIMULADORES_2026-10 §3 A4.
Límite: si la biblioteca no está en esta máquina, la cita queda «no comprobable», no verificada.
"""

import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

VERIFICADA, AVISO, FALLA, NO_COMPROBABLE = "verificada", "aviso", "falla", "no comprobable"
MAX_PALABRAS_PASAJE = 15


@lru_cache(maxsize=1)
def _biblioteca():
    """El módulo `biblioteca` de core/py-common, localizado subiendo desde aquí; None si no está."""
    for carpeta in Path(__file__).resolve().parents:
        candidato = carpeta / "core" / "py-common" / "biblioteca.py"
        if candidato.is_file():
            sys.path.insert(0, str(candidato.parent))
            try:
                import biblioteca
                return biblioteca
            except Exception:
                return None
    return None


def _clave(texto):
    """Secuencia comparable: NFKC, guion de corte unido, solo letras y dígitos en minúscula."""
    t = unicodedata.normalize("NFKC", texto or "")
    t = re.sub(r"[-‐­]\s*\n\s*", "", t)
    return "".join(c for c in t.lower() if c.isalnum())


@lru_cache(maxsize=None)
def _hojas(calibre_id):
    bib = _biblioteca()
    return tuple(bib.texto(calibre_id)) if bib else None


def _folio_visible(hoja, pagina):
    """¿El primer número de la página impresa aparece como número suelto en cabecera o pie?"""
    numero = re.match(r"\s*([0-9ivxlcdm]+)", str(pagina), re.I)
    if not numero:
        return False
    lineas = [l for l in hoja.splitlines() if l.strip()]
    bordes = lineas[:3] + lineas[-3:]
    patron = re.compile(rf"(?<![\w.]){re.escape(numero.group(1))}(?![\w.])", re.I)
    return any(patron.search(l) for l in bordes)


def comprobar(fuente):
    """(estado, detalle) de una base.Fuente."""
    palabras = len((fuente.pasaje or "").split())
    if not palabras:
        return FALLA, "la cita no trae pasaje"
    if palabras > MAX_PALABRAS_PASAJE:
        return FALLA, f"pasaje de {palabras} palabras (máximo {MAX_PALABRAS_PASAJE}: se cita, no se copia)"
    hojas = _hojas(fuente.calibre_id)
    if hojas is None:
        return NO_COMPROBABLE, "la biblioteca no está en esta máquina"
    if not hojas:
        return FALLA, f"calibre {fuente.calibre_id}: sin archivo o sin texto"
    if not 1 <= fuente.pagina_pdf <= len(hojas):
        return FALLA, f"hoja {fuente.pagina_pdf} fuera del PDF ({len(hojas)} hojas)"
    hoja = hojas[fuente.pagina_pdf - 1]
    if _clave(fuente.pasaje) not in _clave(hoja):
        cerca = [n for n in (fuente.pagina_pdf - 1, fuente.pagina_pdf + 1)
                 if 1 <= n <= len(hojas) and _clave(fuente.pasaje) in _clave(hojas[n - 1])]
        pista = f" (está en la hoja {cerca[0]})" if cerca else ""
        return FALLA, f"el pasaje no está en la hoja {fuente.pagina_pdf} del PDF{pista}"
    if not _folio_visible(hoja, fuente.pagina):
        return AVISO, f"pasaje en la hoja {fuente.pagina_pdf}; el folio impreso «{fuente.pagina}» no se ve en el texto"
    return VERIFICADA, f"pasaje en la hoja {fuente.pagina_pdf}, folio impreso {fuente.pagina}"


def referencia(calibre_id):
    """Referencia APA 7 completa del libro: la pide al resolutor (la ficha de Calibre manda)."""
    bib = _biblioteca()
    return bib.apa(calibre_id) if bib else f"Calibre {calibre_id}"


def cita(fuente):
    """Cita en el texto, APA 7: «Wasserman (2003, p. 232)»; «Larsen y Marx (2011, pp. 3-5)»;
    tres autores o más, «Newbold et al. (2008, p. 9)». Apellidos por la partición única del resolutor."""
    bib = _biblioteca()
    prefijo = "pp." if "-" in str(fuente.pagina) else "p."
    d = bib.datos(fuente.calibre_id) if bib else None
    if not d:
        return f"Calibre {fuente.calibre_id} ({prefijo} {fuente.pagina})"
    apellidos = []
    for a in d["autores"]:
        partes = bib.partir_autor(a)
        apellidos.append(partes[0] if partes else a)
    if len(apellidos) >= 3:
        quien = f"{apellidos[0]} et al."
    else:
        quien = " y ".join(apellidos) or "Anónimo"
    anio = (d.get("pubdate") or "")[:4]
    anio = anio if anio.isdigit() and anio > "0101" else "s.f."
    return f"{quien} ({anio}, {prefijo} {fuente.pagina})"


def auditar(modelos):
    """[(modelo, fuente|None, estado, detalle)] de todas las citas; None = el modelo no cita nada."""
    filas = []
    for m in modelos:
        fuentes = getattr(m.ficha, "fuentes", None) or []
        if not fuentes:
            filas.append((m, None, FALLA, "sin fuentes verificables (Ficha.fuentes vacía)"))
        for f in fuentes:
            filas.append((m, f) + comprobar(f))
    return filas


def resumen(filas):
    """Modelos con todas sus citas verificadas (o con aviso) y modelos con alguna falla."""
    por_modelo = {}
    for m, _f, estado, _d in filas:
        por_modelo.setdefault(m.id or m.nombre, set()).add(estado)
    buenos = sorted(k for k, e in por_modelo.items() if e <= {VERIFICADA, AVISO})
    malos = sorted(k for k, e in por_modelo.items() if e & {FALLA, NO_COMPROBABLE})
    return buenos, malos
