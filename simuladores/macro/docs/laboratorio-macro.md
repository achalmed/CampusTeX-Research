---
tipo: doc
titulo: "Laboratorio de Macroeconomía Computacional (`simuladores/`)"
estado: activo
---
# Laboratorio de Macroeconomía Computacional (`simuladores/`)

Diseño del laboratorio histórico-matemático de macroeconomía: cada teoría
macroeconómica reconstruida como **modelo ejecutable** — ecuaciones, parámetros,
simulación de shocks, gráficos e interpretación — siguiendo la evolución
cronológica de la disciplina, desde el flujo circular hasta un modelo aplicado
del Perú con datos reales de datafw.

**Visión (directiva de Edison, 2026-08-19):** no una colección de gráficos, sino
un laboratorio donde cada modelo explica *por qué se construyó, cómo funciona,
qué explica, qué no puede explicar y por qué fue reemplazado o ampliado por
otro*. El recorrido: teoría → matemática → simulación → evidencia empírica.

---

## 1. Principio rector aplicado

El principio del framework (fundamento metodológico → diseño → implementación →
validación → automatización) se aplica **a cada modelo**:

1. **Fundamento**: la ficha pedagógica (contexto histórico, autores, supuestos,
   construcción de cada ecuación, intuición, limitaciones, evolución).
2. **Diseño**: forma funcional, parámetros con rangos, escenarios de shock con
   lectura económica esperada.
3. **Implementación**: motor numérico (`curvas`, `resultados`) sobre la base
   común (`base.py`) — nunca copiar la base.
4. **Validación**: verificaciones numéricas por modelo. Las **identidades
   contables se exigen exactas** (p.ej. ΔS*=0 en la paradoja del ahorro,
   S+T+M=I+G+X en el flujo circular); las **convergencias, con tolerancia**
   (p.ej. suma de rondas del multiplicador). `python3 main.py verificar` debe
   pasar antes de dar un modelo por bueno.
5. **Automatización**: reporte MD + figuras regenerables (`reporte --todos`),
   demo de sensibilidad en PDF, modo interactivo con sliders.

## 2. La plantilla académica de 20 puntos (observación de Edison, 2026-08-19)

Todo modelo del laboratorio apunta a cubrir esta plantilla; los campos viven en
las dataclasses de `base.py` y alimentan CLI, láminas y reportes sin duplicarse:

| # | punto | dónde vive |
|---|---|---|
| 01 | contexto histórico | `Ficha.contexto` |
| 02 | **pregunta económica** (qué investiga el modelo) | `Ficha.pregunta` |
| 03 | autores / escuela | `Ficha.autores` |
| 04 | supuestos | `Ficha.supuestos` |
| 05 | variables (endógenas/exógenas) | `Ficha.variables` |
| 06 | parámetros (símbolo + definición + unidad + rango + **grupo temático**) | `Parametro` |
| 07 | ecuaciones explicadas | `Ficha.ecuaciones` |
| 08 | derivación matemática paso a paso | `Ficha.derivacion` |
| 09 | equilibrio y estabilidad | `Ficha.equilibrio` |
| 10 | intuición económica | `Ficha.intuicion` |
| 11 | simulación base | `resultados()` |
| 12-13 | experimento / shock | `Escenario` (cambios) |
| 14 | resultados (antes/después/Δ) | `calcular()` + lámina |
| 15 | **mecanismo de transmisión** (cadena causal) | `Escenario.cadena` |
| 16 | análisis de sensibilidad (∂magnitud/∂parámetro) | `base.sensibilidad` (genérico) |
| 17 | comparación de escenarios/políticas | `base.comparar` (genérico) |
| 18 | diagnóstico (teoremas como aserciones) | `verificaciones` |
| 19 | limitaciones | `Ficha.limitaciones` |
| 20 | conexión con el siguiente modelo | `Ficha.evolucion` |

Extra: `Modelo.ecuaciones_calibradas(params)` — las ecuaciones CON los valores
vigentes en LaTeX (el "la ecuación se actualiza en tiempo real" de la
observación). Los puntos 16-17 son **genéricos**: los provee el núcleo sin
trabajo por modelo. Estado de cobertura (2026-08-19): 01-04, 07, 09-14 y
18-20 en los 25 modelos; **15 (mecanismo) en los 81/81 escenarios**; 05-08 y
calibradas en las ANCLAS de cada nivel (m03, m04, m10, m12, m14, m23; grupos
de parámetros en m10 y m23). Extender 05-08/calibradas/grupos al resto de
modelos es mejora incremental — se hace al tocar cada modelo, no bloquea el
avance del currículo.

## 3. Arquitectura técnica

Separación en capas (el modelo económico NUNCA se mezcla con la interfaz —
así m10 puede alimentar CLI, láminas, reportes y mañana web/notebook sin
duplicar ecuaciones):

```
simuladores/            EL laboratorio (paraguas multi-disciplina)
├── base.py             ┐ MOTOR compartido en la raíz (agnóstico a la disciplina):
├── graficos.py         │ NÚCLEO sin matplotlib (base) + RENDER con colocación
├── laboratorio.py      │ automática de etiquetas y dibujo progresivo (graficos) +
├── reporte.py          ┘ láminas (laboratorio) + informe MD (reporte)
└── macro/              LA DISCIPLINA macro (reusa el motor de la raíz):
    ├── main.py         punto de entrada: SIN argumentos abre la app; subcomandos = herramientas
    ├── app.py          LA APLICACIÓN: menú del currículo + recorrido pedagógico progresivo
    ├── config.py       rutas, paleta, tipografía, fallback Qt (todo lo ajustable)
    ├── modelos/
    │   ├── nivel_01/   m01…m05  (un archivo = un modelo; patrón: m03_funcion_consumo.py)
    │   ├── nivel_02/   m06…m12  (código común del nivel: `_*.py`, p.ej. nivel_04/_adas.py)
    │   └── …           (nivel_NN según el currículo §6)
    └── salidas/        reportes, láminas y capturas generados (regenerable; NO se versiona)
# hermanas de macro/ (mismo motor): estadistica/ (en curso), econometria/ micro/ mate/ (futuras)
```

