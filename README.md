# simuladores — Laboratorio de Macroeconomía Computacional

Cada teoría macroeconómica como **modelo ejecutable**: ficha pedagógica
(contexto histórico → autores → supuestos → ecuaciones explicadas → intuición →
limitaciones → evolución), simulación de escenarios con lectura económica y
verificación numérica de sus teoremas. Diseño y currículo completo (115
modelos, 12 niveles): [docs/LABORATORIO_MACRO.md](../docs/LABORATORIO_MACRO.md).

**Estado**: niveles 1-4 completos (m01-m25) — 25 modelos, 92 verificaciones
numéricas. Incluye modelos dinámicos (m14, m16, m25), estocástico con semilla
reproducible (m17), régimen endógeno (m12) y el aparato AD-AS con la demanda
derivada del IS-LM (m20-m25). Figuras con tipografía académica (serif +
matemática STIX): ejes, leyendas y anotaciones en notación LaTeX.

Dependencias: `numpy` + `matplotlib` (las de `pipeline/requirements.txt`).

## Uso

```bash
python3 main.py listar                        # qué hay implementado, por nivel
python3 main.py ficha m05                     # la ficha pedagógica en terminal
python3 main.py experimento m10               # hipótesis → ejecutar → ✔/✘ → mecanismo
python3 main.py simular m10 --escenario expansion_fiscal
python3 main.py comparar m10 expansion_fiscal politica_mixta   # políticas lado a lado
python3 main.py sensibilidad m10 --param G --grafico           # ∂Y*/∂G + malla
python3 main.py reporte --todos               # informes MD + láminas → salidas/
python3 main.py verificar                     # validación numérica (debe dar 100%)
python3 main.py demo m10 --param G --valores 100,200,300   # PDF de sensibilidad
python3 main.py laboratorio m10               # ventana con selector de experimentos
python3 main.py interactivo m10               # modo avanzado: sliders libres
```

Un modelo se nombra por id curricular (`m10`), slug (`islm`) o archivo
(`m10_islm`). `salidas/` es regenerable y no se versiona.

## Añadir un modelo (checklist)

1. Crear `modelos/nivel_NN/mNN_slug.py` (patrón completo:
   `modelos/nivel_01/m03_funcion_consumo.py`). Cabecera con ecuaciones y
   **procedencia**.
2. Definir `MODELO = Modelo(...)` con: `id`, `nivel`, `ficha` (todos los campos),
   `curvas`, `resultados`, `escenarios` (cada uno con `lectura`) y
   `verificaciones`.
3. Las verificaciones codifican los **teoremas del modelo**: identidades
   contables exactas (`< 1e-9`), convergencias con tolerancia, estática
   comparativa con el signo correcto.
4. `python3 main.py verificar mNN` al 100% y `reporte mNN` legible.
5. Registrar la fila en `docs/biblio/matriz_trazabilidad.csv` y marcar ✔ en el
   currículo de `docs/LABORATORIO_MACRO.md`.

## Reglas (resumen; completas en el diseño §5)

- Procedencia declarada siempre; sin citas de capítulo/página no verificadas.
- Calibraciones didácticas ≠ datos oficiales (los datos reales entran por los
  conectores de datafw, capa `clean`, solo en el nivel 12).
- Español en etiquetas, fichas y mensajes.
