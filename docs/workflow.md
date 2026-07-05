# Flujo de trabajo semestral

## 1. Antes del semestre

1. Actualiza `config/course.yml` (ciclo, fechas, datos del docente).
2. Revisa/actualiza `course/syllabus/` y compílalo.
3. Define el calendario en `course/calendar/` (semana → sesión → fecha).
4. Define el sistema de evaluación global en `course/evaluation/`.
5. Revisa las retrospectivas del semestre anterior
   (`course/sessions/*/teaching/retrospective.md`) y aplica las mejoras.

## 2. Preparar cada sesión (ideal: 1–2 semanas antes)

```bash
./scripts/new-session.sh NN "Título del Tema"      # si no existe
```

1. Completa `metadata.yml` (objetivos, competencias, prerequisitos).
2. Redacta `teaching/lesson_plan.md` (secuencia inicio–desarrollo–cierre
   con tiempos).
3. Elabora las diapositivas en `slides/` y compila:
   `./scripts/build-session.sh NN`.
4. Escribe el guion en `teaching/teacher_notes.md` (lo que dirás, con
   transiciones y preguntas al auditorio).
5. Prepara `practice/`, `evaluation/` y `homework/` a partir de
   `templates/documents/`.
6. Registra lecturas y enlaces en `resources/`.

## 3. El día de la clase

- Abre `teaching/teacher_notes.md` (checklist pre-clase incluido) y el PDF
  de `slides/`.
- El material del estudiante está en `practice/` listo para distribuir.

## 4. Después de la clase (¡el mismo día!)

Completa `teaching/retrospective.md`: qué funcionó, preguntas frecuentes,
errores comunes, ajustes de tiempo, mejoras. **Este paso convierte el
repositorio en memoria institucional del curso.**

## 5. Fin del semestre

```bash
./scripts/validate.sh   # estructura completa y consistente
./scripts/stats.sh      # panorama del curso
./scripts/clean.sh      # limpiar auxiliares antes del commit final
```

Lee todas las retrospectivas y vuelca las mejoras estructurales en el
syllabus del siguiente ciclo.

## Reutilizar el curso en otro semestre / crear un curso similar

1. Clona o copia el repositorio con otro nombre (`CampusTeX-NuevoCurso`).
2. Edita **solo** `config/course.yml` (nombre, ciclo, docente, logo).
3. Conserva las sesiones que apliquen; crea las demás con `new-session.sh`.
4. Las retrospectivas del curso original son tu guía de qué mejorar.
