# _PLANTILLAS — esqueletos para copiar

Estructuras vacías que se **copian** para crear cosas nuevas (no editar estas; copiar y editar la copia).

| Plantilla | Para crear | Cómo |
|---|---|---|
| `Plantilla_Curso/` | un curso maestro nuevo | `cp -a _PLANTILLAS/Plantilla_Curso CURSOS_MAESTROS/course_NN_<slug>` |
| `Plantilla_Sesion/` | una sesión (`03_SESIONES/SNN/`) | `cp -a _PLANTILLAS/Plantilla_Sesion CURSOS_MAESTROS/course_NN/03_SESIONES/SNN` |
| `Plantilla_Periodo/` | un dictado nuevo | `cp -a _PLANTILLAS/Plantilla_Periodo PERIODOS/<periodo>/course_NN_<slug>` |
| `Plantilla_Examen/` · `Plantilla_Practica/` · `Plantilla_Rubrica/` | documentos sueltos | copiar donde corresponda |

Ver `../LEEME_ESTANDAR.md` para el estándar completo.
