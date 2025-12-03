
import csv
import sys


""" EXPLICACIÓN CÓDIGO 2nda PARTE

El índice del IPEC considera diferentes criterios para filtrar las noticias, específicamente por la presencia de 
palabras clave. Por un tema computacional, y habiendo revisado las noticias extraídas, sabemos que muchas noticias no 
son relevantes para el índice dada la temática (fútbol, televisión, cultura, entre otros). 

En lugar de tomar todos los URL, extraer el fragmento cada noticia, para después ver que la noticia claramente
no es de economía ni política, podemos hacer un filtro sencillo por la URL y título. Extraemos patrones concurrentes 
en noticias de índole no deseada, ahorrando así tiempo y recursos.

*NOTA: este código se separa de la parte 1 para poder limpiar los datos sin necesidad de cargarlos todos otra vez. 

"""

# Configurar la salida estándar para usar UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Archivo de entrada y salida
input_csv = '../stores/gdelt_colombia_2024.csv'
output_csv = '../stores/gdelt_colombia_filtrado.csv'

# Palabras clave para filtrar
keywords = ["deportes", "entretenimiento", "tendencias", "bocas", "estilo de vida", "vivir-bien/", "gente/", "/ocio"]


contador = 0
# Abrir el archivo de entrada y salida
with open(input_csv, mode='r', encoding='utf-8') as infile, open(output_csv, mode='w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Leer y escribir el encabezado, es decir, nombres de las columnas (sin la columna 1, pues URL repetido)
    header = next(reader)
    writer.writerow([col for i, col in enumerate(header) if i != 1]) 
    
    # Datos vienen en formato "URL, URL, FECHA, TITULO"

    # Procesar cada fila
    for row in reader:
        url = row[0]  # Columna 0: URL
        title = row[3]  # Columna 3: Título

        # Verificar si la fila contiene alguna palabra clave
        url_matches = [keyword for keyword in keywords if keyword.lower() in url.lower()]
        title_matches = [keyword for keyword in keywords if keyword.lower() in title.lower()]

        if url_matches or title_matches:
            print(f"Eliminando fila: {repr(row)}")  # Usar repr para evitar problemas de Unicode
            print(f"Coincidencias en URL: {url_matches}")
            print(f"Coincidencias en Título: {title_matches}")
            contador += 1
        else:
            # Escribir la fila filtrada (sin la columna 1; URL repetido)
            writer.writerow([col for i, col in enumerate(row) if i != 1])

print(f"Archivo filtrado guardado en: {output_csv}")
print(f"Total de filas eliminadas: {contador}")
