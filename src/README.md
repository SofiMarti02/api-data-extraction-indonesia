Script en Python para extraer datos de exportaciones desde una API externa, procesar respuestas en formato JSON y generar archivos estructurados en Excel para análisis.

## Funcionalidades
- Consulta de datos por bloques de códigos HS
- Manejo básico de errores y reintentos
- Transformación de respuestas JSON a DataFrame
- Limpieza y estandarización de datos
- Exportación de resultados a Excel

## Tecnologías
- Python
- requests
- pandas
- openpyxl

## Flujo del proceso
1. Lectura de códigos HS desde un archivo Excel
2. Consulta a API externa por bloques
3. Normalización de datos
4. Limpieza y transformación de variables
5. Generación de archivos Excel de salida

## Uso
1. Ajustar las rutas de entrada y salida en el script
2. Reemplazar el valor de API por la clave correspondiente
3. Ejecutar el archivo `main.py`

## Nota
La API key no está incluida por seguridad.