**La lámina de experimento** (una por escenario, incrustada en el reporte):
zona A contexto (modelo · nivel · pregunta · experimento con el cambio de
parámetro), zona B gráfico con transición E1→E2 (flecha), zona C tabla de
resultados con Δ direccionales (↑/↓/=), zona D mecanismo de transmisión
(cadena causal), zona E ecuaciones vigentes (calibradas con los valores del
experimento), pie "¿Por qué?" (lectura económica).

**El modo experimento** (CLI): pregunta → hipótesis del usuario (↑/↓/= sobre
las magnitudes clave) → ejecutar → calificación ✔/✘ contra el resultado real →
mecanismo → ¿por qué? — el ciclo pedagógico completo de la observación.

- Un modelo se invoca por id curricular (`m10`), slug (`islm`) o archivo
  (`m10_islm`).
- Dependencias: numpy + matplotlib (zona científica, como `pipeline/`;
  `connectors/` sigue siendo stdlib puro).
- **Tipografía académica** (pedida por Edison, 2026-08-19): identidad visual de
  artículo científico — texto serif + matemática STIX vía *mathtext* de
  matplotlib. Ejes, leyendas y anotaciones usan notación `$...$` (p. ej.
  `$\pi = \pi^e - \alpha(u-u_n)$` se compone como matemática real en la
  figura); no requiere instalación LaTeX y funciona headless. Para usar el
  LaTeX del sistema: `USAR_TEX_COMPLETO = True` en `config.py`. En los
  reportes MD las ecuaciones van en bloques `$$...$$` (MathJax en Obsidian).
- La simulación dinámica interactiva ya existe (sliders matplotlib); la
  interactividad web (Quarto + OJS para el ecosistema de blogs) es una
  decisión diferida (§8).

## 4. Punto de entrada único (pedido de Edison, 2026-08-19)

```bash
python3 main.py          # ← LA aplicación: todo el laboratorio en una ventana
```

La app (`app.py`) integra todo: menú del currículo → **recorrido progresivo**
por modelo (pregunta → contexto → supuestos/variables → construcción de cada
ecuación → derivación → construcción del gráfico CURVA A CURVA → equilibrio →
experimentos con E1→E2/mecanismo/¿por qué? → **experimentación libre** con
actualización en vivo de ecuaciones-curvas-equilibrio-resultados →
comparación de políticas → limitaciones → siguiente modelo). Navegación
mínima: tres botones y el teclado (↑/↓/Enter en el menú; ←/→ en el recorrido;
M vuelve al menú). Botón «Guardar lámina» exporta el experimento actual.

Los subcomandos de terminal **siguen existiendo como herramientas técnicas**
(automatización, CI y desarrollo — no son la experiencia de usuario):
`verificar` (control de calidad, exige 100%), `reporte --todos` (regenera MD +
láminas), y `listar/ficha/simular/experimento/comparar/sensibilidad/demo/
laboratorio/interactivo` como equivalentes por consola de lo que la app hace
por dentro.

## 5. Reglas duras del laboratorio

1. **Procedencia declarada siempre** (regla 00 del framework). Los modelos de
   manual son `conocimiento macroeconómico general`; **prohibido citar capítulo
   o página sin verificar el libro** (la biblioteca tiene textos macro aún no
   verificados — `docs/biblio/inventario_biblioteca.csv`). Las menciones
   históricas (Keynes 1936, Hicks 1937, Solow 1956) se marcan como *mención,
   no verificado contra edición*.
2. **Calibraciones didácticas ≠ datos oficiales.** Si un parámetro evoca una
   economía real (proporciones del PIB peruano en m02), declararlo como
   *decisión de diseño didáctica*. Los datos reales solo entran vía datafw
   (capas raw → audited → clean), nunca tecleados a mano.
3. **Verificar antes de dar por bueno**: todo modelo nuevo trae verificaciones
   y `main.py verificar` pasa al 100% antes de registrarlo.
4. **Etiquetas y docs en español**; claves y nombres de archivo en el esquema
   `mNN_slug.py`.
5. **Cada modelo se registra en la matriz de trazabilidad**
   (`docs/biblio/matriz_trazabilidad.csv`) al implementarse.
6. **`salidas/` es regenerable y no se versiona** (mismo estatus que
   `data/`): la fuente es el código, no el reporte.

## 6. Currículo (12 niveles, 115 modelos)

Estado: ✔ implementado · — pendiente. La numeración es la posición curricular
estable (id del modelo).

### Nivel 1 — Fundamentos macroeconómicos ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m01 ✔ | Flujo circular de la renta | filtraciones = inyecciones; Y* del circuito |
| m02 ✔ | PIB y componentes de la demanda agregada | identidad Y=C+I+G+XN; identidad ≠ comportamiento |
| m03 ✔ | Función de consumo keynesiana | C=C0+cYd; PMC/PMS; nivelación; crítica de Kuznets |
| m04 ✔ | Multiplicador keynesiano | rondas de gasto; k=1/(1−c(1−t)); convergencia |
| m05 ✔ | Paradoja del ahorro | cruz keynesiana; ΔS*=0; falacia de composición |

