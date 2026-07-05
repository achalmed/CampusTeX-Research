# Redacción de Proyectos de Investigación Científica

## Presentación para Clase de 3 Horas

### 📋 Descripción

Presentación completa en Quarto (RevealJS) sobre redacción científica y académica, diseñada para una clase de 3 horas para estudiantes universitarios.

**Autor:** Edison Achalma  
**Institución:** Universidad Nacional de San Cristóbal de Huamanga  
**Fecha:** Enero 2026

---

## 🎯 Contenido de la Presentación

### Módulo 1: Fundamentos (45 min)
- ¿Qué es la escritura científica?
- Los 4 pilares: Precisión, Claridad, Brevedad, Formalidad
- Honestidad intelectual y plagio
- Géneros académicos: formación vs. expertos
- La monografía como entrenamiento

### Módulo 2: Estructura IMRyD (60 min)
- El formato IMRyD explicado
- Título atractivo
- Resumen (Abstract)
- Introducción y modelo CARS
- Métodos y Materiales
- Resultados objetivos
- Discusión interpretativa

### Descanso (15 min)

### Módulo 3: Proceso de Composición (45 min)
- Escribir vs. componer
- Precomposición (toma de conciencia, descubrimiento, investigación)
- Identificación del público
- Redacción efectiva
- Borradores sucesivos
- El párrafo como unidad de pensamiento

### Módulo 4: Herramientas Prácticas (45 min)
- Vocabulario preciso y propiedad léxica
- Conectores y metadiscurso
- Evitar clichés
- Puntuación correcta
- Legibilidad e índice de nebulosidad
- Interés humano
- Uso ético de la IA
- Lectura crítica

---

## 📦 Archivos Incluidos

```
📁 Presentación/
├── redaccion_investigacion_cientifica.qmd  (Archivo principal Quarto)
├── styles.css                               (Estilos CSS personalizados)
├── custom.scss                              (Tema SCSS para Quarto)
└── README.md                                (Este archivo)
```

---

## 🚀 Cómo Usar esta Presentación

### Requisitos Previos

