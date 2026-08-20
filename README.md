# simuladores — Laboratorio de Macroeconomía Computacional

Cada teoría macroeconómica como **modelo ejecutable**: ficha pedagógica
(contexto histórico → autores → supuestos → ecuaciones explicadas → intuición →
limitaciones → evolución), simulación de escenarios con lectura económica y
verificación numérica de sus teoremas. Diseño y currículo completo (115
modelos, 12 niveles): [docs/LABORATORIO_MACRO.md](../docs/LABORATORIO_MACRO.md).

**Estado**: niveles 1-11 completos (m01-m96) + nivel 12 en curso (m97-m104) —
104 modelos, 514 verificaciones numéricas (410 de contenido + un guardia de
coherencia por modelo). El nivel
11 son 16 EPISODIOS que combinan los mecanismos de todo el currículo sobre el
motor compartido `_episodio.py`: COVID (el doble shock que explica 2020 y 2021
con el mismo modelo), shocks de oferta (petróleo, alimentos), la dimensión
externa (devaluación, FED, salida de capitales, caída del cobre) y los grandes
episodios de política (estanflación de los 70, deflación de Fisher, trampa de
liquidez de Japón, crisis soberana de Grecia/Argentina). Con el nivel 10 había
terminado el currículo TEÓRICO troncal (los mecanismos previos se rompen:
corridas de Diamond-Dybvig m73, ataque cambiario que anticipa m74, zona de
crisis de deuda m76, acelerador κ=λ²·impacto m79, contagio en red m80). El
**nivel 12 es el laboratorio del Perú con datos reales del BCRP**: m97-m104
descargan series macro (PBI, IPC, tasa de referencia, tipo de cambio, cobre;
2004-2024) vía `connectors/bcrp`, destilan un snapshot anual embebido
(`_series_bcrp.py`, para ser auto-contenidos) y **verifican contra el dato
real** en vez de una calibración didáctica — con honestidad econométrica
explícita (el coeficiente Taylor 0.55<1 como sesgo de variable omitida en m100;
la correlación tasa-inflación como causalidad inversa en m101; el canal del
cobre sobre el crecimiento en m103, corr Δcobre-g=+0.45; y sobre el tipo de
cambio en m104, donde los niveles engañan y el canal se rompe en 2021 —
cobre récord con sol débil, la fuga de capitales m111 venció al comercio).
Incluye modelos dinámicos (m14, m16, m25, m27-m33), estocástico con
semilla reproducible (m17), regímenes endógenos (m12, m31 con histéresis y big
push), el aparato AD-AS con la demanda derivada del IS-LM (m20-m25) y el bloque
completo de crecimiento (Solow → regla de oro → progreso técnico → convergencia
→ trampa de pobreza → AK → capital humano). Figuras con tipografía académica
(serif + matemática STIX); cada experimento con mecanismo de transmisión.

Dependencias: `numpy` + `matplotlib` (las de `pipeline/requirements.txt`).

## Uso

```bash
python3 main.py        # ← abre el Laboratorio Interactivo (LA aplicación)
```

Dentro de la app: eliges un modelo del currículo y lo recorres paso a paso
(pregunta → contexto → supuestos → cada ecuación → construcción del gráfico
curva a curva → equilibrio → experimentos con mecanismo → **experimentación
libre en vivo** → comparación de políticas → limitaciones → siguiente modelo).
Teclado: ↑/↓/Enter en el menú; ←/→ para avanzar; M vuelve al menú.

<details><summary>Herramientas técnicas por terminal (automatización/CI)</summary>

```bash
python3 main.py verificar                     # control de calidad (debe dar 100%)
python3 main.py reporte --todos               # regenera informes MD + láminas
python3 main.py ficha m05 · simular m10 --escenario expansion_fiscal ·
        experimento m10 · comparar m10 esc1 esc2 · sensibilidad m10 --param G ·
        demo m10 --param G --valores 100,200,300 · laboratorio m10 · interactivo m10
```
</details>

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