### Nivel 2 — Mercado de bienes y modelo IS-LM ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m06 ✔ | Mercado de bienes | Y=C(Y−T)+I(r)+G; la inversión deja de ser exógena; dY/dr=−b/(1−c1) |
| m07 ✔ | Curva IS | lugar geométrico (Y,r); desplazamientos k·dG, −c1·k·dT |
| m08 ✔ | Mercado monetario | M/P=L(Y,r); preferencia por la liquidez; r*=(kY−M/P)/h |
| m09 ✔ | Curva LM | lugar geométrico del dinero; pendiente k/h; desplazamiento dMP/k |
| m10 ✔ | Modelo IS-LM completo | equilibrio simultáneo; políticas fiscal y monetaria; mezcla |
| m11 ✔ | Efecto expulsión (crowding out) | ΔY=k(ΔG+ΔI); límites h→∞/h→0 = mundos keynesiano/clásico |
| m12 ✔ | Trampa de liquidez | LM con piso r=0; dinero impotente, fiscal a multiplicador pleno |

### Nivel 3 — Inflación, desempleo y ciclo económico ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m13 ✔ | Curva de Phillips | π = πᵉ − α(u−uₙ); el "menú" de los 60 y su colapso |
| m14 ✔ | Phillips aumentada por expectativas | Friedman-Phelps; aceleracionista; LP vertical (dinámico) |
| m15 ✔ | Ley de Okun | Δu = −β(g − g*); advertencia por informalidad peruana |
| m16 ✔ | Brecha del producto | (Y−Y*)/Y*; semivida; PIB-años perdidos |
| m17 ✔ | Ciclo económico | AR(1) impulso-propagación (Slutsky-Frisch); estocástico con semilla |
| m18 ✔ | Shock de demanda agregada | AD-SRAS mínimo; firma: ΔY y ΔP mismo signo; Okun para empleo |
| m19 ✔ | Shock de oferta | estanflación; dilema acomodar/resistir cuantificado |

### Nivel 4 — Modelo AD-AS ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m20 ✔ | Demanda agregada (AD) | DERIVADA del IS-LM (cada punto ≡ m10, verificado); efecto Keynes |
| m21 ✔ | Oferta agregada de corto plazo (SRAS) | P=Pe+λ(Y−Y*); Pe posiciona la curva; microfundamentos citados |
| m22 ✔ | Oferta agregada de largo plazo (LRAS) | Y*=A·K^α·L^(1−α); neutralidad del dinero EXACTA (P escala con M) |
| m23 ✔ | Modelo AD-AS completo | AD∩SRAS (cuadrática exacta, `_adas.py`); entrega (Y, P, r) a la vez |
| m24 ✔ | Estanflación | los 70 con tablero completo (π, Δu, r); Burns vs Volcker como escenarios |
| m25 ✔ | Ajuste hacia el largo plazo | dinámico: Pe(t+1)=P(t); trayectoria a la LRAS; ΔY_LP=0 exacto |

### Nivel 5 — Crecimiento económico ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m26 ✔ | Modelo de Solow | diagrama de dos curvas; estabilidad GLOBAL; ahorro compra nivel, no crecimiento; invierte la paradoja de m05 |
| m27 ✔ | Estado estacionario y transición | λ=(1−α)(n+δ); semivida simulada = ln2/λ; el largo plazo en décadas |
| m28 ✔ | Regla de oro (Phelps) | argmax c*(s)=α; sobreahorro dominado en toda la senda (ineficiencia dinámica) |
| m29 ✔ | Solow con progreso tecnológico | BGP con y creciendo exactamente a g; solo g mueve el crecimiento |
| m30 ✔ | Convergencia | β-convergencia; absoluta entre gemelos, condicional con estructuras distintas |
| m31 ✔ | Trampa de pobreza | A(k) con umbral; dos EE estables; ayuda tímida se diluye; big push e histéresis |
| m32 ✔ | Crecimiento endógeno (AK) | γ=sA−(n+δ) constante; ahorro compra crecimiento; cero convergencia |
| m33 ✔ | Capital humano (MRW) | k y h complementarios; λ≈2.7% reconcilia con los datos; educación casi duplica y* |

### Nivel 6 — Dinero y política monetaria ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m34 ✔ | Teoría cuantitativa | MV=PY; proporcionalidad 2M⇒2P exacta; aritmética de π en tasas |
| m35 ✔ | Neutralidad del dinero | la comba (Y) y la escalera (P) sobre m25; P∞/P0 = M'/M exacto |
| m36 ✔ | Señoreaje | Laffer del impuesto inflación (Cagan); pico=1/b; Perú 1988-90 como episodio |
| m37 ✔ | Multiplicador monetario | m=(1+c)/(c+r); B=C+R exacta; el pánico colapsa M (→m73); crítica endógena |
| m38 ✔ | Regla de Taylor (ANCLA) | principio 1+φπ>1 verificado; frontera con el ZLB; Burns como escenario |
| m39 ✔ | Banco central y tasa (corredor) | fijar el PRECIO del dinero; piso/techo atan exacto; acotación universal |
| m40 ✔ | Inflación objetivo | anclaje θ; semivida=ln2/−ln(1−θ); adopción BCRP 2002 como escenario |
| m41 ✔ | Credibilidad (Barro-Gordon) | sesgo=λαū exacto; sorpresa nula; la regla domina; conservador de Rogoff |
| m42 ✔ | Expectativas racionales | inefectividad exacta (anunciada⇒y=ȳ); sorpresa funciona una vez |

