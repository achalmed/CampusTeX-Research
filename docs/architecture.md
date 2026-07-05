# Arquitectura del framework

## Principio central

**La sesión es la unidad atómica del curso.** Todo lo necesario para
preparar, impartir, evaluar y mejorar una clase vive en una sola carpeta
`course/sessions/session_NN_slug/` con estructura idéntica en todas las
sesiones. Una sesión se puede repasar, compartir (basta comprimir la
carpeta) o clonar como base de otra clase sin depender de archivos externos.

## Capas

```
┌─────────────────────────────────────────────────┐
│ config/course.yml — identidad del curso          │  configuración
├─────────────────────────────────────────────────┤
│ templates/ — plantillas parametrizadas           │  reutilización
├─────────────────────────────────────────────────┤
│ scripts/ — new/build/validate/clean/stats/doctor │  automatización
├─────────────────────────────────────────────────┤
│ course/ — contenido real del curso               │  contenido
│   syllabus · calendar · evaluation · policies    │
│   topics · sessions/session_NN_*/                │
└─────────────────────────────────────────────────┘
```

- Los **scripts nunca contienen datos del curso**: los leen de
  `config/course.yml` (parser de YAML plano en `scripts/lib/common.sh`).
- Las **plantillas usan placeholders** `{{ASI}}` que `new-session.sh`
  sustituye con `sed`.
- El **contenido no depende de los scripts**: cada deck LaTeX es
  autocontenido (preambulo propio + copia local del logo) y compila con
  cualquier herramienta estándar.

## Anatomía de una sesión

```
session_NN_slug/
├── README.md            ← qué hay aquí y cómo compilar
├── metadata.yml         ← ficha técnica (fuente única de datos)
├── slides/              ← fuente (.tex o .qmd) + PDF + imágenes
├── teaching/
│   ├── lesson_plan.md   ← objetivos, competencias, secuencia con tiempos
│   ├── teacher_notes.md ← guion hablado diapositiva por diapositiva
│   └── retrospective.md ← memoria post-clase (gestión del conocimiento)
├── practice/            ← material práctico del estudiante
├── evaluation/          ← quiz, rúbricas, listas de cotejo
├── homework/            ← trabajo domiciliario
├── resources/
│   ├── links.md         ← videos, webs, papers
│   └── readings/        ← lecturas (PDF)
└── archive/             ← versiones antiguas, material descartado
```

## Decisiones de diseño

1. **LaTeX Beamer como estándar; Quarto solo en la sesión 4.** El curso ya
   impartido es mayoritariamente LaTeX y se mantiene así. La sesión 4 nació
   en Quarto y convertirla no aporta valor: queda como excepción documentada
   y `build-session.sh` la detecta automáticamente (`.qmd` → `quarto render`).
2. **Decks autocontenidos, sin preámbulo compartido.** Se evaluó extraer un
   `core/` con preámbulo común, pero refactorizar clases ya impartidas
   introduce riesgo sin beneficio. La consistencia de estilo para sesiones
   futuras la da `templates/session/slides.tex`. (Por eso no existe `core/`.)
3. **Logo duplicado por sesión, canónico en `assets/branding/`.** Los `.tex`
   referencian `cau-logo.png` en su propio directorio: portabilidad gana a DRY
   en este caso. La copia canónica sirve de fuente para sesiones nuevas.
4. **PDFs versionados.** Son entregables del curso; se conservan en git para
   poder repasar/compartir sin recompilar.
5. **Nombres de carpeta sin espacios ni tildes** (`session_03_busqueda_de_informacion`),
   para que el scripting sea fiable. Los archivos históricos internos (p. ej.
   `05 citas/`) conservan su nombre para no romper rutas relativas de LaTeX.
6. **Historial preservado.** La migración se hizo con `git mv`.

## Compatibilidad

- Compilación preferente vía el compilador universal del workspace
  (`scripts_for_latex/script_compilar_latex/main.sh`, autodetección de motor);
  si no está, `build-session.sh` usa el motor detectado por comentario
  mágico `%!TEX`, clase `yaac-*` o presencia de `fontspec`.
- Motores requeridos: syllabus → lualatex · sesión 1 → xelatex ·
  topics/policies → xe/lualatex (fontspec) · resto → pdflatex.
