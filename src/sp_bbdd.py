# Conexión a base de datos PostgreSQL
# -----------------------------------------------------------------------
import psycopg2

# Barra de progreso
# -----------------------------------------------------------------------
from tqdm import tqdm

class Postgres:
    """
    Clase para gestionar conexiones y operaciones en una base de datos PostgreSQL.
    """
    def __init__ (self, database, user, password, host, port):
        """
        Inicializa una instancia de la clase Postgres.

        Parámetros:
            database (str): Nombre de la base de datos.
            user (str): Usuario para la conexión.
            password (str): Contraseña del usuario.
            host (str): Dirección del host.
            port (int o str): Puerto para la conexión.
        """

        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port


    def crear_conexion (self):
        """
        Crea una conexión a la base de datos PostgreSQL.

        Intenta establecer la conexión y guarda el objeto conexión en el atributo `self.connection`.
        En caso de error, maneja algunas de las excepciones comunes relacionadas con la conexión.
        """

        # si bien es cierto que crear la conexión es sencillo, es importante controlar los posibles errores que pudieran existir cuando realicemos estas conexiones
        try:
            connection = psycopg2.connect(
                database= self.database, # la base de datos con la que queremos trabajar
                user= self.user, # el usuario que tenemos 
                password= self.password,
                host= self.host,
                port= self.port)

            self.connection = connection

        except OperationalError as e:
            # Manejo de errores comunes
            if e.pgcode == errorcodes.INVALID_PASSWORD:
                print("Contraseña inválida.")
                
            elif e.pgcode == errorcodes.CONNECTION_EXCEPTION:
                print("Error de conexión.")
            else:
                print(f"Ocurrió un error: {e}")
        


    def cerrar_conexion(self):
        """
        Cierra la conexión a la base de datos PostgreSQL.

        Se asume que la conexión ya fue establecida y se cierra utilizando el atributo `self.connection`.
        """
        connection = self.crear_conexion()
        self.connection.close()

    def query_creacion(self, query):
        """
        Ejecuta una query de creación (DDL) en la base de datos.

        Parámetros:
            query (str): La instrucción SQL para crear objetos (tablas, índices, etc.).
        """
        self.crear_conexion()
        connection = self.connection
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            cursor.close()
        except Exception as error:
            print(f"Ocurrió un error: {error}")

        self.cerrar_conexion()



    def query_insercion (self, tabla, df):
        """
        Inserta registros en la tabla especificada utilizando un DataFrame de pandas.

        Parámetros:
            tabla (str): Nombre de la tabla en la que se insertarán los registros.
            df (pandas.DataFrame): DataFrame que contiene los datos a insertar.
        """
        self.crear_conexion()
        connection = self.connection
        cursor = connection.cursor()
        cols = ', '.join(df.columns)
        s = ['%s' for i in range(len(df.columns))]
        values = ', '.join(s)
        query = f'''INSERT INTO "{tabla}" ({cols}) VALUES ({values})'''
        lista_tuplas = df.to_numpy().tolist()
        try:
        # Ejecutamos nuestras queries
            cursor.executemany(query, lista_tuplas)
            connection.commit()
            #Mostramos el número de registros insertados
            print(cursor.rowcount, 'registros insertados')
            # Ejecutamos nuestra query
            cursor.close()
        #Si la query no es exitosa que nos indique el error pertiente
        except cursor.connector.Error as err:
                print(err)
                print("Error Code:", err.errno)
                print("SQLSTATE", err.sqlstate)
                print("Message", err.msg)
        cursor.close()
        self.cerrar_conexion()
        

    