### Nivel 7 — Macroeconomía abierta ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m43 ✔ | Balanza de pagos | CC+CF=ΔRIN exacta; flotación ⇒ CF=−CC; la fuga se paga con reservas |
| m44 ✔ | Cuenta corriente | CC=(Sp−I)+(T−G); déficits GEMELOS exactos; el "déficit bueno" |
| m45 ✔ | Tipo de cambio nominal | mercado PEN/USD; bonanza aprecia; intervención estilo BCRP |
| m46 ✔ | Tipo de cambio real | RER=E·P*/P; el HÁMSTER exacto (dE=dP ⇒ RER=100); apreciación silenciosa |
| m47 ✔ | PPP | E_ppp sigue a π−π*; RER constante en la senda; vida media del desvío (puzzle) |
| m48 ✔ | UIP | E=Ee(1+i*+ρ)/(1+i); la FED deprecia HOY; el riesgo se cobra en el cambio |
| m49 ✔ | Mundell-Fleming (ANCLA) | 4 teoremas exactos: fiscal nula/potente, monetaria potente/imposible según régimen |
| m50 ✔ | Trilema | elegir dos; T*=RIN0/fuga exacto; controles ×10; la esquina peruana (flotar) |

### Nivel 8 — Modelos macroeconómicos modernos ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m51 ✔ | Modelo IS-MP | la LM muere: el BC fija r con regla; la M no existe como parámetro (verificado) |
| m52 ✔ | AD-AS dinámico con expectativas | el NK "de entrenamiento"; la regla α ES el ancla; estanflación dinámica |
| m53 ✔ | Nuevo keynesiano básico | Calvo (¡en biblioteca!); duración=1/(1−θ) exacta; θ=0 recupera m42 |
| m54 ✔ | Curva IS dinámica (Euler) | x0=−σΣ(tasas futuras); FORWARD GUIDANCE como teorema |
| m55 ✔ | NKPC | inflación=profecía (κΣβ^j x); sin inercia intrínseca; el futuro pesa β^j exacto |
| m56 ✔ | IS+NKPC+Taylor (ANCLA MAYOR) | DSGE mínimo resuelto a mano (coef. indeterminados) y verificado ecuación×período; violar el principio ⇒ Burns emerge del álgebra |
| m57 ✔ | Ciclos reales (RBC) | ciclo sin dinero; amplificación 1+α_nη y jerarquía σ_i>σ_y>σ_c exactas; persistencia heredada |
| m58 ✔ | Shock tecnológico | la IRF como huella digital; decae a ρ exacto; semivida verificada |
| m59 ✔ | Shock monetario | EL test RBC vs NK: cero vs comba θ^{t+1}; área real=θ/(1−θ)dM exacta |
| m60 ✔ | Shock fiscal | un multiplicador POR RÉGIMEN: 5 fórmulas del currículo compitiendo (auditables) |
| m61 ✔ | Shocks de productividad | propagación: semivida(y)>semivida(a) con capital; la joroba de k; cierre metodológico |

### Nivel 9 — Modelos fiscales ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m62 ✔ | Restricción presupuestaria | usos=fuentes exacta; primario (decisión) vs total (herencia r·B) |
| m63 ✔ | Deuda pública | la bola de nieve: SP=0 ⇒ (1+r)^t exacto; SP*=r·B0 congela; duplicación ln2/ln(1+r) |
| m64 ✔ | Dinámica deuda/PIB (ANCLA) | Δb≈b(r−g)−sp; sp* congela exacto; g>r licúa sola; la bañera fiscal |
| m65 ✔ | Sostenibilidad | sp* requerido vs techo; b_max=cruce exacto; el ESTRÉS voltea el veredicto |
| m66 ✔ | Déficit estructural vs cíclico | el termómetro al sol; el boom esconde (pre-2008); la regla como vacuna |
| m67 ✔ | Equivalencia ricardiana | λ=0: compensación total exacta; VP=dT; la ruptura lineal en λ (crédito) |
| m68 ✔ | Política contracíclica | atenuación (1−mult·φ) exacta; simétrica⇒deuda 0; el RATCHET en escalera |
| m69 ✔ | Austeridad | b1=(b0−dA)/(1−mult·dA/100); mult*=100/b0 exacto; la paradoja del denominador |
| m70 ✔ | Multiplicadores (juicio empírico) | condicional al estado; el ZLB apaga al BC; Perú<1<ZLB; rangos de literatura |

### Nivel 10 — Modelos de crisis ✔ completo

| id | modelo | núcleo |
|---|---|---|
| m71 ✔ | Crisis financiera | balance apalancado; ΔE/E = −shock·λ exacto; insolvencia en shock=1/λ |
| m72 ✔ | Burbuja de activos | Gordon; burbuja racional (1+r)/(1−q); arbitraje sin almuerzo gratis |
| m73 ✔ | Crisis bancaria | Diamond-Dybvig (Nobel 2022); DOS equilibrios; el seguro elimina el pánico sin costo |
| m74 ✔ | Crisis cambiaria | Krugman/Obstfeld; el ataque anticipa (T−h) con reservas en la bóveda |
| m75 ✔ | Sudden stop | Calvo (¡en biblioteca!); ΔCC=−ΔCF exacto; el golpe a no transables |
| m76 ✔ | Crisis de deuda soberana | zona de crisis (Calvo/Cole-Kehoe): 3 regímenes por umbrales; profecía autocumplida |
| m77 ✔ | Crisis de balanza de pagos | identidad de reservas en el tiempo; el RER (m46) como CAUSA, reservas síntoma |
| m78 ✔ | Trampa de deuda | m64+m69+m76: lazos endógenos que hacen explosiva la aritmética; 3 salidas |
| m79 ✔ | Recesión por shock financiero | acelerador: κ=λ²·impacto; el multiplicador de m04 con el alma invertida; κ=1 separa recesión de colapso |
| m80 ✔ | Crisis sistémica | contagio en red; robust-yet-fragile; la estabilidad como bien público — cierre teórico troncal |

