# Crear una sesión nueva

## Comando

```bash
./scripts/new-session.sh NUM "TÍTULO" [--quarto]
```

Ejemplos:

```bash
./scripts/new-session.sh 07 "Marco Teórico"
./scripts/new-session.sh 08 "Análisis de Datos" --quarto
```

## Qué genera

```
course/sessions/session_07_marco_teorico/
├── README.md                  ← índice de la sesión (generado)
├── metadata.yml               ← ficha técnica pre-rellenada desde config/
├── slides/
│   ├── slides.tex             ← deck Beamer con el estilo de la casa
│   │                            (o slides.qmd con --quarto)
│   └── cau-logo.png           ← copia local del logo (marca de agua)
├── teaching/
│   ├── lesson_plan.md         ← plan de clase con secuencia y tiempos
│   ├── teacher_notes.md       ← guion del docente (esqueleto)
│   └── retrospective.md       ← para completar después de la clase
├── practice/  evaluation/  homework/  archive/
└── resources/
    ├── links.md
    └── readings/
```

Todos los placeholders (curso, docente, institución, ciclo, tema Beamer,
duración) se rellenan automáticamente desde `config/course.yml`.

## Después de generar

1. **`metadata.yml`** — completa objetivos, competencias, prerequisitos.
2. **`teaching/lesson_plan.md`** — planifica la secuencia didáctica.
3. **`slides/slides.tex`** — desarrolla el contenido. Compila con
   `./scripts/build-session.sh NUM`.
4. **`teaching/teacher_notes.md`** — escribe el guion (mira los guiones
   reales de las sesiones 1, 3 y 4 como modelo de tono y detalle).
5. Prepara **práctica, evaluación y tarea** desde `templates/documents/`:

```bash
cp templates/documents/quiz.md          course/sessions/session_07_*/evaluation/quiz.md
cp templates/documents/rubric.md        course/sessions/session_07_*/evaluation/rubrica.md
cp templates/documents/practice_guide.md course/sessions/session_07_*/practice/guia.md
cp templates/documents/case_study.md    course/sessions/session_07_*/practice/caso.md
cp templates/documents/reading_guide.md course/sessions/session_07_*/resources/guia_lectura.md
```

6. Valida: `./scripts/validate.sh`.

## Convenciones

- Numeración con dos dígitos (`07`, no `7` — el script normaliza).
- El slug se genera del título: minúsculas, sin tildes, `_` por espacios.
- No renombres las carpetas a mano; si necesitas cambiar un título,
  renombra con `git mv` manteniendo el patrón `session_NN_slug`.