class ListasInsertar:
    """
    Clase para generar listas de inserción a partir de las colecciones de la base de datos.

    Atributos:
        colecc_api: Conexión a la colección de la API de películas (información complementaria).
        colecc_pelis: Conexión a la colección principal de películas.
        colecc_actores: Conexión a la colección de actores/personas.
    """

    def __init__ (self, colecc_api, colecc_pelis, colecc_actores):
        """
        Inicializa la clase ListasInsertar con las colecciones necesarias.

        Parámetros:
            colecc_api: Conexión a la colección de la API de películas.
            colecc_pelis: Conexión a la colección de películas.
            colecc_actores: Conexión a la colección de actores.
        """
        self.colecc_api = colecc_api
        self.colecc_pelis = colecc_pelis
        self.colecc_actores = colecc_actores

    def genero(self):
        """
        Genera una lista de géneros únicos extraídos de la colección de la API.

        Recorre cada documento de la colección `colecc_api`, extrae los géneros y
        devuelve una lista de tuplas en la que cada tupla contiene un índice y el género.

        Retorna:
            list: Lista de tuplas con el formato (índice, género).
        """
        generos = set()
        for peli in list(self.colecc_api.find()):
            for genero in peli['genre']:
                generos.add(genero)
        list_generos = []
        for i, genero in enumerate(list(generos), start=1):
            list_generos.append((i,genero))

        return list_generos

    def tipos(self):
        """
        Genera una lista de tipos únicos de películas extraídos de la colección de la API.

        Recorre cada documento en la colección `colecc_api` y extrae el tipo de película,
        devolviendo una lista de tuplas donde cada tupla contiene un índice y el tipo.

        Retorna:
            list: Lista de tuplas con el formato (índice, tipo).
        """
        tipos = set()
        for peli in list(self.colecc_api.find()):
            tipos.add(peli['type'])
        list_tipos = []
        for i, tipo in enumerate(list(tipos), start=1):
            list_tipos.append((i,tipo))

        return list_tipos


    def pelis(self):
        """
        Genera una lista de películas a partir de la colección de películas.

        Para cada película en la colección `colecc_pelis`, obtiene información adicional 
        (título, año, género y tipo) a partir de la colección `colecc_api` usando el ID de IMDb.
        Además, extrae otros campos como puntuación y duración.

        Retorna:
            list: Lista de tuplas con los datos de cada película en el formato
                  (id_IMDB, título, año, género, tipo, puntuación, duración).
        """
        lista_peliculas = []
        for peli in tqdm(list(self.colecc_pelis.find())):
            imdb = peli['id_IMDB']
            titulo = self.colecc_api.find_one({'id':peli['id_IMDB']})['title']
            year = self.colecc_api.find_one({'id':peli['id_IMDB']})['year']
            genero = self.colecc_api.find_one({'id':peli['id_IMDB']})['genre']
            tipo = self.colecc_api.find_one({'id':peli['id_IMDB']})['type']
            puntuacion = peli['puntuacion']
            duracion = peli['duracion']

            tupla = (imdb,titulo, year, genero, tipo, puntuacion, duracion)

            lista_peliculas.append(tupla)

        return lista_peliculas

    def personas(self):
        """
        Genera una lista de personas (directores, guionistas y actores) a partir de las colecciones.

        - Recorre cada película en `colecc_pelis` para extraer los directores y guionistas.
        - Si la persona ya existe en la colección `colecc_actores`, verifica su campo 'roles' y, 
          en caso de no tener el rol correspondiente, lo actualiza.
        - Si la persona no existe, crea una nueva entrada con datos predeterminados.
        - Finalmente, recorre la colección `colecc_actores` para incluir todos los actores.

        Retorna:
            list: Lista de tuplas con los datos de cada persona en el formato
                  (nombre, año, conocido, roles, premios, nominaciones).
        """
        lista_personas = []
        for peli in tqdm(list(self.colecc_pelis.find())):
            for director in peli['direccion']:
                if self.colecc_actores.find_one({'nombre':director}):
                    if  type(self.colecc_actores.find_one({'nombre':director})['roles']) is float:
                        continue
                    elif  type(self.colecc_actores.find_one({'nombre':director})['roles']) is not list:
                        continue
                    elif 'Dirección' in self.colecc_actores.find_one({'nombre':director})['roles']:
                        continue
                    else:
                        self.colecc_actores.update_one({'nombre':director},{'$set': {'roles': self.colecc_actores.find_one({'nombre':director})['roles'].append('Dirección')}})
                    
                else:
                    nombre = director
                    año = np.nan
                    conocido = list(pd.DataFrame(self.colecc_pelis.find({'direccion': director},{'id_IMDB':1, '_id':0}))['id_IMDB'])
                    roles = ['Dirección']
                    premios = np.nan
                    nominaciones = np.nan
                    tupla = (nombre,año,conocido, roles, premios, nominaciones)
                    lista_personas.append(tupla)
                        
            for guionista in peli['guion']:
                if self.colecc_actores.find_one({'nombre':guionista}):
                    if  type(self.colecc_actores.find_one({'nombre':guionista})['roles']) is float:
                        continue
                    elif  type(self.colecc_actores.find_one({'nombre':guionista})['roles']) is not list:
                        continue
                    elif 'Guion' in self.colecc_actores.find_one({'nombre':guionista})['roles'] :
                        continue
                    else:
                        self.colecc_actores.update_one({'nombre':guionista},{'$set': {'roles': self.colecc_actores.find_one({'nombre':guionista})['roles'].append('Guion')}})


                else:
                    nombre = guionista
                    año = np.nan
                    conocido = list(pd.DataFrame(self.colecc_pelis.find({'guion': guionista},{'id_IMDB':1, '_id':0}))['id_IMDB'])
                    roles = ['Guion']
                    premios = np.nan
                    nominaciones = np.nan
                    tupla = (nombre,año,conocido, roles, premios, nominaciones)
                    lista_personas.append(tupla)

        for actor in tqdm(list(self.colecc_actores.find())):
            nombre = actor['nombre']
            año = actor['year']
            conocido = actor['conocido']
            roles = actor['roles']
            premios = actor['premios']
            try:
                nominaciones = actor['nominaciones']
            except:
                nominaciones = np.nan
            tupla = (nombre,año,conocido, roles, premios, nominaciones)
            lista_personas.append(tupla)

        return lista_personas


    def roles(self, df):
        """
        Genera una lista de roles únicos a partir del DataFrame proporcionado.

        Recorre la columna 'roles' del DataFrame, descartando aquellos roles que contengan dígitos,
        y devuelve una lista de tuplas en la que cada tupla contiene un índice y el rol.

        Parámetros:
            df (pandas.DataFrame): DataFrame que contiene la columna 'roles'.

        Retorna:
            list: Lista de tuplas con el formato (índice, rol).
        """
        roless = set()
        for roles in df['roles']:
            if type(roles) is not list:
                continue
            for rol in roles:
                if any(char.isdigit() for char in rol):
                    continue
                roless.add(rol)

        list_roles = []
        for i, rol in enumerate(list(roless), start=1):
            list_roles.append((i,rol))

        
        return list_roles