### Nivel 11 — Escenarios aplicados (síntesis) ✔ completo

Motor compartido `nivel_11/_episodio.py` (AD-AS dinámico de m52 con secuencias
de shocks). Cada modelo es un EPISODIO que combina mecanismos previos.

| id | escenario | núcleo verificado |
|---|---|---|
| m81 ✔ | COVID-19 | doble shock (oferta+demanda); el MISMO modelo explica 2020 (desinfla) y 2021-22 (infla) |
| m82 ✔ | Shock petrolero | estanflación (m19/m24); acomodar (Burns) vs resistir (Volcker), ninguno gratis |
| m83 ✔ | Shock de alimentos | peso en el IPC (40% vs 10%) amplifica exacto; regresivo; Perú=m113 |
| m84 ✔ | Devaluación | competitividad (m49) vs balance (m71); el signo cambia en la dolarización de cruce γ/β |
| m85 ✔ | Inflación importada | Δπ=passthrough×dev×peso; el ancla (m40) baja el passthrough >4× |
| m86 ✔ | Alza de la FED | dilema defender/flotar; no hay salida gratis (trilema m50); reservas dan margen |
| m87 ✔ | Salida de capitales | push/pull; el push global domina (huye con fundamentos sanos); reservas amortiguan |
| m88 ✔ | Boom de materias primas | shock de ingreso; enfermedad holandesa (m46); ahorrar el transitorio (m68) |
| m89 ✔ | Caída del cobre | TRES canales (externo m43 + fiscal m62 + real m10); preludio de m103 |
| m90 ✔ | Shock de productividad | mueve el potencial (m22/m29) vs demanda transitoria; respuesta OPUESTA |
| m91 ✔ | Gasto público masivo | multiplicador (m60) vs servicio capitalizado (m64); ZLB+productivo+r<g |
| m92 ✔ | Recesión con inflación | diagnóstico: oferta (m24) vs demanda con inercia (m14); el tratamiento opuesto |
| m93 ✔ | Estanflación (los 70) | shock sobre Phillips desanclada (m14)+acomodo (m41); el ancla (m40) es la diferencia con hoy |
| m94 ✔ | Deflación | espiral de Fisher; tasa real sube en el ZLB (m12); la paradoja de la credibilidad (Krugman) |
| m95 ✔ | Trampa de liquidez | Japón/2008-2015; el menú del ZLB; el fiscal es lo más potente (m91) |
| m96 ✔ | Crisis de deuda soberana | anatomía: zona (m76)→espiral (m78); Grecia (austeridad) vs Draghi (backstop) vs Argentina (quita) |

### Nivel 12 — Laboratorio macroeconómico del Perú (con datos reales)

Aquí el laboratorio se une con el resto de datafw: **cada modelo se calibra o
contrasta con series oficiales adquiridas por los conectores** (nunca tecleadas).

| id | modelo | fuente de datos (conector) |
|---|---|---|
| m97 ✔ | Crecimiento del Perú | bcrp PN01728AM (PBI var%); 2004-24: media 4.5%, boom +9.2% (2008), COVID −10.9% (2020) |
| m98 ✔ | PIB potencial vs observado | bcrp PN01770AM (índice); tendencia + brecha; superciclo (+) vs COVID (−) |
| m99 ✔ | Inflación peruana | bcrp PN01273PM (IPC); anclada ~2%, dentro del rango meta 1-3% del BCRP |
| m100 ✔ | Regla de Taylor para el BCRP | bcrp (tasa, inflación); coef inflación 0.55<1 → sesgo de variable omitida (honestidad econométrica) |
| m101 ✔ | Tasa de referencia → inflación | bcrp; correlación contemporánea (+) = causalidad inversa, no efecto de política |
| m102 ✔ | Tipo de cambio PEN/USD | bcrp PN01207PM; flotación administrada, volatilidad << régimen libre |
| m103 ✔ | Precio del cobre → crecimiento | bcrp PN01652XM+PN01728AM; corr(Δcobre,g)=+0.45, R²~0.20; importa el CAMBIO no el nivel (m89) |
| m104 ✔ | Precio del cobre → tipo de cambio | bcrp PN01652XM+PN01207PM; niveles engañan (+0.12), cambios sin 2020-21 = −0.45; el TC es precio de activo (m111) |
| m105 ✔ | Términos de intercambio → PIB vs ingreso | bcrp PN38923BM+PM04901AA+PM04904AA; el cobre mueve la TdI (0.85), la TdI mueve el INGRESO no el PBI-volumen (efecto +56 mil M S/ en 2024; ingreso 7.5% vs PBI 3.5%) |
| m106 ✔ | Inversión pública → crecimiento | bcrp PM10081FA+PN01728AM; corr ~0 (contracíclica: 2009 estímulo inv↑ PBI↓, m69); endogeneidad, no efecto (m70) |
| m107 ✔ | Gasto público → multiplicador fiscal | bcrp PN02207FM+PM04946AA; naive~0.1 (sesgado, m106), identificado ~0.5-1 (m70, abierto→filtra m43), CONDICIONAL (ZLB>1, m91) |
| m108 ✔ | Deuda pública → sostenibilidad | bcrp PN03371FQ/PM04946AA; aritmética de m64: 45%(2004)→19%(2013 disciplina)→34%(2020 COVID); contraejemplo de m96 |
| m109 ✔ | Exportaciones → crecimiento | bcrp PM04933AA+PN01728AM; corr +0.74, R²=0.55 (motor externo, m43); informa porque es EXÓGENA (contraste con m106) |
| m110 ✔ | Shock externo sobre Perú | bcrp (síntesis cobre+TdI+exportaciones); índice externo corr +0.58 con crecimiento (m86-m89); pero R²~0.34 (2/3 doméstico; 2020 precio↑/volumen↓) |
| m111 ✔ | FED → flujo de capitales hacia Perú | bcrp PD04722MM+PN01207PM (reales) + tasa FED (dato público ilustrativo, FRED bloqueado); corr FED-BCRP +0.54 (trilema m50); salvo 2021 (riesgo local, m104) |
| m112 ✔ | Minería → crecimiento y empleo | bcrp PM04972AA+PN01728AM; paradoja del enclave: ~13% PBI/~60% export (corr +0.53, amplifica) pero ~1.5% empleo (INEI declarado) → diversificar (m115) |
| m113 ✔ | Inflación importada (passthrough) | bcrp PN01207PM+PN01273PM; passthrough ≈0 (sol −12%/+11% en 2015/2021, inflación en banda) = dividendo de credibilidad (m40); 2022 inflación global con sol estable (m83) |
| m114 ✔ | Shock climático → inflación y producción | El Niño como shock de oferta transitorio (m11/m52/m83); estanflacionario, reversible con ancla (m40); BCRP mira a través (m113); calibración didáctica (sin conector SENAMHI) |
| m115 ✔ | Modelo macroeconómico simplificado del Perú | SÍNTESIS de m97-m114: cobre/FED/fiscal → crecimiento, ingreso, inflación, sol, deuda; economía abierta con ancla (m113) y disciplina (m108); reto = diversificar (m112) |

