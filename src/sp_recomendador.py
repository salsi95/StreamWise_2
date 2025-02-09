import pymongo
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

cliente = pymongo.MongoClient()
# nos conectamos con una BBDD 
streamwise = cliente['StreamWise']
api = streamwise['Api']
peliculas = streamwise['Peliculas']
actores = streamwise['Actores']
nlp = streamwise['NLP']



# Crear DataFrame desde MongoDB
def crear_df(columnas_df):
    cliente = pymongo.MongoClient()
    streamwise = cliente['StreamWise']
    nlp = streamwise['NLP']

    df = pd.DataFrame(nlp.find())
    df["genre_text"] = df["genre"].apply(lambda x: " ".join(x) if isinstance(x, list) else x)
    df["director_text"] = df["direccion"].apply(lambda x: " ".join(x) if isinstance(x, list) else x)
    df["guion_text"] = df["guion"].apply(lambda x: " ".join(x) if isinstance(x, list) else x)
    df["actor_text"] = df["actores"].apply(lambda x: " ".join(x) if isinstance(x, list) else x)

    dicc_cols = {
        'argument': 'argumento',
        'genre': 'genre_text',
        'director': 'director_text',
        'script': 'guion_text',
        'rating': 'puntuacion',
        'actor': 'actor_text'
    }

    cols_df = ['id_IMDB', 'poster', 'title']
    for col in columnas_df:
        if col in dicc_cols:
            cols_df.append(dicc_cols[col])

    df_buscar = df[cols_df].dropna().reset_index(drop=True)
    return df_buscar

# Crear matriz de similitud
def crear_cosines(df):
    tfidvectorizer = TfidfVectorizer(stop_words="english")
    countvectorizer = CountVectorizer(analyzer="word", binary=True)
    lista_sim = []

    if "argumento" in df.columns:
        matrix_arg = tfidvectorizer.fit_transform(df["argumento"])
        lista_sim.append(cosine_similarity(matrix_arg))

    for col in ["genre_text", "director_text", "guion_text", "actor_text"]:
        if col in df.columns:
            matrix = countvectorizer.fit_transform(df[col])
            lista_sim.append(cosine_similarity(matrix))

    if "puntuacion" in df.columns:
        scaler = MinMaxScaler()
        df["puntuacion"] = scaler.fit_transform(df[["puntuacion"]])
        lista_sim.append(cosine_similarity(df[["puntuacion"]]))

    return sum(lista_sim)

# Función para obtener recomendaciones
def recomendar_peliculas(titulo, columnas_seleccionadas):
    df = crear_df(columnas_seleccionadas)

    # Obtener el ID de la película buscada
    pelicula_api = nlp.find_one({'title': titulo})
    if not pelicula_api:
        return []

    id_IMDB = pelicula_api['id_IMDB']
    idx = df[df["id_IMDB"] == id_IMDB].index[0]

    sim_scores = list(enumerate(crear_cosines(df)[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Filtrar solo las películas con similitud significativa
    sim_scores = [s for s in sim_scores if s[1] > 0]
    top_peliculas = sim_scores[1:6] if len(sim_scores) > 5 else sim_scores[1:]

    ids_recomendados = list(df.iloc[[i[0] for i in top_peliculas]]["id_IMDB"].values)
    recomendaciones = list(nlp.find({'id_IMDB': {'$in': ids_recomendados}}, {"id_IMDB":1, "title": 1, "poster": 1, "_id": 0}))

    return recomendaciones