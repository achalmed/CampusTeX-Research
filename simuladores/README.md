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
motor común. El motor (agnóstico a la disciplina) vive en la raíz, con la
aplicación (`app.py`); cada disciplina es una subcarpeta con su `config.py`,
su `main.py` y sus `modelos/`.

```
simuladores/
├── base.py         MOTOR compartido: dataclasses (Modelo/Ficha/Escenario/
├── graficos.py     Verificacion), cálculo y verificación (base); render
├── laboratorio.py  matplotlib con anti-solape y dibujo progresivo (graficos);
├── reporte.py      láminas de experimento (laboratorio); informe MD (reporte)
├── app.py          la aplicación (recorrido pedagógico) que usan todas las disciplinas
├── fuentes.py      comprueba cada cita (calibre_id, hoja del PDF, pasaje) contra la edición
│
├── macro/          Macroeconomía — currículo completo por niveles
├── estadistica/    Estadística — en curso (temario.yml) (+ animaciones Manim)
└── …               econometría / micro / mate (futuras disciplinas hermanas)
```

## Uso

### Cómo correr una disciplina

Cada disciplina tiene su propio punto de entrada; su `main.py` añade la raíz al
`sys.path` para reusar el motor:

```bash
cd simuladores/macro   &&  python3 main.py            # abre el laboratorio macro
cd simuladores/macro   &&  python3 main.py verificar  # control de calidad (100%)

cd simuladores/estadistica  &&  python3 main.py       # abre el laboratorio de estadística
cd simuladores/estadistica  &&  python3 main.py fuentes  # citas comprobadas contra la edición
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

Una carpeta por disciplina (`macro/`, `estadistica/`, …), cada una con sus modelos por nivel y su
`matriz_trazabilidad.csv`; `CLAUDE.md` guarda las reglas del laboratorio. Cuántos modelos y verificaciones
tiene cada disciplina lo dice `python3 main.py verificar` dentro de ella.

## Diseño y currículos

- Macro: [macro/docs/laboratorio-macro.md](macro/docs/laboratorio-macro.md)
- Estadística: [estadistica/docs/laboratorio-estadistica.md](estadistica/docs/laboratorio-estadistica.md)

## Convención al añadir una disciplina

Crear `simuladores/<disciplina>/` con `config.py` (rutas + paleta), `main.py`
(bootstrap que añade la raíz al path + CLI) y `modelos/nivel_NN/`; la app es la del motor.
**Prohibido copiar el motor** (`base/graficos/reporte/laboratorio`): se importa
de la raíz. `salidas/` de cada disciplina es regenerable (en `.gitignore`).

## Límite honesto

- Es un laboratorio pedagógico: los modelos reproducen teoremas y escenarios de manual, no pronósticos. Los que usan
  datos reales (el nivel 12 de macro, con series del BCRP) los leen de `02 analysis` por nombre; el laboratorio no adquiere datos.
- «Página verificada» significa que el pasaje citado está en esa hoja del PDF del `calibre_id`: lo comprueba
  `fuentes.py` con el texto que da `core/py-common/biblioteca.py`. Sin la biblioteca en la máquina, la cita queda
  «no comprobable», no verificada; y la página impresa solo se confirma si el PDF trae el folio en su texto.
- Las rutas de los currículos de cada disciplina se citan desde su README, no desde aquí.
