# # Tratamiento de datos
# # -----------------------------------------------------------------------
import re


# # Para modelos NLP
# # -----------------------------------------------------------------------
import spacy
from nltk.corpus import stopwords
import nltk
import contractions


# Descargar stopwords si no están disponibles
nltk.download('stopwords')

# Descargar recursos necesarios de nltk
nltk.download('vader_lexicon')



def limpiar_texto(text, language="english"):
    """
    Limpia y normaliza un texto aplicando diversas transformaciones de preprocesamiento.

    Este método realiza las siguientes operaciones:
      - Expande contracciones (por ejemplo, convierte "don't" en "do not").
      - Convierte el texto a minúsculas.
      - Elimina puntuación y números.
      - Reemplaza múltiples espacios o saltos de línea por un solo espacio.
      - Elimina espacios en blanco al inicio y al final del texto.
      - Tokeniza el texto usando spaCy y aplica lematización.
      - Elimina las palabras vacías (stopwords) correspondientes al idioma especificado.

    Parámetros:
        text (str): El texto que se desea limpiar.
        language (str, opcional): Idioma del texto para la carga de stopwords y del modelo de spaCy.
                                  Por defecto es "english". Si se especifica otro idioma (por ejemplo, "es"),
                                  se cargará el modelo correspondiente ("es_core_news_sm").

    Retorna:
        str: El texto limpio y normalizado, con tokens lematizados y sin palabras vacías.
    """
    stop_words = set(stopwords.words(language))
    nlp = spacy.load("en_core_web_sm") if language == "english" else spacy.load("es_core_news_sm")
    # Expandir contracciones
    text = contractions.fix(text)  # Convierte "don't" -> "do not"
    
    # Limpieza de texto
    text = text.lower()  # Convertir a minúsculas
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar puntuación
    text = re.sub(r'\d+', '', text)  # Eliminar números
    text = re.sub(r'\s+', ' ', text)  # Reemplazar múltiples espacios o saltos de línea por un espacio
    text = text.strip()  # Quitar espacios en blanco al inicio y al final
    doc = nlp(text)  # Tokenizar con spaCy
    tokens = [token.lemma_ for token in doc if token.text not in stop_words]
    return " ".join(tokens)

