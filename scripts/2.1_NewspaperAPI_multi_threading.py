"""

Notas pa ordenar mi cabeza:
- Sacamos todas las noticias SIN el tiempo por web scrapping
- Añadimos las que son del tiempo para cada año (que usó FEDESARROLLO); bien formateadas y pegadas
    - Están todas por año
- Sacamos código que cree DTM por TF-IDF (ver todo el proceso)
    - Creamos IPEC para cada mes    
    - Clasificador(es) por sector
        - Falta etiquetar
    - Usar esa matriz pa sacar correlaciones con palabra (como "Petro", "gobierno", "ELN/FARC", cosas así)
- Análisis
    - Sacar datos históricos (mes si es posible para IPEC, año para total & por sector)
    - Contrastar con datos macro (ver informe FEDESAROLLO)
    - Preparar script para ambos videos

"""

import pandas as pd
import requests
import time
import random
from urllib.parse import urlparse
from newspaper import Article
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from threading import Semaphore

# -----------------------------
# Configuración (ajustable)
# -----------------------------
INPUT_CSV = "stores/gdelt_colombia_2023.csv"
OUTPUT_CSV = "stores/noticias_completas_2023.csv"
FAILED_CSV = "stores/noticias_fallidas_2023.csv"

MAX_WORKERS = 20              # el usuario puede poner 2; se respetará
REQUEST_TIMEOUT = 15          # segundos para requests.get
MAX_RETRIES = 2               # reintentos por intento de descarga
BACKOFF_BASE = 1.0            # segundos de backoff inicial

# Control de concurrencia por dominio: cuántas conexiones concurrentes permitimos por dominio.
# Algunos dominios sensibles (elespectador, eltiempo) se configuran con 1-2.
DEFAULT_DOMAIN_CONCURRENCY = 3
DOMAIN_OVERRIDES = {
    "www.elespectador.com": 1,
    "elespectador.com": 1,
    "www.eltiempo.com": 1,
    "eltiempo.com": 1,
    # agrega más si quieres
}

# Headers realistas
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# -----------------------------
# Helper: semáforos por dominio
# -----------------------------
_domain_semaphores = {}
def get_domain_semaphore(domain):
    if domain not in _domain_semaphores:
        limit = DOMAIN_OVERRIDES.get(domain, DEFAULT_DOMAIN_CONCURRENCY)
        _domain_semaphores[domain] = Semaphore(limit)
    return _domain_semaphores[domain]

# -----------------------------
# Función que extrae un solo artículo
# -----------------------------
def extraer_texto_indexed(idx, url, session):
    """
    Intenta descargar y parsear el artículo en 'url'.
    Devuelve (idx, texto, ok_bool, mensaje_error)
    """
    row_number = idx + 1  # para mostrar 1-based
    print(f"Descargo artículo #{row_number}: {url}")

    domain = urlparse(url).netloc
    sem = get_domain_semaphore(domain)

    for intento in range(1, MAX_RETRIES + 1):
        try:
            # controlar concurrencia por dominio
            sem.acquire()
            # Hacer petición HTTP con session + headers
            resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            status = resp.status_code
            html = resp.text
            sem.release()

            if status == 429:
                # Rate limited: backoff y reintento
                wait = BACKOFF_BASE * (2 ** (intento - 1)) + random.random()
                print(f"[429] {url} - intento {intento}/{MAX_RETRIES}. Esperando {wait:.1f}s")
                time.sleep(wait)
                continue

            if status >= 400:
                # errores 4xx/5xx
                wait = 1 + intento * 0.5
                print(f"[HTTP {status}] {url} - intento {intento}/{MAX_RETRIES}. Esperando {wait:.1f}s")
                time.sleep(wait)
                continue

            # Tenemos HTML: pasarlo a newspaper para parsear (evita que newspaper haga otra request)
            article = Article(url, language="es")
            # Article.download permite input_html
            article.download(input_html=html)
            article.parse()
            texto = article.text.replace("\n", " ").replace("  ", " ")
            # eliminación de strings comunes si lo deseas
            texto = texto.replace(
                "Ingrese o regístrese acá para guardar los artículos en su zona de usuario y leerlos cuando quiera", ""
            )

            # éxito
            return idx, texto, True, ""

        except requests.exceptions.RequestException as re:
            # errores de red
            try:
                sem.release()
            except:
                pass
            wait = BACKOFF_BASE * (2 ** (intento - 1)) + random.random()
            print(f"[ReqErr] {url} - intento {intento}/{MAX_RETRIES} -> {re}. Esperando {wait:.1f}s")
            time.sleep(wait)
            continue
        except Exception as e:
            try:
                sem.release()
            except:
                pass
            # puede ser parse error; reintentar un par de veces
            wait = 0.5 + intento * 0.5
            print(f"[ParseErr] {url} - intento {intento}/{MAX_RETRIES} -> {e}. Esperando {wait:.1f}s")
            time.sleep(wait)
            continue

    # si llegamos acá, falló totalmente
    print(f"[FALLÓ] artículo #{row_number}: {url}")
    return idx, "", False, "max_retries_exceeded"

