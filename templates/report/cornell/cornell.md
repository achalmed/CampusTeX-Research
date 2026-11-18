---
tipo: plantilla
title: "Hoja Cornell"
titulo: "Hoja Cornell: apuntes de la sesión"
estado: activo
fuentes:
  - {calibre_id: 11126, uso: 'columnas de preguntas, notas y resumen; los cinco pasos (p. 1)'}
  - {pendiente: 'Kiewra (1985)', motivo: 'no está en Calibre; el beneficio de los apuntes está sobre todo en su revisión'}
---

> **Cómo se usa.** Durante la clase escribe en **Notas**, con frases cortas. Después de la clase escribe a la
> izquierda las **Preguntas** que tus notas responden y, al final, el **Resumen** con tus palabras.
> Para repasar, tapa las notas, lee cada pregunta y responde en voz alta; lo que no sale, vuelve a
> estudiarse. La columna de preguntas es el insumo del repaso, porque el beneficio de los apuntes
> está sobre todo en su revisión posterior (Kiewra, 1985). Esta hoja no supone que escribir a mano
> sea mejor que en teclado: es la misma en papel (`cornell.tex`) y aquí.

| Curso | Sesión | Fecha |
|---|---|---|
|  |  |  |

| Preguntas (después de clase) | Notas (durante la clase) |
|---|---|
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

| Resumen (después de clase, con tus palabras) |
|---|
|  |
|  |
|  |

## Ejemplo lleno

**Curso:** Econometría I · **Sesión:** Diseño muestral de la ENAHO

| Preguntas | Notas |
|---|---|
| ¿Por qué la ENAHO no es una muestra aleatoria simple (MAS)? | Muestra probabilística, de áreas, estratificada, bietápica e independiente en cada departamento (INEI, 2026, p. 404). Cada hogar tiene probabilidad conocida de entrar, pero no la misma. |
| ¿Qué es un estrato y qué gana el diseño con él? | **Estrato**: grupo que no se mezcla con otro; se sortea dentro de cada uno. Asegura que todos los dominios estén en la muestra; suele bajar la varianza. |
| ¿Qué se sortea en cada etapa? ¿Qué cuesta sortear conglomerados? | **Conglomerado**: grupo de viviendas vecinas. 1.ª etapa: conglomerados; 2.ª etapa: viviendas dentro de cada uno. Abarata el campo, pero los vecinos se parecen (correlación dentro del conglomerado): cada hogar aporta menos información. |
| ¿Qué representa el factor de expansión? ¿Por qué sale 17,2 % y no 20,2 %? | **Factor de expansión** (`factor07`): cuántos hogares del país representa cada hogar de la muestra; parte de la inversa de la probabilidad de selección. Pobreza de personas: peso `factor07 × mieperho`. ENAHO 2019 sin pesos y sobre hogares: 17,2 %. Con pesos y sobre personas: 20,2 %, la cifra oficial (INEI, 2026, p. 72). |
| ¿Qué mide el efecto de diseño? ¿Qué pasa si lo ignoro? | **Efecto de diseño**: deff = Var(diseño) / Var(MAS). Tasa de 2019: EE como MAS 0,22 pp; EE con el diseño 0,44 pp (el doble); deff ≈ 4,2 con los EE sin redondear. Ignorarlo da intervalos la mitad de anchos: falsa precisión, diferencias “significativas” que no lo son. Muestra efectiva ≈ n / deff. |
| ¿Cómo se declara el diseño antes de estimar? | Stata: `svyset conglome [pw=factor07], strata(estrato)` y luego `svy: mean pobre` (`pobre` = 1 si `pobreza` ≤ 2). Sin `svyset`, el EE sale como MAS. |

**Resumen.** La ENAHO no es una MAS: estratifica, sortea conglomerados y luego viviendas, y
pondera. Sin el factor de expansión y contando hogares la tasa sale 17,2 % y no el 20,2 % oficial;
sin el diseño, el error estándar sale la mitad del verdadero (deff ≈ 4,2). Toda estimación con la
ENAHO se declara con estratos, conglomerados y pesos.

*Nota.* Cifras de pobreza: INEI (2026, p. 72). Tasa sin pesos, errores estándar y efecto de
diseño: cálculo propio con la ENAHO 2019 (pp = puntos porcentuales; EE = error estándar).

## Por qué

La hoja original reparte la página en una columna de preguntas, una de notas y una franja de
resumen, y propone cinco pasos: registrar, preguntar, recitar, reflexionar y repasar al menos diez
minutos a la semana (Cornell University, Learning Strategies Center, 2013, p. 1).

**Fuente:** Cornell University, Learning Strategies Center (2013, Calibre 11126); Kiewra (1985).

## Referencias

Cornell University, Learning Strategies Center. (2013). *The Cornell note-taking system*.

Instituto Nacional de Estadística e Informática. (2026). *Perú: Evolución de la pobreza monetaria
2016-2025. Informe técnico*. INEI.

Kiewra, K. A. (1985). Investigating notetaking and review: A depth of processing alternative.
*Educational Psychologist, 20*(1), 23–32. <https://doi.org/10.1207/s15326985ep2001_4>