1. **Instalar Quarto** (https://quarto.org/docs/get-started/)
   ```bash
   # Descargar desde: https://quarto.org/docs/download/
   ```

2. **Instalar RStudio o VS Code** (opcional pero recomendado)
   - RStudio: https://posit.co/download/rstudio-desktop/
   - VS Code: https://code.visualstudio.com/

### Renderizar la Presentación

#### Opción 1: Línea de comandos

```bash
# Navegar al directorio de la presentación
cd /ruta/a/la/presentacion

# Renderizar a HTML
quarto render redaccion_investigacion_cientifica.qmd

# O usar preview para ver en tiempo real
quarto preview redaccion_investigacion_cientifica.qmd
```

#### Opción 2: Desde RStudio

1. Abrir `redaccion_investigacion_cientifica.qmd` en RStudio
2. Hacer clic en el botón "Render" o presionar `Ctrl+Shift+K`
3. La presentación se abrirá automáticamente en el navegador

#### Opción 3: Desde VS Code

1. Instalar la extensión de Quarto para VS Code
2. Abrir el archivo .qmd
3. Presionar `Ctrl+Shift+K` o usar el comando "Quarto: Render"

### Resultado

Se generará un archivo HTML interactivo:
- `redaccion_investigacion_cientifica.html`

---

## 🎨 Características de la Presentación

### Diseño Visual
- ✅ Paleta de colores profesional y académica
- ✅ Tipografía legible (Georgia para títulos, Calibri para cuerpo)
- ✅ Layout responsive (se adapta a diferentes pantallas)
- ✅ Transiciones suaves entre diapositivas

### Funcionalidades Interactivas
- ✅ Navegación con flechas del teclado
- ✅ Pizarra integrada (presiona `C` para activar)
- ✅ Modo presentador (presiona `S`)
- ✅ Vista general (presiona `ESC`)
- ✅ Zoom (presiona `Alt + Click`)
- ✅ Búsqueda (presiona `Ctrl+Shift+F`)

### Contenido Estructurado
- ✅ 50+ diapositivas organizadas en 4 módulos
- ✅ Ejemplos prácticos y ejercicios
- ✅ Tablas comparativas
- ✅ Cajas de llamada (tips, advertencias, notas)
- ✅ Listas de verificación (checklist)
- ✅ Preguntas frecuentes
- ✅ Recursos bibliográficos

---

## 🎓 Modo Presentador

Para activar el modo presentador durante la clase:

1. **Abrir la presentación** en el navegador
2. **Presionar la tecla `S`**
3. Se abrirá una ventana adicional con:
   - Vista previa de la siguiente diapositiva
   - Notas del presentador
   - Temporizador
   - Contador de diapositivas

**Truco profesional:** Usa dos pantallas:
- Pantalla 1 (proyector): Presentación principal para estudiantes
- Pantalla 2 (laptop): Modo presentador para el docente

---

## ✏️ Personalización

### Cambiar Colores

Editar `custom.scss`:

```scss
$primary: #1E2761;    // Azul marino principal
$secondary: #2C5F2D;  // Verde bosque
$danger: #F96167;     // Coral/rojo para énfasis
```

### Añadir tu Logo

En el archivo .qmd, busca la línea `logo: ""` y añade la ruta:

```yaml
logo: "img/logo_universidad.png"
```

### Modificar Footer

Editar la línea `footer:` en el encabezado YAML:

```yaml
footer: "Tu Texto | Universidad | Fecha"
```

### Añadir Nuevas Diapositivas

Formato básico de una diapositiva:

```markdown
## Título de la Diapositiva

Contenido aquí...

---
```

Para columnas:

```markdown
:::: {.columns}
::: {.column width="50%"}
Contenido columna izquierda
:::

::: {.column width="50%"}
Contenido columna derecha
:::
::::
```

---

## 🔧 Solución de Problemas

### Problema: "Comando quarto no encontrado"

**Solución:** Asegúrate de que Quarto esté instalado y en tu PATH:
```bash
# Verificar instalación
quarto --version

# Si no está instalado, descargar de https://quarto.org
```

### Problema: "Los estilos no se aplican"

**Solución:** Verifica que `styles.css` y `custom.scss` estén en el mismo directorio que el archivo .qmd

### Problema: "No se ve el modo presentador"

**Solución:** Asegúrate de permitir pop-ups en tu navegador al presionar `S`

### Problema: "Las diapositivas se ven muy pequeñas/grandes"

**Solución:** Ajustar el zoom del navegador (`Ctrl + +` o `Ctrl + -`)

---

## 📚 Recursos Adicionales

### Documentación de Quarto
- Guía oficial: https://quarto.org/docs/presentations/revealjs/
- Ejemplos: https://quarto.org/docs/gallery/

### Atajos de Teclado en la Presentación

| Tecla | Función |
|-------|---------|
| `→` / `Space` | Siguiente diapositiva |
| `←` | Diapositiva anterior |
| `Home` | Primera diapositiva |
| `End` | Última diapositiva |
| `ESC` | Vista general (todas las diapositivas) |
| `S` | Modo presentador |
| `F` | Pantalla completa |
| `C` | Activar pizarra |
| `B` | Pantalla en negro |
| `?` | Ayuda de atajos |

---

## 📖 Estructura de la Clase Sugerida

### Hora 1 (Módulo 1 + inicio Módulo 2)
- **00-10 min:** Bienvenida y objetivos
- **10-30 min:** Fundamentos de escritura científica
- **30-45 min:** Los 4 pilares y ética
- **45-60 min:** Géneros académicos e introducción a IMRyD

### Hora 2 (Módulo 2 completo)
- **60-75 min:** Estructura IMRyD completa
- **75-90 min:** Título, abstract e introducción
- **90-105 min:** Métodos, resultados y discusión
- **105-120 min:** Ejercicio práctico de análisis

### Descanso (15 min)

### Hora 3 (Módulos 3 y 4)
- **135-160 min:** Proceso de composición y precomposición
- **160-180 min:** Herramientas de estilo prácticas
- **180-195 min:** Ejercicios y checklist final
- **195-210 min:** Preguntas, respuestas y cierre

---

## 🤝 Contribuciones y Mejoras

Si encuentras errores o tienes sugerencias para mejorar la presentación:

1. Documenta el cambio propuesto
2. Verifica que no rompa el formato
3. Prueba renderizando la presentación
4. Comparte tus mejoras con colegas

---

## 📄 Licencia

Esta presentación está diseñada con fines educativos. El contenido está basado en múltiples fuentes académicas reconocidas sobre redacción científica.

**Uso permitido:**
- ✅ Educación universitaria
- ✅ Talleres y seminarios académicos
- ✅ Modificación para adaptación local
- ✅ Compartir con atribución apropiada

**Uso NO permitido:**
- ❌ Venta comercial sin autorización
- ❌ Remoción de créditos al autor original
- ❌ Uso para fines no educativos

---

## 📧 Contacto

**Edison Achalma**  
Economista - Informático  
Universidad Nacional de San Cristóbal de Huamanga  

🌐 Enlaces:
- GitHub: https://github.com/achalmed
- LinkedIn: https://linkedin.com/in/achalmaedison
- X (Twitter): https://x.com/achalmaedison
- Bluesky: https://bsky.app/profile/achalmaedison.bsky.social

---

## ✅ Checklist Antes de Presentar

- [ ] Quarto instalado y funcionando
- [ ] Presentación renderizada correctamente
- [ ] Todos los archivos (CSS, SCSS) en el directorio
- [ ] Modo presentador probado (tecla `S`)
- [ ] Proyector/pantalla funcionando
- [ ] Backup de la presentación en USB o nube
- [ ] Ejemplos y ejercicios preparados
- [ ] Tiempo estimado revisado (3 horas)
- [ ] Material adicional impreso (opcional)
- [ ] Enlace para compartir la presentación con estudiantes

---

## 🎉 ¡Listo para Presentar!

Tu presentación está completamente lista. Solo necesitas:

1. Renderizar el archivo .qmd
2. Abrir el HTML resultante
3. Presionar `F` para pantalla completa
4. Presionar `S` para modo presentador
5. ¡Comenzar a enseñar!

**¡Éxito en tu clase!** 🎓📚🚀
