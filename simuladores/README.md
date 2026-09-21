---
tipo: readme
estado: activo
---
# simuladores/ — el laboratorio computacional (multi-disciplina)

Laboratorio histórico y computacional de economía y sus herramientas: cada
teoría o método reconstruido como **modelo ejecutable** con ficha pedagógica
(contexto histórico → derivación → intuición → limitaciones), simulación de
escenarios y **verificación numérica de sus teoremas**.

Es **un solo laboratorio con varias disciplinas hermanas** que comparten un
motor común. El motor (agnóstico a la disciplina) vive en la raíz; cada
disciplina es una subcarpeta con su propia app, config y modelos.

```
simuladores/
├── base.py         MOTOR compartido: dataclasses (Modelo/Ficha/Escenario/
├── graficos.py     Verificacion), cálculo y verificación (base); render
├── laboratorio.py  matplotlib con anti-solape y dibujo progresivo (graficos);
├── reporte.py      láminas de experimento (laboratorio); informe MD (reporte)
│
├── macro/          ✅ Macroeconomía — 115 modelos, 12 niveles, 569 verificaciones
├── estadistica/    🚧 Estadística — 239 temas en 20 secciones (+ animaciones Manim)
└── …               econometría / micro / mate (futuras disciplinas hermanas)
```

## Uso

### Cómo correr una disciplina

Cada disciplina tiene su propio punto de entrada; su `main.py` añade la raíz al
`sys.path` para reusar el motor:

```bash
cd simuladores/macro   &&  python3 main.py            # abre el laboratorio macro
cd simuladores/macro   &&  python3 main.py verificar  # control de calidad (100%)

cd simuladores/estadistica  &&  python3 main.py       # (scaffolding en curso)
```

## Las capas de visualización (un modelo, tres vistas)

El **modelo nunca se mezcla con la interfaz**. La misma lógica (`base.py`) se
muestra de tres formas complementarias:

| Vista | Herramienta | ¿En vivo? | Para qué |
|---|---|---|---|
| Estática | matplotlib | figura | reportes (`reporte`), ver el estado |
| Interactiva / animada | matplotlib (`Slider`/`FuncAnimation`) | **sí, en la app** | explorar: mover parámetros y ver en tiempo real |
| Video pulido | **Manim** (env conda aparte) | archivo | redes / clases / incrustar (ver `estadistica/animaciones/`) |

## Estructura

Una carpeta por disciplina (`macro/`, `estadistica/`, …), cada una con sus modelos por nivel, sus animaciones y su
`README.md`; `CLAUDE.md` guarda las reglas del laboratorio. Detalle por disciplina en su propio README.

## Diseño y currículos

- Macro: [macro/docs/laboratorio-macro.md](macro/docs/laboratorio-macro.md)
- Estadística: [estadistica/docs/laboratorio-estadistica.md](estadistica/docs/laboratorio-estadistica.md)

## Convención al añadir una disciplina

Crear `simuladores/<disciplina>/` con `config.py` (rutas + paleta), `main.py`
(bootstrap que añade la raíz al path + CLI), `app.py` y `modelos/nivel_NN/`.
**Prohibido copiar el motor** (`base/graficos/reporte/laboratorio`): se importa
de la raíz. `salidas/` de cada disciplina es regenerable (en `.gitignore`).

## Límite honesto

- Es un laboratorio pedagógico: los modelos reproducen teoremas y escenarios de manual, no series reales ni pronósticos;
  los datos vivos viven en `02 analysis`.
- Vive dentro de `10 Class` desde 2026-09-20 (venía de `02 analysis`): las rutas de los currículos de cada disciplina
  se citan desde su README, no desde aquí.