**Regla del nivel 12**: aplica la política solo-ejemplos (regla 0 del
framework) — activar series/datasets nuevos requiere pedido explícito de
Edison; los datos pasan por raw → audited → clean antes de tocar un modelo.

## 7. Ruta de construcción

Secuencia troncal (un modelo "ancla" por etapa, el resto del nivel después):

> m01→m05 ✔ → **m10 ✔** → m15 ✔ → m20 ✔ → m26 ✔ → m38 ✔ → m49 ✔ → m56 ✔ → m63 ✔ → m80 ✔ → m96 ✔ → **m115 ✔ (currículo macro COMPLETO)**

- **Hito 1 (2026-08-19): nivel 1 completo + m10** — 6 modelos. ✔
- **Hito 2 (2026-08-19): nivel 2 completo** — m06-m09 (descomposición didáctica
  del IS-LM), m11 (expulsión con sus límites teóricos como tests) y m12
  (trampa: primer modelo con régimen endógeno). ✔
- **Hito 3 (2026-08-19): nivel 3 completo** — la economía de la inflación.
  Primeros modelos **dinámicos** (m14: espiral aceleracionista; m16: cierre de
  brecha) y **estocásticos** (m17: AR(1) con semilla reproducible). m18-m19
  anticipan el plano (Y,P) con las dos firmas de shock. ✔
  Total acumulado: 19 modelos, 68 verificaciones.
- **Hito 4 (2026-08-19): nivel 4 completo — el aparato AD-AS.** La AD se
  DERIVA del IS-LM (verificado: cada punto de m20 reproduce m10); solver
  cuadrático compartido en `modelos/nivel_04/_adas.py`; neutralidad del dinero
  exacta a largo plazo (m22) y NO neutralidad a corto (m23) como teoremas
  contrastados; m25 es la "película" (Pe_{t+1}=P_t → trayectoria a la LRAS).
  Total acumulado: 25 modelos, 92 verificaciones. ✔
