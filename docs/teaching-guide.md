# Manual de uso para docentes

Guía práctica para usar este repositorio como sistema de preparación y
dictado de clases. No necesitas saber programar: solo ejecutar comandos
en la terminal desde la raíz del repositorio.

## Encontrar el material de una clase

Todo lo de una clase está en `course/sessions/session_NN_tema/`:

| Quiero... | Abro... |
|---|---|
| Repasar las diapositivas | `slides/slides.pdf` |
| Recordar qué iba a decir | `teaching/teacher_notes.md` |
| Ver el plan y los tiempos | `teaching/lesson_plan.md` |
| El material para estudiantes | `practice/` |
| El quiz o la rúbrica | `evaluation/` |
| Qué mejorar la próxima vez | `teaching/retrospective.md` |

## Preparar una clase nueva

```bash
./scripts/new-session.sh 07 "Marco Teórico"
```

Esto crea la carpeta completa con todos los esqueletos. Luego sigue el
orden natural: `metadata.yml` → `lesson_plan.md` → diapositivas → guion →
práctica/evaluación. Detalle completo en
[session-creation.md](session-creation.md).

## Compilar diapositivas

```bash
./scripts/build-session.sh 02    # una sesión
./scripts/build-course.sh        # todo el curso
```

No necesitas saber qué motor LaTeX usa cada deck: el script lo detecta.
La sesión 4 (Quarto) también se renderiza con el mismo comando.

## Después de cada clase: la retrospectiva

El hábito más valioso de este sistema. Apenas termine la clase, abre
`teaching/retrospective.md` y anota 5 minutos:

- qué preguntas hicieron los estudiantes,
- qué concepto costó y qué analogía funcionó,
- qué actividad se pasó de tiempo,
- qué cambiarías.

El próximo semestre, tú (o quien herede el curso) empezará leyendo eso.

## Compartir material

- **Una sesión completa a un colega:** comprime la carpeta
  `session_NN_*` — es autosuficiente.
- **Solo material del estudiante:** comparte `slides/slides.pdf` +
  `practice/` + `resources/links.md` (el guion y la retrospectiva son tuyos).

## Reusar este curso como plantilla de otro

Copia el repositorio, edita `config/course.yml` con los datos del nuevo
curso y crea sesiones con `new-session.sh`. Nada más que tocar.

## Si algo no funciona

```bash
./scripts/doctor.sh     # ¿está todo instalado?
./scripts/validate.sh   # ¿la estructura está completa?
```
