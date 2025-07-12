# Ejemplos de Uso - News Manager

## 🎯 **Nuevas Funcionalidades de Manejo de Archivos**

### 1. **Uso Básico (Archivo por Defecto)**

```bash
# Crear archivo de entrada
echo "El Dr. María González ha descubierto una nueva técnica de reciclaje de plásticos." > /tmp/noticia.txt

# Generar noticia
news-manager generate
```

### 2. **Especificar Archivo Directamente**

```bash
# Crear archivo en cualquier ubicación
echo "Nueva tecnología solar revoluciona la energía renovable." > ./mi_noticia.txt

# Usar el archivo específico
news-manager generate --input-file ./mi_noticia.txt
# o con la forma corta
news-manager generate -i ./mi_noticia.txt
```

### 3. **Configurar Archivo por Defecto con Variable de Entorno**

```bash
# En tu archivo .env
NEWS_INPUT_FILE="/home/usuario/noticias/entrada.txt"

# O en tu shell
export NEWS_INPUT_FILE="/home/usuario/noticias/entrada.txt"

# Ahora puedes usar simplemente
news-manager generate
```

### 4. **Manejo de Errores Mejorado**

El sistema ahora detecta y reporta errores específicos:

```bash
# Archivo no existe
news-manager generate -i archivo_inexistente.txt
# Error: El archivo no existe: archivo_inexistente.txt
# Sugerencia: Crea el archivo con tu texto fuente o especifica otro archivo con --input-file

# Archivo vacío
echo "" > archivo_vacio.txt
news-manager generate -i archivo_vacio.txt
# Error: El archivo archivo_vacio.txt está vacío.

# Sin permisos
chmod 000 archivo_sin_permisos.txt
news-manager generate -i archivo_sin_permisos.txt
# Error: No tienes permisos para leer el archivo archivo_sin_permisos.txt
```

### 5. **Orden de Prioridad**

El sistema busca el archivo de entrada en este orden:

1. **Parámetro `--input-file`** (máxima prioridad)
2. **Variable de entorno `NEWS_INPUT_FILE`**
3. **Archivo por defecto `/tmp/noticia.txt`**

### 6. **Ejemplos Prácticos**

```bash
# Trabajar con múltiples archivos
news-manager generate -i noticia1.txt
news-manager generate -i noticia2.txt
news-manager generate -i noticia3.txt

# Usar archivos en diferentes directorios
news-manager generate -i /home/usuario/noticias/ciencia.txt
news-manager generate -i /tmp/noticias/tecnologia.txt
news-manager generate -i ./proyectos/noticia_local.txt

# Configurar un directorio de trabajo
export NEWS_INPUT_FILE="/home/usuario/noticias/entrada.txt"
news-manager generate  # Usa automáticamente el archivo configurado
```

### 7. **Ayuda del Comando**

```bash
# Ver todas las opciones disponibles
news-manager generate --help

# Ver ayuda general
news-manager --help
```

## 🎯 **Nueva Funcionalidad: Instrucciones Personalizadas**

### 8. **Uso de `--prompt-extra`**

La opción `--prompt-extra` te permite añadir instrucciones específicas para personalizar la generación de noticias:

```bash
# Centrarse en una persona específica
news-manager generate --url "https://ejemplo.com/noticia" --prompt-extra "céntrate en María Santos e ignora el resto"

# Enfocar en un aspecto particular
news-manager generate -i noticia.txt --prompt-extra "enfócate solo en los aspectos tecnológicos"

# Cambiar el tono de la noticia
news-manager generate --url "https://ejemplo.com" --prompt-extra "usa un tono más formal y académico"

# Enfatizar ciertos elementos
news-manager generate -i noticia.txt --prompt-extra "destaca especialmente los logros y premios obtenidos"

# Ignorar cierta información
news-manager generate --url "https://ejemplo.com" --prompt-extra "ignora los detalles técnicos y céntrate en el impacto social"

# Modo interactivo (se te preguntará qué instrucciones quieres)
news-manager generate --url "https://ejemplo.com" --interactive-prompt
```

**Ejemplo de sesión interactiva:**
```bash
$ news-manager generate --url "https://ejemplo.com" --interactive-prompt

--- Instrucciones adicionales ---
Ejemplos de instrucciones que puedes usar:
• 'céntrate en María Santos e ignora el resto'
• 'enfócate solo en los aspectos tecnológicos'
• 'usa un tono más formal y académico'
• 'destaca especialmente los logros y premios obtenidos'
• 'ignora los detalles técnicos y céntrate en el impacto social'
• (deja vacío para no añadir instrucciones)

¿Qué instrucciones adicionales quieres añadir?: céntrate en los aspectos de investigación
```

### 9. **Casos de Uso Avanzados con `--prompt-extra`**

```bash
# Para noticias de investigación
news-manager generate --url "https://universidad.com/investigacion" --prompt-extra "enfócate en la metodología y los resultados principales"

# Para noticias de empresas
news-manager generate -i noticia_empresa.txt --prompt-extra "destaca el impacto económico y las oportunidades de empleo"

# Para noticias de tecnología
news-manager generate --url "https://tech.com/nueva-app" --prompt-extra "explica las ventajas para el usuario final de forma clara"

# Para noticias de salud
news-manager generate -i noticia_salud.txt --prompt-extra "enfócate en los beneficios para la salud pública y la prevención"
```

### 10. **Combinación de Opciones**

```bash
# URL + instrucciones personalizadas
news-manager generate --url "https://i3a.unizar.es/noticia" --prompt-extra "céntrate en los investigadores jóvenes y sus logros"

# Archivo + instrucciones personalizadas
news-manager generate -i ./noticia_local.txt --prompt-extra "usa un tono más cercano y local"

# URL + modo interactivo
news-manager generate --url "https://i3a.unizar.es/noticia" --interactive-prompt

# Ver todas las opciones disponibles
news-manager generate --help
```

