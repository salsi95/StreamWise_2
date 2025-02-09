# StreamWise

StreamWise es una sistema de recomendación diseñado para ofrecer recomendaciones aún más precisas y personalizadas de películas, series y videojuegos. Este sistema se basa en técnicas avanzadas de Procesamiento de Lenguaje Natural (NLP), aprendizaje automático y una integración optimizada de múltiples fuentes de datos.

## Características destacadas
- **Recomendaciones inteligentes:** Basadas en el análisis del argumento, género, actores, directores y otros metadatos.
- **Optimización del procesamiento de texto:** Utilización de textos limpios para mejorar el rendimiento del recomendador.
- **Base de datos relacional mejorada:** Gestión eficiente y escalable de los datos mediante sistemas relacionales.
- **Interfaz web local:** Implementada con Streamlit para la visualización rápida de recomendaciones.

## Fases del proyecto
1. **Obtención de información básica de las películas:** Uso de la API de RapidAPI (MoviesDatabase) para recopilar datos iniciales.
2. **Obtención de información adicional de IMDb:** Scraping de información complementaria de las películas.
3. **Obtención de información de los actores de IMDb:** Recolección de detalles relevantes de actores y actrices.
4. **Obtención de plataformas de streaming:** Uso de una API para determinar en qué plataformas está disponible cada película o serie.
5. **Creación de la base de datos:** Integración y normalización de los datos obtenidos en una base de datos relacional.
6. **Procesamiento del argumento con NLP:** Limpieza y análisis del texto de los argumentos para mejorar la calidad de las recomendaciones.
7. **Creación del sistema de recomendación:** Desarrollo del modelo basado en los datos recopilados y procesados.
8. **Implementación de la interfaz Streamlit:** Creación de la interfaz web para facilitar la interacción del usuario con el sistema.

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/salsi95/StreamWise_2.git
   ```
2. Accede al directorio del proyecto:
   ```bash
   cd StreamWise_2
   ```
3. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Ejecuta la interfaz de usuario local:
   ```bash
   streamlit run app.py
   ```
2. Accede a la aplicación en tu navegador local y sigue las instrucciones para explorar recomendaciones personalizadas.

## Estructura del proyecto
- `data/`: Contiene los archivos de datos usados para el entrenamiento y pruebas del sistema.
- `notebooks/`: Jupyter notebooks para el análisis y pruebas de los modelos.
- `models/`: Modelos de recomendación entrenados.
- `app.py`: Archivo principal de la interfaz web local.
- `requirements.txt`: Lista de dependencias necesarias para el proyecto.

## Tecnologías utilizadas
- **Python**
- **Streamlit** (Interfaz web)
- **NLTK / SpaCy** (Procesamiento de texto)
- **Pandas y NumPy** (Manejo y análisis de datos)
- **PostgreSQL / SQLite** (Bases de datos relacionales)
- **Selenium / BeautifulSoup** (Scraping de datos adicionales)

## Cómo contribuir
¡Tus contribuciones son bienvenidas! Para contribuir al proyecto:
1. Realiza un fork del repositorio.
2. Crea una nueva rama para tu funcionalidad:
   ```bash
   git checkout -b feature-nueva-funcionalidad
   ```
3. Realiza los cambios necesarios y haz commit:
   ```bash
   git commit -m "Descripción breve de los cambios"
   ```
4. Envía un pull request para revisión.

## Contacto
Si tienes dudas, sugerencias o deseas colaborar, puedes encontrarme en [GitHub](https://github.com/salsi95).

## Licencia
Este proyecto está bajo la licencia MIT.

