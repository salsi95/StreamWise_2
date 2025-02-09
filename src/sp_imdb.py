# Importamos las librerías que necesitamos

# Barra de progreso
# -----------------------------------------------------------------------
from tqdm import tqdm

# Manejo del sistema
# -----------------------------------------------------------------------
import sys
sys.path.append("../")  # Agregamos el directorio principal al sistema de rutas


# Tratamiento de datos
# -----------------------------------------------------------------------
import numpy as np
import pandas as pd

# Automatización web con Selenium
# -----------------------------------------------------------------------
from selenium import webdriver  # Permite automatizar la interacción con navegadores web
from webdriver_manager.chrome import ChromeDriverManager  # Gestiona la instalación del controlador de Chrome
from selenium.webdriver.common.keys import Keys  # Simula eventos de teclado en Selenium
from selenium.webdriver.support.ui import Select  # Manejo de elementos desplegables en formularios

# Traducción automática
# -----------------------------------------------------------------------
from deep_translator import GoogleTranslator

# Conexión a base de datos
# -----------------------------------------------------------------------
import pymongo


#Conexión con Mongo
cliente = pymongo.MongoClient()
imdb = cliente['IMDB']
peliculas = imdb['Peliculas']
actores = imdb['Actores']


def obtener_pelis(df_iterable):
    """
    Realiza web scraping en IMDb para obtener información detallada de películas a partir de una lista de identificadores.

    Parámetros:
        df_iterable (iterable): Un iterable que contiene los identificadores de IMDb de las películas a buscar.

    Funcionalidad:
        - Abre un navegador Chrome con Selenium.
        - Busca cada película en IMDb y extrae información como puntuación, directores, guionistas, duración y argumento.
        - Traduce el argumento al inglés si está disponible.
        - Inserta los datos obtenidos en una base de datos MongoDB.

    Nota:
        - Se omiten las películas que ya existen en la base de datos.
        - Si ocurre un error durante la búsqueda, se reinicia el navegador para continuar con las siguientes películas.

    No retorna ningún valor.
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.imdb.com")
    for id_peli in tqdm(df_iterable): 
        if peliculas.find_one({'id_IMDB': id_peli}): #Si la peli está en mongo pasa a la siguiente
            continue
        dicc = {}
        dicc['id_IMDB'] = id_peli
        #Quitamos lo de la cuenta
        try:
            cuenta=driver.find_element('css selector','#imdbHeader > div.ipc-page-content-container.ipc-page-content-container--center.navbar__inner > div.nav__userMenu.navbar__user.sc-jfTVlA.esWGB > div > div > div > div > div.sc-cOxWqc.bNDQpU > button > svg').click() 

        except:
            pass
        #Intentamos la búsqueda si no funciona repetimos el proceso por si se ha caído la página en el primer intento
        try:
            busqueda_peli = driver.find_element('css selector', '#suggestion-search').send_keys(id_peli, Keys.ENTER)
        except:
            driver.close()
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get("https://www.imdb.com")
            busqueda_peli = driver.find_element('css selector', '#suggestion-search').send_keys(id_peli, Keys.ENTER)
        #Puntuacion
        try:
            dicc['puntuacion'] = float(driver.find_element('css selector','#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > section > div:nth-child(5) > section > section > div.sc-9a2a0028-3.bwWOiy > div.sc-3a4309f8-0.jJkxPn.sc-70a366cc-1.kUfGfN > div > div:nth-child(1) > a > span > div > div.sc-d541859f-0.hNIoIx > div.sc-d541859f-2.kxphVf > span.sc-d541859f-1.imUuxf').text.replace(",","."))
                                                                        
        except:
            dicc['puntuacion'] = np.nan

        #Directores y guionistas
        directores = []
        guionistas = []

        for i in range(1,5):
            try:

                directores.append(driver.find_element("xpath", f'//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul/li[{i}]/a').text)
            except:                                              
                pass

            try:
                guionistas.append(driver.find_element("xpath", f'//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]/div/ul/li[{i}]/a').text)
            except:
                pass

            dicc['direccion'] = directores

            dicc['guion'] = guionistas
        #Duración de las pelícuals
        try:
            dicc['duracion'] = driver.find_element('css selector','#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > section > div:nth-child(5) > section > section > div.sc-9a2a0028-3.bwWOiy > div.sc-70a366cc-0.bxYZmb > ul > li:nth-child(3)').text.replace('h','').replace('min','').split()
            if len(dicc['duracion']) == 1:                         
                try:
                    dicc['duracion'] = int(dicc['duracion'][0])
                except:
                    dicc['duracion'] = np.nan
            else:
                try:
                    dicc['duracion'] = int(dicc['duracion'][0])*60 + int(dicc['duracion'][1])
                except:
                    dicc['duracion'] = np.nan
        except:
            
            try:
                dicc['duracion']  =driver.find_element('css selector','#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > section > div:nth-child(5) > section > section > div.sc-9a2a0028-3.bwWOiy > div.sc-70a366cc-0.bxYZmb > ul > li:nth-child(2)').text.replace('h','').replace('min','').split()
                if len(dicc['duracion']) == 1:
                    try:
                        dicc['duracion'] = int(dicc['duracion'][0])
                    except:
                        dicc['duracion'] = np.nan
                else:
                    try:
                        dicc['duracion'] = int(dicc['duracion'][0])*60 + int(dicc['duracion'][1])
                    except:
                        dicc['duracion'] = np.nan
            except:
                dicc['duracion'] = np.nan
        
        
        #Argumento
        try:
            dicc['argumento'] = driver.find_element('xpath','//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]').text
            #Traducimos el argumento a inglés
            dicc['argumento'] = GoogleTranslator(source='auto', target='en').translate(dicc['argumento'])
            if dicc['argumento'] == '':
                dicc['argumento'] = np.nan
        except:
            dicc['argumento'] = np.nan
            # Insertar el documento en mongo
        peliculas.insert_one(dicc)

    driver.close()



def obtener_actores():
    """
    Realiza web scraping en IMDb para obtener los actores principales de cada película almacenada en la base de datos.

    Funcionalidad:
        - Abre un navegador Chrome con Selenium y navega a IMDb.
        - Para cada película en la base de datos que aún no tenga actores registrados:
            - Busca la película en IMDb mediante su identificador.
            - Extrae hasta 10 actores principales.
            - Almacena la información en la base de datos.
        - En caso de errores en la búsqueda, reinicia el navegador para continuar con el proceso.

    No retorna ningún valor.
    """


    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.imdb.com/")
    for peli in tqdm(list(peliculas.find())):
        if 'actores' in peli.keys(): #Si ya tiene la clave actores pasa a la siguiente película
            continue
        #Busca la película y si no la encuentra vuelvwe a abrir el navegador
        try:
            driver.find_element("css selector", "#suggestion-search").send_keys(peli['id_IMDB'], Keys.ENTER)
        except:
            driver.close()
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get("https://www.imdb.com")
            driver.find_element("css selector", "#suggestion-search").send_keys(peli['id_IMDB'], Keys.ENTER)

        #Buscamos los actores
        lista_actores = []
        for i in range(1, 11):
            try:
                lista_actores.append(driver.find_element("css selector", f"#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > div > section > div > div.sc-aa354f15-1.cgHAsh.ipc-page-grid__item.ipc-page-grid__item--span-2 > section.ipc-page-section.ipc-page-section--base.sc-cd7dc4b7-0.ycheS.title-cast.title-cast--movie.celwidget > div.ipc-shoveler.ipc-shoveler--base.ipc-shoveler--page0.title-cast__grid > div.ipc-sub-grid.ipc-sub-grid--page-span-2.ipc-sub-grid--wraps-at-above-l.ipc-shoveler__grid > div:nth-child({i}) > div.sc-cd7dc4b7-7.vCane > a").text)
                                                                        
                                                                        
            except:
                pass

            try:
                lista_actores.append(driver.find_element("css selector", f"#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > div > section > div > div.sc-aa354f15-1.cgHAsh.ipc-page-grid__item.ipc-page-grid__item--span-2 > section.ipc-page-section.ipc-page-section--base.sc-cd7dc4b7-0.ycheS.title-cast.title-cast--episode.celwidget > div.ipc-shoveler.ipc-shoveler--base.ipc-shoveler--page0.title-cast__grid > div.ipc-sub-grid.ipc-sub-grid--page-span-2.ipc-sub-grid--wraps-at-above-l.ipc-shoveler__grid > div:nth-child({i}) > div.sc-cd7dc4b7-7.vCane > a").text)
            except:
                pass
        
        #Actualizamos el documento de mongo
        peliculas.update_one({'id_IMDB':peli['id_IMDB']},{'$set': {'actores': lista_actores}})

    driver.close()

def obtener_conocidos():
    """
    Realiza web scraping en IMDb para obtener las películas o series más conocidas de cada actor almacenado en la base de datos.

    Funcionalidad:
        - Abre un navegador Chrome con Selenium y navega a IMDb.
        - Para cada actor en la base de datos que no tenga información válida en la clave 'conocido':
            - Busca el actor en IMDb mediante su nombre.
            - Extrae hasta 4 películas o series en las que es conocido.
            - Almacena la información en la base de datos.
        - En caso de errores en la búsqueda, reinicia el navegador para continuar con el proceso.

    No retorna ningún valor.
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.imdb.com/")
    for actor in tqdm(list(actores.find())):
        if  type(actor['conocido']) is float: #Si en lugar de una lista es un float(nan) pasa al siguiente
            continue
        elif len(actor['conocido'])<1: #Si la lista está vacía pasa al siguiente
            continue
        elif type(actor['conocido'][0]) is float: #Si el primer elemento de la lista es un float (nan) pasa al siguiente
            continue
        elif len(actor['conocido'][0]) == 10 or len(actor['conocido'][0]) == 9: #Si el primer elemento de la lista tiene 9 caracteres pasa al siguiente
            continue

        #Intenta una primera búsqueda y sino pasa a la siguiente
        try:
            busqueda_actor = driver.find_element('css selector', '#suggestion-search').send_keys(actor['nombre'], Keys.ENTER)
            driver.implicitly_wait(3)
            driver.find_element("css selector", "#__next > main > div.ipc-page-content-container.ipc-page-content-container--full.sc-9b6c53e1-0.jTQUPo > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(4) > div.sc-b03627f1-2.gWHDBT > ul > li:nth-child(1) > div.ipc-metadata-list-summary-item__c > div > a").click()
                                                
        except:
            driver.close()
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get("https://www.imdb.com")
            busqueda_actor = driver.find_element('css selector', '#suggestion-search').send_keys(actor['nombre'], Keys.ENTER)
            try:
                driver.find_element("css selector", "#__next > main > div.ipc-page-content-container.ipc-page-content-container--full.sc-9b6c53e1-0.jTQUPo > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(4) > div.sc-b03627f1-2.gWHDBT > ul > li:nth-child(1) > div.ipc-metadata-list-summary-item__c > div > a").click()
            except:
                continue

        #Incluye el id_IMDB de las películas por las que es conocido cada actor
        lista_conocidos = []
        try:
            for i in range(1,5):
                nuevo_conocido = driver.find_element("xpath", f'//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/div[3]/section[1]/div[2]/div/div[2]/div[{i}]/div[2]/div[1]/a').get_attribute('href').split('/')[5]
                lista_conocidos.append(nuevo_conocido)                                         
        except:
            pass
        #Actualiza el documento del actor
        actores.update_one({'nombre':actor['nombre']},{'$set': {'conocido': lista_conocidos}})
        
    driver.close()

