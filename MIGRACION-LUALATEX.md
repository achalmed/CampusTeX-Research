# Migración XeLaTeX → LuaLaTeX — Academic Class Framework

**Fecha:** 2026-07-23 · **Motor único soportado a partir de ahora:** LuaLaTeX.

Registro de **cada cambio**, su **motivo** y su **beneficio**. La migración preserva
la apariencia (mismo nº de páginas) y **cumple el diseño ya declarado** en
`docs/00-arquitectura.md`, que prometía «protrusion + expansion» — expansión que
XeLaTeX ignoraba y LuaLaTeX ahora sí aplica.

---

## 1. Resultado de verificación

Compilado con **LuaHBTeX 1.22.0 (TeX Live 2025)** vía `scripts/build.sh`:

| Documento | Baseline (protrusion) | LuaLaTeX (protrusion + **expansion**) | Resultado |
|---|---|---|---|
| `templates/exam/examen-problemas` | 3 pág | 3 pág | ✅ mismas páginas |
| `templates/presentation/clase` (Beamer) | 6 pág | 6 pág | ✅ mismas páginas |
| `templates/report/silabo` | — | 2 pág | ✅ compila |
| `scaffolds/session/02_Clase/slides.tex` (migrado) | — | 6 pág | ✅ compila |

Detalle del `.log`: `Automatic font expansion enabled (level 2)`, motor LuaHBTeX,
**sin drivers XeTeX**, 0 errores. Los mensajes `LaTeX Info: Redefining \frac…` son
el comportamiento normal de `unicode-math`/`mathtools` (idéntico bajo XeLaTeX).

> **Nota clave:** activar la expansión **no cambió la paginación** de examen ni
> diapositiva. Se entregó la mejora tipográfica sin alterar la maquetación.

---

## 2. Tipografía — `styles/academic-fonts.sty`

- **Cambio funcional:** microtype pasa de `[protrusion=true,final]` a
  **`[protrusion=true,expansion=true,final]`**.
- **Motivo:** la expansión (algoritmo *hz*) solo es efectiva bajo LuaLaTeX/pdfTeX;
  XeLaTeX la ignoraba. El diseño (`docs/00-arquitectura.md`) ya la prometía. Los
  documentos del *Class* framework (diapositivas, exámenes) se **regeneran**, no son
  archivo con paginación contractual.
- **Beneficio:** mejor «gris» tipográfico y justificación (menos ríos), sin cambio de
  paginación verificado. No toca la matemática (`unicode-math`) ni el monoespaciado.
- Se corrigieron los comentarios factualmente falsos («la expansion es solo pdf/lua,
  XeLaTeX la ignora / SOLO XeLaTeX») y la cabecera del paquete (v2, LuaLaTeX).
- **Sin cambio (verificado):** `libertinus` (wrapper) se mantiene — bajo LuaLaTeX
  despacha a `libertinus-otf` (`\iftutex`) y fija `\setmathfont{LibertinusMath}`;
  cambiarlo a `libertinus-otf` sería cosmético y sin beneficio. `\setmonofont`
  Inconsolata por archivo OTF sigue resolviéndose vía kpathsea.

---

## 3. Sistema de build

| Archivo | Cambio | Motivo / beneficio |
|---|---|---|
| `scripts/build.sh` | `xelatex` (hardcodeado ×3) → variable **`ENGINE=lualatex`** (`require_cmd` + dos pasadas); cabeceras | Motor parametrizado en un punto; futuros cambios triviales. |
| `scripts/lib/common.sh` | `latex_engine()` simplificada: honra `%!TEX program` y por defecto **`lualatex`**; se retiran las heurísticas `yaac-*` y `fontspec → xelatex` | La regla `fontspec→xelatex` era el requisito a corregir, y además **fallaba**: un `\documentclass{academic-beamer}` (sin la cadena «fontspec» en el `.tex`) caía por error a `pdflatex`. Ahora es correcto. |
| `scripts/doctor.sh` | Promueve **lualatex** como motor del framework (fontspec + microtype); xelatex/pdflatex quedan como «alternativos, no soportados» | Diagnóstico coherente con el motor único. |
| `config/course.yml` | Comentario del compilador → lualatex directo | Coherencia. |

Sintaxis verificada con `bash -n` en los tres scripts.

---

## 4. Scaffold `scaffolds/session/02_Clase/slides.tex`

Deck Beamer **standalone** (identidad institucional propia, no `academic-beamer`)
que estaba en **pdfLaTeX**:

- `%!TEX program = pdflatex` → **`lualatex`**.
- Se **elimina** `\usepackage[utf8]{inputenc}` (UTF-8 es nativo en LuaLaTeX).
- Se **conserva** `\usepackage[T1]{fontenc}` + `babel[spanish]` (válidos bajo
  LuaLaTeX; preservan las fuentes Latin Modern y la partición del español).
- **Motivo:** migrar el motor sin rediseñar (usa tema `whale` + colores azules,
  ajenos a la identidad «Academic»). Reescribirlo a `academic-beamer` cambiaría la
  apariencia de sesiones existentes.
- **Beneficio:** compila con `lualatex` (verificado, 6 pág) sin `inputenc`, coherente
  con el motor único.

---

## 5. Comentarios de código y documentación

- Cabeceras de clases (`academic-base/exam/report/beamer.cls`), estilos
  (`academic.sty`), tema Beamer y las 12 plantillas (`templates/*/*.tex`):
  «(XeLaTeX)» / «Motor: XeLaTeX exclusivamente» → **LuaLaTeX**.
- `academic-exam.cls`: la nota histórica «Migración XeLaTeX de la antigua
  evaluacion.cls» pasa a reflejar el linaje completo (pdfLaTeX → XeLaTeX → LuaLaTeX).
- `README.md`, `CLAUDE.md`, `docs/00-arquitectura.md` (fuente de verdad),
  `docs/architecture.md`, `docs/developer-guide.md`, `docs/automation.md`: motor
  único LuaLaTeX; se reconcilió la descripción **multi-motor pre-rediseño** que
  contradecía a `00-arquitectura.md`; se documentó que la expansión ya es efectiva.

---

## 6. Decisiones de diseño

- **polyglossia se conserva** (no babel): funciona en LuaLaTeX; `csquotes` +
  `\setdefaultlanguage{spanish}` intactos.
- **`unicode-math` se conserva** (vía `libertinus`): es el sistema matemático vigente
  y correcto del *Class* framework. El orden `amsmath` **antes** de `academic-fonts`
  (que carga `libertinus`→`unicode-math`) es crítico y se mantiene. `academic-exam`
  ya evita `\square`/`\boxtimes` de `amssymb` (usa `fontawesome`) precisamente por la
  convivencia con `unicode-math`.
- **Diferencia con `Academic_Writing_Framework`:** allí la matemática es *tradicional*
  (`lmodern`, sin `unicode-math`); aquí es *OpenType* (`unicode-math`). Son **dos
  regímenes matemáticos separados**: no mezclar reglas.

---

## 7. Reproducir la verificación

```bash
scripts/build.sh templates/exam/examen-problemas/examen-problemas.tex
scripts/build.sh templates/presentation/clase/clase.tex
scripts/doctor.sh   # lualatex como motor del framework

# Comparar con el baseline (protrusion-only) forzando el motor:
ENGINE=xelatex scripts/build.sh <ruta>.tex   # baseline
scripts/build.sh <ruta>.tex                  # LuaLaTeX + expansion
# pdfinfo <pdf> | grep Pages   → mismas páginas
```
