
import requests
import pandas as pd
import time
import io
from urllib.parse import quote
from datetime import datetime, timedelta


""" EXPLICACIÓN CÓDIGO 1era PARTE

Gdelt es una base de datos pública de noticias y eventos globales. Los datos obtenidos fueron a partir de queries a la API 
de Gdelt, que permite filtrar por temas, dominios, fechas, entre otros.

Los PARÁMETROS FIJOS se son constantes entre todas las queries, pues solo buscamos artículos de noticias en español y originarias 
en Colombia; evidente en la estructura de la query que no cambia.

Los PARÁMETROS CONFIGURABLES son el tema, el dominio (url de un periódico, como "elespectador.com) y el rango de fechas; se 
editaron para obtener una buena cantidad de noticias de diferentes medios, manteniendo el propósito de la investigación. Se 
justifica abajo el criterio de la selección de las variables de los parámetros; cabe mencionar que en todos hubo una consideración 
computacional, pues aumentar variables aumentaba considerablemente el tiempo de ejecución, por lo cual se decidio acotar.

- Dominio: se seleccionaron medios colombianos que fueran influyentes en el país. Algunos no pudieron obteneres (resalta la ausencia de caracol),
        pero los presentes son igualmente relevantes y suficientes para el propósito del trabajo.
- Fechas: se seleccionaron fechas de 2024, pues son noticias suficientemente recientes para ser relevantes, pero suficientemente antiguas 
        para poder obtener sus datos (noticias muy recientes requieren subscripciones o están muy protegidas)
        
También mencionar que las iteraciones se hacen porque la API retorma máximo 250 registros por query, entonces rangos de muy grandes podían 
dejar muchas noticias importantes fuera; por ejemplo, no se pide todo un año, o todo un tema.
        
Finalmente mencionar 2 detalles. Primero, se puede demorar en cargar porque se establce un delay de 1 segundos entre cada query para evitar 
error 429 (demasiadas peticiones), y segundo, se busca no repetir noticias, por ende se compara el URL de  las noticias obtenidas con las ya vistas,
antes de guardarlas, así solo se guardan nuevas, lo que también demora la ejecución.

"""

# Parámetros configurables

#elcolombiano.com, wradio.com, vanguardia.com ; añadibles, pero no generan muchas noticias nuevas para el periodo, y si agregan capacidad computacional
domain = ['eltiempo.com', 'elespectador.com', 'noticiasrcn.com', 'semana.com', 'pulzo.com', 'larepublica.co', 'lasillavacia.com'] 

# Emparejamos inicio con final de mes; formato YYYYMMDDHHMMSS
start = ['20240101000000', '20240201000000', '20240301000000', '20240401000000', '20240501000000', '20240601000000', '20240701000000', '20240801000000', '20240901000000', '20241001000000', '20241101000000', '20241201000000'] 
end = ['20240103000000', '20240228000000', '20240330000000', '20240430000000', '20240530000000', '20240630000000', '20240703000000', '20240830000000', '20240930000000', '20241030000000', '20241130000000', '20241230000000'] 


# Variables internas
base_url = 'https://api.gdeltproject.org/api/v2/doc/doc'
seen_urls = set()  # para evitar duplicados|
all_data = []

output_csv = 'stores/gdelt_colombia_2024.csv' # Archivo final de esta parte


# Ejemplo uso para 2022 (colombia, noticiero "pulzo.com", en español, entre enero 1 - diciembre 30)
# https://api.gdeltproject.org/api/v2/doc/doc?query=colombia AND domain:pulzo.com AND sourcelang:spanish AND sourcecountry:colombia&startdatetime=20220101000000&enddatetime=20221230000000&mode=ArtList&format=html&maxrecords=250


# Función que construye la URL para la query
def construir_url(domain, start, end):
    a = f"{base_url}?query=colombia AND domain:{domain} AND sourcelang:spanish AND sourcecountry:colombia&startdatetime={start}&enddatetime={end}&mode=ArtList&format=csv&maxrecords=250"
    print(f"URL construida: {a}")
    return a

# Función que extrae datos y los guarda en CSV
def extraer_y_guardar(domain, start, end):
    global all_data

    url = construir_url(domain, start, end)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 429:
            print("Demasiadas peticiones, esperando 60 segundos...")
            time.sleep(60)
            return
        elif r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            return

        df = pd.read_csv(io.StringIO(r.text))
        nuevos = df[~df['URL'].isin(seen_urls)]
        print(f"{len(nuevos)} noticias nuevas")

        seen_urls.update(nuevos['URL'])
        all_data.append(nuevos)

        # Guardar al CSV de forma acumulativa
        if not nuevos.empty:
            nuevos.to_csv(output_csv, mode='a', index=False, header=not pd.io.common.file_exists(output_csv))

    except Exception as e:
        print("Error al procesar:", e)
        

# Bucle para iterar sobre los parámetros
for j in range(len(domain)):
    for k in range(len(start)):
        # Se imprime la iteración para mostrar el progreso de las queries
        print(f"\n Iteración {domain[j]}, {start[k]}, {end[k]}")
        
        # Ajustar el rango de fechas dinámicamente
        extraer_y_guardar(domain[j], start[k], end[k])
        time.sleep(1)  # Esperar 1 segundo entre peticiones para evitar errores de límite



# Unir todo en un dataframe (esto es para revisión, el CSV ya se guardó antes)
if all_data:
    full_df = pd.concat(all_data, ignore_index=True)
    print(f"\n Total artículos únicos obtenidos: {len(full_df)}")
else:
    print("\n No se obtuvo ningún dato.")