- **Hito 5 (2026-08-19, vigente): DE SLIDERS A LABORATORIO** (observación de
  Edison: "no necesitas más contenido todavía; necesitas convertir esos
  modelos en un laboratorio interactivo serio"). Entregado en este hito:
  capas modelo/render/experiencia, lámina de experimento de 5 zonas en cada
  escenario del reporte, modo `experimento` (hipótesis→ejecutar→✔/✘),
  `sensibilidad` y `comparar` genéricos, plantilla de 20 puntos, pregunta
  económica en los 25 modelos, mecanismos de transmisión y m10 como buque
  insignia (variables, derivación, grupos de parámetros, ecuaciones
  calibradas). **CERRADO el mismo día**: mecanismos de transmisión en los
  81/81 escenarios; plantilla profunda (variables, derivación, calibradas)
  en las anclas de cada nivel (m03, m04, m10, m12, m14, m23) y grupos de
  parámetros en m10/m23. La profundización del resto es incremental (§2). ✔
- **Hito 6 (2026-08-19): nivel 5 completo — crecimiento económico.** Solow con
  motor común (`nivel_05/_solow.py`), transición con semivida verificada,
  regla de oro con ineficiencia dinámica demostrada en toda la senda,
  progreso técnico con BGP exacta, convergencia absoluta/condicional, trampa
  de pobreza con histéresis y big push, AK como anti-Solow y MRW reconciliando
  la velocidad observada. Los 8 modelos con plantilla profunda (pregunta,
  variables, derivación, cadenas, calibradas en m26/m28/m32/m33).
  Total acumulado: **33 modelos, 124 verificaciones**. ✔
- **Hito 7 (2026-08-19): nivel 6 completo — dinero y política monetaria.**
  Arco completo: por qué imprimir es inflación (m34-m36), quién crea el dinero
  (m37), y el régimen moderno entero — regla (m38), instrumento (m39), ancla
  (m40), fundamento institucional (m41) y fundamento de expectativas (m42).
  El sesgo λαū de Barro-Gordon y la inefectividad de Sargent-Wallace como
  verificaciones exactas. Total acumulado: **42 modelos, 160 verificaciones**. ✔
- **Hito 8 (2026-08-19): nivel 7 completo — macroeconomía abierta.** Las
  cuentas (m43-m44), los precios (m45-m46), las paridades (m47-m48) y la
  síntesis de política (m49 con sus 4 teoremas de eficacia EXACTOS por
  régimen; m50 con el reloj del trilema T*=RIN0/fuga). Calibración de m49
  con base idéntica entre regímenes (verificada): los experimentos comparan
  políticas, no calibraciones. Total: **50 modelos, 193 verificaciones**. ✔
- **Hito 9 (2026-08-19): nivel 8 completo — los modelos modernos.** La
  transición (IS-MP, AD-AS dinámico, Calvo), las curvas racionales (m54-m55:
  forward guidance e inflación-profecía como teoremas) y el MODELO DE 3
  ECUACIONES (m56) resuelto por coeficientes indeterminados y verificado
  ecuación por ecuación — un DSGE mínimo auditado a mano donde converge todo
  el currículo. El bloque RBC (m57-m61) cierra con el duelo de paradigmas
  (m59: cero vs comba) y la lección metodológica (m61: colas y jorobas).
  Total: **61 modelos, 238 verificaciones**. ✔
- **Hito 10 (2026-08-19): nivel 9 completo — los modelos fiscales.** La
  aritmética de la deuda (m62-m66: identidad, bola de nieve, la ecuación
  central Δb≈b(r−g)−sp, el diagnóstico con estrés, estructural vs cíclico)
  y los debates (m67-m70: Barro con la ruptura λ, la contracíclica con el
  ratchet en escalera exacta, la paradoja de la austeridad con su frontera
  mult*=100/b0, y el juicio empírico condicional de los multiplicadores).
  Total: **70 modelos, 274 verificaciones**. ✔
- **Hito 11 (2026-08-19): nivel 10 completo — los modelos de crisis.** Los
  mecanismos de los niveles previos se ROMPEN: el multiplicador de m37 en
  reversa (m73 corridas), el reloj del trilema m50 con expectativas (m74 el
  ataque anticipa), la aritmética de m64 con lazos endógenos (m78 trampa), el
  multiplicador de m04 con el alma invertida (m79 acelerador). Tres profecías
  autocumplidas con backstop como cura (m73/m74/m76) y el cierre sistémico en
  red (m80, robust-yet-fragile). Total: **80 modelos, 314 verificaciones**;
  con él termina el currículo TEÓRICO troncal (m01→m80). ✔
- **Hito 12 (2026-08-19): nivel 11 completo — los escenarios aplicados.** 16
  EPISODIOS que combinan los mecanismos de todo el currículo sobre el motor
  compartido `_episodio.py` (AD-AS dinámico de m52). COVID (el doble shock que
  explica 2020 Y 2021 con el mismo modelo), los shocks de oferta (petróleo,
  alimentos), la dimensión externa (devaluación, FED, salida de capitales,
  cobre), y los grandes episodios de política (estanflación de los 70,
  deflación de Fisher, trampa de liquidez de Japón, crisis soberana de
  Grecia/Argentina). Bug estructural corregido (parámetros huérfanos en
  m94/m96) + guardia de coherencia permanente en base.verificar. Total:
  **96 modelos, 474 verificaciones** (378 de contenido + 96 de coherencia). ✔
- **Hito 13 (2026-08-19): nivel 12 (1/N) — el laboratorio aterriza en el Perú
  con datos BCRP reales.** Edison autorizó activar los conectores BCRP; se
  descargaron 6 series macro (PBI, IPC, tasa, tipo de cambio; 2004-2024) vía
  `connectors/bcrp` y se destiló un **snapshot anual embebido**
  (`_series_bcrp.py`) para que los modelos sean auto-contenidos (`data/` está
  en `.gitignore`); los datos mensuales de `data/raw/` sirven como resolución
  fina cuando están presentes (`_datos_bcrp.py`). m97-m102 leen la serie,
  calculan hechos estilizados y **verifican contra el dato real** (no contra
  una calibración didáctica). Dos modelos enseñan honestidad econométrica: m100
  presenta el coeficiente Taylor real 0.55<1 como sesgo de variable omitida (no
  lo esconde) y m101 lee la correlación tasa-inflación como causalidad inversa.
  m103-m104 añaden el **canal del cobre**: m103 lo cuantifica sobre el
  crecimiento (corr Δcobre-g = +0.45, R²~0.20; importa el cambio no el nivel),
  m104 lo lleva al tipo de cambio y descubre que ahí es débil y se ROMPE en las
  crisis (2021: cobre récord + sol débil = fuga de capitales m111; el TC es un
  precio de activo). m105 cierra el bloque externo generalizando el cobre a los
  TÉRMINOS DE INTERCAMBIO (PN38923BM): el cobre los mueve (corr 0.85), pero
  ellos mueven el INGRESO nacional (efecto TdI de PM04904AA), no el PBI-volumen
  — se disuelve la paradoja "TdI récord 2024, PBI +3.5%" (el ingreso creció
  +7.5%: fue poder adquisitivo, no producción). m106 y m109 abren el bloque
  fiscal/real con un contraste metodológico: la inversión pública correlaciona
  ~0 con el crecimiento (contracíclica, endógena — el estímulo de 2009 es el
  caso de manual, m69), pero las exportaciones correlacionan +0.74 (R²=0.55)
  porque son EXÓGENAS (demanda mundial, m88) — la correlación revela causa solo
  cuando el impulsor no reacciona al ciclo (m70). m107 y m108 completan el
  bloque fiscal: m107 lleva la endogeneidad de m106 al MULTIPLICADOR (naive ~0.1
  sesgado, identificado ~0.5-1 por m70, condicional al estado m91) y m108 aplica
  la aritmética de m64 a la deuda peruana real (45% en 2004 → mínimo 19% en 2013
  por la disciplina del boom → salto a 34% en 2020 por el COVID, sostenible: el
  contraejemplo virtuoso de m96). m110 sintetiza el canal externo REAL en un
  índice (cobre+TdI+exportaciones) que correlaciona +0.58 con el crecimiento
  (m86-m89), pero con honestidad: R²~0.34, dos tercios del ciclo son domésticos
  (2020 es la excepción — precio externo ↑ pero volumen ↓ por el cierre de minas,
  shock doméstico). m111 añade el canal FINANCIERO externo: la tasa de la FED
  marca los flujos de capital y el Perú la sigue en parte (corr FED-BCRP +0.54,
  el trilema de m50), salvo cuando el riesgo político local domina (2021, m104);
  tasas BCRP reales + tasa FED como dato público ilustrativo (FRED bloqueado).
  m112 y m113 cierran los canales sectoriales: m112 la paradoja del ENCLAVE
  minero (mucho valor, ~13% del PBI y ~60% de exportaciones, pero ~1.5% del
  empleo → diversificar, m115) y m113 el PASSTHROUGH casi nulo (una devaluación
  del sol NO se traslada a la inflación gracias al ancla del BCRP, m40; 2022 fue
  inflación global con sol estable, m83). Total: **113 modelos, 559
  verificaciones**. Pendiente del nivel: m114 (clima) y m115 (síntesis).
- **Hito 14 (2026-08-20): nivel 12 completo — el CURRÍCULO MACRO CERRADO.** m114
  modela El Niño como shock de oferta transitorio (m11/m52/m83): estanflacionario
  y reversible, con la lección de que el BCRP debe "mirar a través" (m113) y la
  respuesta correcta es fiscal (m106); calibración didáctica (sin conector
  SENAMHI). m115 es la SÍNTESIS que cierra el currículo: un modelo estilizado del
  Perú donde un shock (cobre/FED/fiscal) se propaga por los cinco canales del
  nivel —externo real (m103/m105/m110), externo financiero (m104/m111), monetario
  (m99/m100/m113), fiscal (m106-m108) y estructural (m112)— y muestra el
  diagnóstico de fondo: economía abierta y dependiente de commodities, con ancla
  monetaria y disciplina fiscal que dan resiliencia, cuyo reto pendiente es
  diversificar. Total: **115 modelos, 569 verificaciones (454 de contenido + 115
  de coherencia)** — el currículo macro de 115 modelos en 12 niveles está
  COMPLETO. ✔
- Hito 15: extender a micro / econometría / matemática (§9), con la misma
  filosofía (ficha + escenarios + verificaciones); la econometría NO duplica
  `pipeline/`. Los datos reales del Perú (nivel 12) siguen bajo solo-ejemplos.

## 8. Decisiones diferidas (registradas, no tomadas)

- **Interactividad web**: exportar los modelos a Quarto + Observable JS para el
  ecosistema de blogs (`pub_*`); los sliders locales de matplotlib ya cubren la
  experimentación personal.
- **DSGE completo / Dynare** (nivel 8 avanzado): evaluar al llegar; el modelo
  de 3 ecuaciones (m56) se puede resolver con numpy/scipy sin Dynare.
- **Libro del laboratorio**: compilar las fichas + reportes en un PDF vía la
  plantilla LaTeX de `03 writing` cuando haya masa crítica de niveles.
- **Verificación bibliográfica**: cuando Edison verifique un manual de macro de
  la biblioteca (procedimiento pdftotext → localizar → extraer → ficha), las
  procedencias `conocimiento general` de los modelos afectados se elevan a
  `libro verificado` y se actualiza la matriz.

## 9. Extensión a otras disciplinas (directiva de Edison, 2026-08-19)

Terminado el currículo macro, el laboratorio se extenderá a **microeconomía,
econometría y matemática para economistas** con la misma filosofía (ficha
histórica + motor numérico + escenarios + verificaciones). Implicación
arquitectónica ya tomada: `base.py` es **agnóstico a la disciplina** — `Modelo`,
`Ficha`, `Escenario` y `Verificacion` no contienen nada específicamente
macroeconómico. **Decisión tomada (2026-08-20)**:

- `simuladores/` es el **paraguas** del laboratorio; el motor
  (`base/graficos/reporte/laboratorio`) vive en la raíz y cada disciplina es una
  **subcarpeta hermana** con su `config/main/app/modelos` propios:
  `simuladores/macro/` (esta), `simuladores/estadistica/` (en curso, ids `eNN`),
  y futuras `econometria/`/`micro/`/`mate/`. El `main.py` de cada disciplina
  añade la raíz al `sys.path` (motor) y su carpeta primero (config/modelos) — el
  motor se comparte sin copiarlo. Correr: `cd simuladores/<disciplina> && python3 main.py`.
- Cada disciplina tendrá su documento de diseño gemelo
  (`docs/LABORATORIO_MICRO.md`, …) con su propio currículo.
- La econometría del laboratorio se apoyará en lo ya construido en
  `pipeline/` (diagnóstico, MCO, panel): los "modelos" econométricos del
  laboratorio serán fichas pedagógicas SOBRE los métodos ya implementados y
  validados allí — no se duplica código (regla del framework).
