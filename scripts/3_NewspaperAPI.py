
import pandas as pd
from newspaper import Article, news_pool


""" EXPLICACIÓN CODIGO 3era PARTE

Ya tenemos los urls de los artículos para analizar. Ahora usamos la API newspaper para extraer el texto de cada 
uno según su URL. Se mantienen solo los primeros 2000 caracteres, pues es una parte representativa del texto 
(especialmente la introducción, que resume el contenido y la posición del autor), y cargar más tiene un costo 
computacional alto para el modelo de análisis posterior.

También nos dimos cuenta que la API extrae la mayor parte correctamente, pero a veces copia publicidad o propaganda,
por lo cual se hace un filtro adicional al texto para eliminar estos casos. Se agregaran 200 caracteres a los 2000
originales considerando aquellos que se eliminarán.

*NOTA: recomendado usar el código de prueba para verificar el funcionamiento. El completo tardó 16 horas.

"""

# Cargar el CSV exportado de GDELT
df = pd.read_csv("stores/gdelt_colombia_2024.csv") 

# Quitar segunda columna inútil
df = df.drop(columns=[df.columns[1]])

# Ponerle titulo a las columnas del df
df.columns = ['url', 'fecha', 'titulo']

print(f"columnas del df: {df.columns}")

# Extraer contenido de cada URL
def extraer_texto(url):
    try:
        articulo = Article(url, language='es')
        print("Descargando:", url) # esta línea es para ver el progreso, puede quitarse si es incómodo
        articulo.download()
        articulo.parse()
        
        # eliminar saltos de página 
        articulo.text = articulo.text.replace("\n", " ")
        # eliminar espacios dobles
        articulo.text = articulo.text.replace("  ", " ")
        # quitar promoción ElTiempo
        articulo.text = articulo.text.replace("Ingrese o regístrese acá para guardar los artículos en su zona de usuario y leerlos cuando quiera", "")
        
        
        return articulo.text
    except:
        print("Error al procesar la URL:", url)
        return ""

# Aplicarlo a todas las URLs
df["texto"] = df["url"].apply(extraer_texto)

# Guardar resultado
df.to_csv("stores/noticias_completas_2024.csv", index=False, sep='~')
print("Artículos listos. Guardado en: 'stores/noticias_completas_2024.csv'")


""" PRUEBA (esto se usó para probar que el código funcionara antes de aplicarlo a todas las noticias)

    # Tomar solo primeros 10 artículos
    df_prueba = df.head(10)
    
    # Extraer contenido de cada URL en el DataFrame de prueba
    df_prueba["texto"] = df_prueba["url"].apply(extraer_texto)

    # Guardar el resultado de prueba en un archivo separado
    df_prueba.to_csv("../stores/gdelt_con_texto_prueba.csv", index=False)

    print("Prueba completada. Resultado guardado en '../stores/gdelt_con_texto_prueba.csv'")
    
"""



