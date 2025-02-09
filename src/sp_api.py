# Importamos las librerías que necesitamos

# Tratamiento de datos
# -----------------------------------------------------------------------
import pandas as pd
import numpy as np

# Manejo del sistema
# -----------------------------------------------------------------------
import sys
sys.path.append("../")  # Agregamos el directorio principal al sistema de rutas


# Uso de API's
# -----------------------------------------------------------------------
import requests

# Para trabajar con archivos dotenv y los tokens
# -----------------------------------------------------------------------
import os
from dotenv import load_dotenv
load_dotenv()
  
# Obtenemos la API key desde las variables de entorno
api_key = os.getenv("API_KEY")
api_key_2 = os.getenv("API_KEY_2")


def buscar_genero_api():
    """
    Obtiene la lista de géneros de películas desde la API de Movies Database.

    Retorna:
        dict: Un diccionario con la respuesta en formato JSON que contiene los géneros disponibles.
    """

    url = "https://moviesdatabase.p.rapidapi.com/titles/utils/genres"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "moviesdatabase.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    print(response)

    return response.json()







def buscar_peliculas (genero, ano, pagina):
    """
    Busca películas en la API de Movies Database según el género, año y página especificados.

    Parámetros:
        genero (str): El género de las películas a buscar.
        ano (int): El año de lanzamiento de las películas.
        pagina (int): El número de página de los resultados.

    Retorna:
        dict: Un diccionario con la respuesta en formato JSON que contiene las películas encontradas.
    """

    url = "https://moviesdatabase.p.rapidapi.com/titles"

    querystring = {"genre":genero,"year":ano,"page":pagina,"limit":"50"}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "moviesdatabase.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()




def obtener_datos (dicc_peliculas):
    """
    Procesa un diccionario de películas y extrae información relevante para crear un DataFrame.

    Parámetros:
        dicc_peliculas (dict): Un diccionario que contiene los géneros como claves y listas de resultados de películas como valores.

    Retorna:
        pd.DataFrame: Un DataFrame con las columnas 'id', 'title', 'type', 'genre' y 'year', representando las películas y su información.
    """

    todas_pelis = {}
    for genero in dicc_peliculas.keys():
        for llamada in dicc_peliculas[genero]:
            try:
                for pelicula in llamada['results']:
                    lista_peli=[]
                    lista_peli.append(pelicula['id'])
                    lista_peli.append(pelicula['titleText']['text']) #Titulo
                    lista_peli.append(pelicula['titleType']['text']) #Type
                    lista_peli.append(genero)#Genero
                    lista_peli.append(pelicula['releaseYear']['year'])#año
                    lista_peli.append(pelicula['primaryImage']['url'])
                    todas_pelis[pelicula['id']] = lista_peli
            except:
                pass

    df = pd.DataFrame(todas_pelis).T
    df.rename(columns={0:'id', 1:'title', 2: 'type', 3: 'genre', 4: 'year', 5:'poster'}, inplace=True)
    return df


def buscar_genero (df):
    """
    Agrupa los géneros de las películas en un diccionario, donde la clave es el identificador de la película
    y el valor es una lista de géneros asociados a esa película.

    Parámetros:
        df (pd.DataFrame): Un DataFrame que contiene la información de las películas, con una columna de 'id' 
                           y una columna de 'genre'.

    Retorna:
        dict: Un diccionario donde las claves son los identificadores de las películas y los valores son listas 
              de géneros asociados a cada película.
    """
    dicc_generos = {}
    for i in range(df.shape[0]):
        if df.iloc[i,0] in dicc_generos:
            dicc_generos[df.iloc[i,0]].append(df.iloc[i,3])
        else:
            dicc_generos[df.iloc[i,0]] = [df.iloc[i,3]]
    return dicc_generos


def aplicar_generos(col_index, dicc_generos):

    """
    Aplica los géneros de una película a partir de su identificador, si existe en el diccionario de géneros.

    Parámetros:
        col_index (int): El identificador de la película cuyo género se desea obtener.
        dicc_generos (dict): Un diccionario que contiene los identificadores de las películas como claves y listas 
                             de géneros como valores.

    Retorna:
        list: Una lista con los géneros asociados a la película, si el identificador se encuentra en el diccionario.
        np.nan: Si el identificador no existe en el diccionario.
    """
    if col_index in dicc_generos:

        lista = dicc_generos[col_index]
        dicc_generos.pop(col_index)
        return lista
    else:
        return np.nan




def plataformas(id_IMDB):
    """
    Consulta la API de Streaming Availability para obtener información sobre las plataformas donde se encuentra disponible
    una serie o película, utilizando su identificador de IMDb.

    Parámetros:
        id_IMDB (str): El identificador de IMDb de la serie o película a consultar.

    Retorna:
        dict: Un diccionario con la respuesta en formato JSON que contiene la información sobre la disponibilidad en
              diferentes plataformas de streaming, incluyendo detalles como episodios y opciones de visualización.
    """

    url = f"https://streaming-availability.p.rapidapi.com/shows/{id_IMDB}"

    querystring = {"series_granularity":"episode","output_language":"en","country":"es"}

    headers = {
        "x-rapidapi-key": api_key_2,
        "x-rapidapi-host": "streaming-availability.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()

