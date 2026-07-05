# assets/

Recursos visuales compartidos del curso.

- `branding/cau-logo.png` — logo institucional canónico. `new-session.sh`
  copia este archivo junto a las diapositivas de cada sesión nueva para
  que cada deck sea autocontenido (los `.tex` lo referencian en su propio
  directorio).

Si cambias el logo, actualiza este archivo y la clave `logo:` de
`config/course.yml`; las sesiones ya existentes conservan su copia local.
