# Manejo del sistema
# -----------------------------------------------------------------------
import sys  # System-specific parameters and functions
sys.path.append("../")  # Adding the parent directory to the system path

# Funciones personalizadas (Procesamiento NLP)
# -----------------------------------------------------------------------
from src import sp_recomendador as sr
import streamlit as st
import pymongo
#import pandas as pd
#from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
#from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.preprocessing import MinMaxScaler

# Conectar a MongoDB
# lo primero que tenemos que hacer es conectarnos con Mongo
cliente = pymongo.MongoClient()
# nos conectamos con una BBDD 
streamwise = cliente['StreamWise']
api = streamwise['Api']
peliculas = streamwise['Peliculas']
actores = streamwise['Actores']
nlp = streamwise['NLP']



# Interfaz en Streamlit
st.set_page_config(page_title="StreamWise", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #1E1B33; color: white;}
    .stButton > button {background-color: #6A0DAD; color: white; font-size: 18px;}
    .stTextInput > div > div > input {background-color: #2A2A40; color: white;}
    .stMarkdown {text-align: center;}
    div[data-baseweb="select"] {background-color: #6A0DAD !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 5px !important;}
    div[data-baseweb="select"] > div {color: white !important;}
    .stMultiSelect [role="option"] {background-color: #6A0DAD !important; color: white !important;}
    .stMultiSelect [role="option"][aria-selected="true"] {background-color: #4B0082 !important; color: white !important;}
    .stMultiSelect div[role="listbox"] > div {background-color: #6A0DAD !important; color: white !important; border-radius: 5px; padding: 5px;}
    </style>
    """, unsafe_allow_html=True)

# Cambiar el tamaño del título de la página
st.markdown("<h1 style='color: white; font-size: 60px; text-align: center;'>🎬 StreamWise 🎬</h1>", unsafe_allow_html=True)

# Cambiar el tamaño del subtítulo de la página
st.markdown("<h2 style='color: white; font-size: 30px; text-align: center;'>Your Data-Driven Streaming Guide!</h2>", unsafe_allow_html=True)


# Entrada del usuario
titulo = st.text_input("Enter the name of a movie:", )


# Opciones para la recomendación
columnas_seleccionadas = st.multiselect(
    "Select the recommendation criteria",
    ['argument', 'genre', 'director', 'script', 'rating', 'actor'],
    default=['argument', 'genre']
)

if st.button("Get Recommendations") and titulo:
    recomendaciones = sr.recomendar_peliculas(titulo, columnas_seleccionadas)
    if recomendaciones:
        st.markdown("<h1 style='color: white; font-size: 60px; text-align: center;'>Recommended Movies</h1>", unsafe_allow_html=True)
        cols = st.columns(len(recomendaciones))  # Crear columnas dinámicas según el número de recomendaciones
        for i, pelicula in enumerate(recomendaciones):
            with cols[i]:
                st.markdown(f"""
                    <div style='display: flex; justify-content: center;'>
                        <img src="{pelicula.get('poster', '')}" alt="Poster de la película" style="height: 300px; object-fit: cover; border-radius: 10px;">
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"<h2 style='color: white; font-size: 25px;text-align: center;'>{pelicula['title']}</h2>", unsafe_allow_html=True)

        # Agregar sección "Más detalles" debajo de las recomendaciones
        st.markdown("<h2 style='color: white; font-size: 60px;text-align: center;'>More Details</h2>", unsafe_allow_html=True)

        # Crear una fila con dos columnas: izquierda (poster) y derecha (título + argumento)
        for pelicula in recomendaciones:
            sinopsis = peliculas.find_one({'id_IMDB': pelicula['id_IMDB']}, {'argumento': 1, '_id': 0})
            argumento = sinopsis['argumento'] if sinopsis and 'argumento' in sinopsis else 'Sin sinopsis disponible'

            # Extraemos la información adicional de la colección nlp
            pelicula_nlp = nlp.find_one({'id_IMDB': pelicula['id_IMDB']})

            direccion = "No disponible"
            genero = "No disponible"
            puntuacion = "No disponible"
            guion = "No disponible"
            actores = "No disponible"

            if pelicula_nlp:
                direccion = ", ".join(pelicula_nlp.get('direccion', []))
                genero = ", ".join(pelicula_nlp.get('genre', []))
                puntuacion = pelicula_nlp.get('puntuacion', "No disponible")
                guion = ", ".join(pelicula_nlp.get('guion', []))
                actores = ", ".join(pelicula_nlp.get('actores', []))

            # Extraemos la información sobre las plataformas de streaming
            streaming_info = nlp.find_one({'id_IMDB': pelicula['id_IMDB']}, {'streaming': 1, '_id': 0}).get('streaming', {})
            
            # Obtener plataformas para cada categoría (rent, buy, subscription)
            rent_platforms = streaming_info.get('rent', [])
            buy_platforms = streaming_info.get('buy', [])
            subscription_platforms = streaming_info.get('subscription', [])
            
            # Crear columnas dinámicas
            col1, col2 = st.columns([1, 2])  # 1 es para el poster, 2 para el texto

            # Columna 1: Mostrar el poster
            with col1:
                st.image(pelicula.get('poster', ''), use_column_width=True)

            # Columna 2: Mostrar título y argumento
            with col2:
                st.markdown(f"<h2 style='color: white; font-size: 50px;'>{pelicula['title']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: white; font-size: 20px;'>{argumento}</p>", unsafe_allow_html=True)

                info_col1, info_col2 = st.columns(2)  # 1 es para el poster, 2 para el texto

                # Mostrar información adicional sobre la película
                with info_col1:
                    st.markdown(f"<h4 style='color: white;font-size: 30px'>Rating:</h4><p style='color: white;font-size: 20px'>⭐ {puntuacion}</p>", unsafe_allow_html=True)
                with info_col2:
                    st.markdown(f"<h4 style='color: white;font-size: 30px'>Genre:</h4><p style='color: white;font-size: 20px'>{genero}</p>", unsafe_allow_html=True)
                
                info_col3, info_col4 = st.columns(2)
                with info_col3:
                    st.markdown(f"<h4 style='color: white;font-size: 30px'>Director:</h4><p style='color: white;font-size: 20px'>{direccion}</p>", unsafe_allow_html=True)
                
                with info_col4:
                    st.markdown(f"<h4 style='color: white;font-size: 30px'>Script:</h4><p style='color: white;font-size: 20px'>{guion}</p>", unsafe_allow_html=True)
                
                st.markdown(f"<h4 style='color: white;font-size: 30px'>Actors:</h4><p style='color: white;font-size: 20px'>{actores}</p>", unsafe_allow_html=True)

                # Crear una fila con tres columnas para las plataformas
                platforms_col1, platforms_col2, platforms_col3 = st.columns(3)

                with platforms_col1:
                    if rent_platforms:
                        st.markdown("<h4 style='color: white;font-size: 30px'>Alquiler:</h4>", unsafe_allow_html=True)
                        for platform in rent_platforms[:2]:
                            precio = platform['price']
                            st.markdown(f"<div><img src='{platform['img']}'  style='height: 40px;'> </div><p style='color: white;font-size: 20px'>{precio}</p>", unsafe_allow_html=True)
                with platforms_col2:
                    if buy_platforms:
                        st.markdown("<h4 style='color: white;font-size: 30px'>Compra:</h4>", unsafe_allow_html=True)
                        for platform in buy_platforms[:2]:
                            precio = platform['price']
                            st.markdown(f"<div><img src='{platform['img']}' style='height: 40px;'></div><p style='color: white;font-size: 20px'>{precio}</p>", unsafe_allow_html=True)
                with platforms_col3:
                    if subscription_platforms:
                        st.markdown("<h4 style='color: white;font-size: 30px'>Suscripción:</h4>", unsafe_allow_html=True)
                        for platform in subscription_platforms:
                            st.markdown(f"<div><img src='{platform['img']}' style='height: 40px;'> </div>", unsafe_allow_html=True)
    else:
        st.write("No se encontraron recomendaciones.")