# -----------------------------
# Main: leer CSV y procesar en paralelo
# -----------------------------
def main():
    # carga
    df = pd.read_csv(INPUT_CSV)
    # si hay una columna lateral inútil como la tuya, la quitamos si existen >2 columnas
    if df.shape[1] > 2:
        df = df.drop(columns=[df.columns[1]])
    df.columns = ['url', 'fecha', 'titulo'] if df.shape[1] == 3 else df.columns

    urls = df["url"].tolist()
    n = len(urls)
    resultados = ["" for _ in range(n)]
    failed = []

    # Usar una sesión requests por worker para keep-alive
    session = requests.Session()

    print(f"Proceso iniciado: {n} URLs. Usando {MAX_WORKERS} workers (hilos).")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futuros = {executor.submit(extraer_texto_indexed, i, url, session): i for i, url in enumerate(urls)}

        for fut in as_completed(futuros):
            i = futuros[fut]
            try:
                idx, texto, ok, msg = fut.result()
                if ok:
                    resultados[idx] = texto
                else:
                    resultados[idx] = ""
                    failed.append((idx, urls[idx], msg))
            except Exception as e:
                # fallo inesperado
                print(f"[EXCEPCIÓN] fila {i+1} -> {e}")
                resultados[i] = ""
                failed.append((i, urls[i], "exception"))

    # guardar resultados parciales
    df["texto"] = resultados
    df.to_csv(OUTPUT_CSV, index=False, sep="~")
    print(f"Primera pasada completada. Guardado parcial en '{OUTPUT_CSV}'.")

    # Reintentar fallidos, pero secuencialmente (más amigable)
    if failed:
        print(f"Reintentando {len(failed)} artículos fallidos, uno por uno (modo secuencial).")
        failed_second_round = []
        # usar una sesión nueva para la fase secuencial
        session2 = requests.Session()
        for idx, url, why in failed:
            # pequeño delay entre cada reintento para no sobrecargar
            time.sleep(0.5 + random.random() * 0.5)
            _, texto, ok, msg = extraer_texto_indexed(idx, url, session2)
            if ok:
                resultados[idx] = texto
            else:
                failed_second_round.append((idx, url, msg))

        # sobrescribir datos con los nuevos resultados
        df["texto"] = resultados
        df.to_csv(OUTPUT_CSV, index=False, sep="~")
        print(f"Segunda pasada completada. Archivo final guardado en '{OUTPUT_CSV}'.")

        # guardar fallidos finales
        if failed_second_round:
            failed_df = pd.DataFrame(failed_second_round, columns=["index", "url", "error"])
            failed_df.to_csv(FAILED_CSV, index=False)
            print(f"Se guardaron {len(failed_second_round)} URLs fallidas en '{FAILED_CSV}'.")
        else:
            print("Todos los artículos se descargaron con éxito en la segunda pasada.")
    else:
        print("Todos los artículos se descargaron con éxito en la primera pasada.")

if __name__ == "__main__":
    main()
