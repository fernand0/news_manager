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

## 🔧 **Ventajas de las Mejoras**

✅ **Flexibilidad**: Puedes usar archivos en cualquier ubicación  
✅ **Configurabilidad**: Variable de entorno para archivo por defecto  
✅ **Validación**: Verifica que el archivo existe y es legible  
✅ **Manejo de errores**: Mensajes claros y útiles  
✅ **Compatibilidad**: Mantiene el comportamiento original  
✅ **UTF-8**: Soporte completo para caracteres especiales 