### 11. **Funcionalidad de URLs en Enlaces**

Cuando uses la opción `--url`, la URL aparecerá automáticamente en la sección de enlaces de la noticia generada:

```bash
# La URL aparecerá en los enlaces
news-manager generate --url "https://ejemplo.com/noticia"

# Salida esperada:
# Enlaces:
# - https://ejemplo.com/noticia
```

Esto es especialmente útil para:
- Mantener referencia a la fuente original
- Facilitar el acceso a la noticia completa
- Cumplir con estándares de citación

## 🎯 **Nueva Funcionalidad: Directorio de Salida Configurable**

### 12. **Configurar Directorio de Salida Permanente**

Puedes configurar un directorio por defecto para guardar automáticamente los archivos generados:

```bash
# En tu archivo .env
NEWS_OUTPUT_DIR="/home/usuario/noticias/generadas"

# O en tu shell
export NEWS_OUTPUT_DIR="/home/usuario/noticias/generadas"

# Ahora los archivos se guardarán automáticamente
news-manager generate --url "https://ejemplo.com/noticia"
# Los archivos se guardarán en /home/usuario/noticias/generadas/
```

### 13. **Especificar Directorio de Salida Manualmente**

```bash
# Directorio específico para esta ejecución
news-manager generate --url "https://ejemplo.com/noticia" --output-dir ./mis_noticias

# Crear directorio si no existe
news-manager generate -i noticia.txt --output-dir ./nuevas_noticias
```

### 14. **Formato de Archivos Guardados**

Los archivos se guardan con un formato estructurado y legible:

**Archivo de noticia** (`2025-07-14-nombre-slug.txt`):
```
Título: Investigadores españoles desarrollan nueva técnica de purificación de agua

Texto: El Dr. Carlos Ruiz y la Dra. Ana Martínez, del Instituto de Tecnología de Madrid, han desarrollado una innovadora técnica de purificación de agua utilizando nanopartículas magnéticas...

Enlaces:
- https://www.nature.com/ (Ejemplo, reemplazar con link real si existe)
- https://www.mit.es/ (Ejemplo, reemplazar con link al Instituto de Tecnología de Madrid)
```

**Archivo de Bluesky** (`2025-07-14-nombre-slug_blsky.txt`):
```
Innovación en purificación de agua! Los Drs. Ruiz & Martínez (Instituto de Tecnología de Madrid) desarrollan técnica con nanopartículas magnéticas, publicada en Nature. #AguaPotable #Nanotecnología #Innovación #CienciaEspañola [enlace a la noticia]
```

### 15. **Nomenclatura de Archivos**

Los archivos se nombran automáticamente con:
- **Fecha**: Siguiente día laborable (YYYY-MM-DD)
- **Slug**: Palabras clave del título + nombres de protagonistas
- **Extensión**: `.txt` para noticias, `_blsky.txt` para posts de Bluesky

**Ejemplos de nombres de archivo:**
```
2025-07-14-Carlos-Ana-investigadores-espanoles.txt
2025-07-14-Carlos-Ana-investigadores-espanoles_blsky.txt
2025-07-14-Maria-Gonzalez-nueva-tecnologia.txt
2025-07-14-Maria-Gonzalez-nueva-tecnologia_blsky.txt
```

### 16. **Casos de Uso del Directorio de Salida**

```bash
# Configurar directorio de trabajo
export NEWS_OUTPUT_DIR="/home/usuario/proyectos/noticias"

# Generar múltiples noticias
news-manager generate --url "https://noticia1.com" --prompt-extra "céntrate en los aspectos científicos"
news-manager generate --url "https://noticia2.com" --prompt-extra "enfócate en el impacto social"
news-manager generate --url "https://noticia3.com" --prompt-extra "destaca los logros obtenidos"

# Todos los archivos se guardarán en /home/usuario/proyectos/noticias/
```

### 17. **Formato de Enlaces Simplificado**

Los enlaces ahora aparecen como URLs directas, sin formato markdown:

```bash
# Antes (formato markdown):
# - [Enlace a la publicación en Nature]

# Ahora (formato directo):
# - https://www.nature.com/ (Ejemplo, reemplazar con link real si existe)
```

Esto facilita:
- Copiar y pegar URLs directamente
- Leer los enlaces de forma más clara
- Mantener un formato consistente en archivos guardados

## 🔧 **Ventajas de las Mejoras**

✅ **Flexibilidad**: Puedes usar archivos en cualquier ubicación  
✅ **Configurabilidad**: Variable de entorno para archivo por defecto  
✅ **Validación**: Verifica que el archivo existe y es legible  
✅ **Manejo de errores**: Mensajes claros y útiles  
✅ **Compatibilidad**: Mantiene el comportamiento original  
✅ **UTF-8**: Soporte completo para caracteres especiales  
✅ **Personalización**: Instrucciones adicionales con `--prompt-extra`  
✅ **Modo interactivo**: `--interactive-prompt` para instrucciones dinámicas  
✅ **Extracción inteligente**: Descarga y parsing automático de URLs  
✅ **Exclusividad**: Opciones claras y sin conflictos  
✅ **Directorio de salida configurable**: Variable `NEWS_OUTPUT_DIR` para guardar archivos automáticamente  
✅ **Formato de enlaces limpio**: URLs directas sin formato markdown  
✅ **Archivos estructurados**: Etiquetas explícitas "Título:", "Texto:", "Enlaces:" en archivos guardados