def obtener_info_actores():
    """
    Realiza web scraping en IMDb para obtener información de los actores que aparecen en la base de datos de películas.

    Funcionalidad:
        - Abre un navegador Chrome con Selenium y navega a IMDb.
        - Para cada actor en la base de datos de películas que no esté registrado en la colección de actores:
            - Busca el actor en IMDb por nombre.
            - Extrae información relevante como:
                - Año de nacimiento (si está disponible).
                - Lista de películas o series más conocidas.
                - Roles principales interpretados.
                - Cantidad de premios y nominaciones.
            - Almacena la información en la base de datos de actores.
        - En caso de errores en la búsqueda, maneja excepciones y reinicia el navegador si es necesario.

    No retorna ningún valor.
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.imdb.com/")
    #Busca cada pelicula
    for pelicula in tqdm(list(peliculas.find())):
        #Busca cada actor dentro de película
        for actor in pelicula['actores']:
            #Comprueba si ya tenemos ese actor en la BBDD y si es así pasa al siguiente
            if actores.find_one({'nombre': actor}):
                continue
            dicc = {}
            dicc['nombre'] = actor
            try:
                busqueda_actor = driver.find_element('css selector', '#suggestion-search').send_keys(actor, Keys.ENTER)
                driver.implicitly_wait(3)
                driver.find_element("css selector", "#__next > main > div.ipc-page-content-container.ipc-page-content-container--full.sc-9b6c53e1-0.jTQUPo > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(4) > div.sc-b03627f1-2.gWHDBT > ul > li:nth-child(1) > div.ipc-metadata-list-summary-item__c > div > a").click()
            #Intenta una primera búsqueda y sino pasa a la siguiente
            except:
                driver.close()
                driver = webdriver.Chrome()
                driver.maximize_window()
                driver.get("https://www.imdb.com")
                busqueda_actor = driver.find_element('css selector', '#suggestion-search').send_keys(actor, Keys.ENTER)
                #Intenta seleccionar al actor y si no lo encuentra llena toda la info con nulos
                try:
                    driver.find_element("css selector", "#__next > main > div.ipc-page-content-container.ipc-page-content-container--full.sc-9b6c53e1-0.jTQUPo > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(4) > div.sc-b03627f1-2.gWHDBT > ul > li:nth-child(1) > div.ipc-metadata-list-summary-item__c > div > a").click()
                except:
                    lista_conocidos = []
                    dicc['year'] = np.nan
                    dicc['conocido']= lista_conocidos
                    dicc['roles']= np.nan
                    dicc['premios'] = np.nan
                    dicc['nominaciones'] = np.nan
                    actores.insert_one(dicc)
                    continue
            #Año de nacimiento
            try: 
                dicc['year'] = driver.find_element("css selector", "#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > div > section > div > div.sc-aa354f15-1.cgHAsh.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(22) > div.sc-f65f65be-0.dQVJPm > ul > li:nth-child(4) > div > ul > li.ipc-inline-list__item.test-class-react > a").text.split(",")[-1] 
                dicc['year'] = int(dicc['year'].split()[-1])
                                                        #__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-304f99f6-0.fSJiHR > section > div:nth-child(4) > section > section > div.sc-e226b0e3-4.dEqUUl > div.sc-e226b0e3-6.CUzkx > div.sc-e226b0e3-11.kkLqLt > section > aside > div > span:nth-child(2)
            except:
                dicc['year'] = np.nan
            #Películas por las que es conocido el actor
            try:
                lista_conocidos = []
                for i in range(1,5):
                    conocido = driver.find_element("xpath", f'//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/div[3]/section[1]/div[2]/div/div[2]/div[{i}]/div[2]/div[1]/a').get_attribute('href').split('/')[5]
                                                            
                    lista_conocidos.append(conocido)
                dicc['conocido'] =lista_conocidos                   #__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-304f99f6-0.fSJiHR > div > section > div > div.sc-9178d6fe-1.fqVKQb.ipc-page-grid__item.ipc-page-grid__item--span-2 > div.celwidget > section:nth-child(1) > div.sc-a6d4b6c0-0.bBRhdF > div > div.ipc-sub-grid.ipc-sub-grid--page-span-2.ipc-sub-grid--wraps-at-above-l.ipc-shoveler__grid
            except:
                dicc['conocido']= lista_conocidos
            #Roles por los que es conocido el actor
            try:
                dicc['roles'] = driver.find_element("css selector", "#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > section > div:nth-child(5) > section > section > div.sc-9a2a0028-3.bwWOiy > div > ul").text.split("\n")
            except:
                dicc['roles']= np.nan
            #Premios y nominaciones
            try:
                premios = driver.find_element("css selector", '#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-75c84411-0.icfMdl > div > section > div > div.sc-aa354f15-1.cgHAsh.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(3) > div > ul > li > div > ul').text
                try:
                    dicc['premios'] = int(premios.split(' premio')[0])
                    nominaci_y =premios.split(' premio')[-1].split(' nominaci')[0]
                    dicc['nominaciones'] = int(nominaci_y.split(' y ')[-1])
                except:
                    if 'nominaci' in premios: 
                        dicc['nominaciones'] = int(premios.split(' nominaci')[0])
                        dicc['premios'] = np.nan
                    else:
                        dicc['premios'] = premios.split(' premio')[0]
                        dicc['nominaciones'] = np.nan
            except:
                dicc['premios'] = np.nan
                dicc['nominaciones'] = np.nan
                       
            actores.insert_one(dicc)
    driver.close()
