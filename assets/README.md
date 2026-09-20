---
tipo: readme
estado: activo
---
# assets/ — los recursos visuales compartidos del framework

Una sola pieza hoy: el logo institucional canónico.

## Uso

```bash
ls assets/branding/cau-logo.png                       # el logo canónico vive aquí
cp assets/branding/cau-logo.png <carpeta del deck>/   # un deck heredado lo espera como hermano del .tex
```

Los decks nuevos no necesitan el `cp`: `new-session.sh` y `new-presentation.sh` copian el logo junto a
las diapositivas para que cada deck sea autocontenido. La clave `logo:` de `config/course.yml` apunta
a este archivo; si cambia el logo, se cambian los dos y las sesiones ya creadas conservan su copia.

## Estructura

| Ruta | Qué es | Dueño |
|---|---|---|
| `branding/cau-logo.png` | el logo institucional canónico (343 KB) | el autor |

## Límite honesto

- **El logo está aquí, pero falta donde hace falta.** Los decks Beamer referencian el logo como
  **hermano del `.tex`**, no esta ruta. Hoy nueve documentos de `docencia/` lo citan y solo dos tienen
  su copia local: **cinco decks heredados no compilan por eso** (uno, además, declara
  `%!TEX program = xelatex`). Remedio al reconstruirlos: copiar `assets/branding/cau-logo.png` a la
  carpeta del deck. Es pendiente del docente, no del framework.
- **Al mover una sesión hay que mover su carpeta completa**: los assets son hermanos del `.tex`.
- **Aquí no viven las fotografías ni los kits de vídeo** del ecosistema (`~/Pictures`, `~/Videos`) ni
  el sistema de diseño (`sistema-editorial`, `identidad_visual`).
