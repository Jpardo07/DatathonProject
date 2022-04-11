# -----------------------------
#  Libraries import
# -----------------------------

import pandas as pd # Dataframes management
from zipfile import ZipFile  # Files compressed management
import os # Files management along OS
import re # Expresiones regulares

from os import mkdir # Comprobaciones de existencia de archivos etc.
from os.path import exists

import nltk # Procesamiento del lenguaje natural
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

import logging # Para generar logs
import datetime
import sys


# -----------------------------
# Variables a modificar para adaptar el código
# -----------------------------

# Tabla a nombrar para la BBDD
tableMain = "ZipsInfo"


# -----------------------------
# Importación de módulos
# -----------------------------

# Módulo personal para manejar la Base de datos del proyecto
from db import *

# -----------------------------
#  Data import
# -----------------------------

# Specifying the name of the zip file
fileZIP = "/items_ordered_2years_V2.zip"
fileCSV = "/items_ordered_2years_V2.csv"

path = "Inputs/Modificados - Atmira_Pharma_Visualization"
  
# Open the zip file in read mode
with ZipFile(f"{path}{fileZIP}", 'r') as zip: 
    # List all the contents of the zip file
    zip.printdir() 
  
    # Extract all files
    print('extraction...') 
    zip.extractall(path) 
    print('Done!')

#Import CSV to pandas
itemsOrdered = pd.read_csv(f"{path}{fileCSV}")
print("CSV imported to Pandas successfully")

# Remove uncompressed CSV file
os.remove(f"{path}{fileCSV}")
print("Original CSV removed to preserve repo health")


#Necesario para evitar malentendidos entre librerías posteriores
del zip


# -----------------------------
# Arreglos para facilitar el webscrapping
# -----------------------------

itemsOrdered.loc[itemsOrdered['zipcode'].eq('30139') & itemsOrdered['city'].eq('Murcia'), "city"] = "EL RAAL"
itemsOrdered['zipcode'] = itemsOrdered['zipcode'].replace("29039", "28039")
itemsOrdered.loc[itemsOrdered['zipcode'].eq('33195') & itemsOrdered['city'].eq('Oviedo '), "city"] = "Morente"
itemsOrdered["city"].replace(to_replace={'Cangas Del Narcea':"Cerezaliz"}, inplace=True)
itemsOrdered['zipcode'] = itemsOrdered['zipcode'].replace("O88oo", "08800")
itemsOrdered.loc[itemsOrdered['zipcode'].eq('43890') & itemsOrdered['city'].eq('TARRAGONA'), "city"] = "Hospitalet"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('07700') & itemsOrdered['city'].eq('MAHON'), "city"] = "Grau"
itemsOrdered['zipcode'] = itemsOrdered['zipcode'].replace("47021", "46021")
itemsOrdered.loc[itemsOrdered['zipcode'].eq('33405'), "city"] = "Raices Nuevo"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('29720') & itemsOrdered['city'].eq('MALAGA'), "city"] = "La Arana"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('08222'), "city"] = "Terrassa"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('03195'), "city"] = "Los Arenales Del Sol"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('08780'), "city"] = "Palleja"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('33405'), "city"] = "Raices Nuevo"
itemsOrdered['zipcode'] = itemsOrdered['zipcode'].replace("347007", "37007")
itemsOrdered.loc[itemsOrdered['zipcode'].eq('36194'), "city"] = "Perdecanai"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('29631'), "city"] = "Arroyo De La Miel"
itemsOrdered.loc[itemsOrdered['zipcode'].eq('27810'), "city"] = "Sancobade"
itemsOrdered['zipcode'] = itemsOrdered['zipcode'].replace("-39840", "39840")
itemsOrdered.loc[itemsOrdered['zipcode'].eq('50620'), "city"] = "Casetas"


# -----------------------------
#  SCRAPEO DE BASE DE DATOS 
# -----------------------------

# Detección de Base de Datos para almacenamiento de resultados formateados del Scrapping

def IntroDB():
    try:
        pathDB = "../databases/"
        nameDB= "scrapedZips.db"
        if exists(pathDB):
            print(f"Carpeta {pathDB} encontrada")
        else:
            mkdir(pathDB)
            print (f"Creada carpeta {pathDB}")
    except OSError:
        print (f"Creación de carpeta {pathDB} falló")
        
    if exists(f"{pathDB}{nameDB}"):
        print("Database existe")
        con, cur = SqlConnection(f"{pathDB}{nameDB}")
        return con, cur
    else:
        print("Database no existe")
        CreateCon(f"{pathDB}{nameDB}")
        con, cur = SqlConnection(f"{pathDB}{nameDB}")
        PrepareCon(con, cur, option="insert",
            values=("Test","Test","Test","Test","Test"))
        return con, cur


con, cur = IntroDB()

%%capture
try:
    if GetThings(cur, selection="Country,Region,City,Zipcode,id_ori", where=["ID", 1], limit=1)[0][0] == "Test":
        PrepareCon(con,cur,where=["ID",1],option="delete")
        cur.execute("UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = 'ZipsInfo';")
except IndexError:
    pass

'''
Check the next query if something was wrong
SELECT * FROM `sqlite_sequence`;
'''


# A continuación se genera una lista compuesta de tuplas compuestas de la siguiente forma: ("Ciudad", "Zipcode")

rawDataZipcode = list(zip(itemsOrdered["city"].tolist(), itemsOrdered["zipcode"].tolist()))


# -----------------------------
# Funciones destacadas
# -----------------------------


# Función que "limpia" los nombres de ciudades para mejorar su emparejamiento automático

def CityCleaner(text):
    stopWordSpanish = set(stopwords.words('spanish'))
    wordTokens = word_tokenize(AcentosLimpiador(text.lower()).rstrip()) 
    filteredSentence = [element for element in wordTokens if not element in stopWordSpanish] 
    return filteredSentence
 

# Función que limpia zipcodes

# Limpieza de zipcodes con RegEx
def num_guion(string):
    """ Get a string with the numbers and hyphens of another string
    
    Args:
        df: string used to extract the string with numbers abd hyphens

    Returns:
        df: the string with numbers and hyphens
    """
    aux = re.match("([\d-]+)", str(string))
    try:
        return str(aux.group())
    except:
        return string

itemsOrdered["zipcode"] = itemsOrdered["zipcode"].apply(lambda x: num_guion(x))


# Función que limpia los acentos con el fin de homogeneizar

def AcentosLimpiador(text):
	acentos = {'ñ':'n','á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'à':'a'}
	for ele in acentos:
		if ele in text:
			text = text.replace(ele, acentos[ele])
	return text


# Configuración de logging del scrapeo

logger = logging.getLogger('ScrapLog')
logger.setLevel(logging.INFO)

timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H-%M-%S')
filename=f'Scrapping{timestamp}.log'
formatter = logging.Formatter('[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')


file_handler = logging.FileHandler(filename=filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


logging.basicConfig(
    filename=filename,
    level=logging.INFO,
    format='[{%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
)


# Función que formatea los resultados del webscrapping de forma adecuada a los requerimientos necesarios

def zipCodeManipulation(city, zipcode, queryResult="", saved = False):
  
    # This conditional checks if the zipcode info was scrapped and stored succesfully
    if saved == False:

        listTestingZipcode = queryResult.split("\n")
        indexMatchRegex = list(map(lambda x: [(m.start(0), m.end(0)) for m in re.finditer(r"[a-z][A-Z0-9]", x)], listTestingZipcode))

        resultScrapClean = []
        for pas,resultScrap in enumerate(listTestingZipcode):
            for pos,ele in enumerate(indexMatchRegex[pas]):
                if len(indexMatchRegex[pas])==2:
                    if pos ==0:
                        txt = resultScrap[:ele[0]+1]+","+resultScrap[ele[1]-1:]
                    elif pos ==1:
                        txt = txt[:ele[0]+2]+","+txt[ele[1]:]
                        resultScrapClean.append(txt)
                elif len(indexMatchRegex[pas])==3:
                    if pos ==0:
                        txt = resultScrap[:ele[0]+1]+","+resultScrap[ele[1]-1:]
                    elif pos ==1:
                        txt = txt[:ele[0]+2]+","+txt[ele[1]:]
                    elif pos ==2:
                        txt = txt[:ele[0]+3]+","+txt[ele[1]+1:]
                        resultScrapClean.append(txt)

        resultScrapListed = [element.split(",") for element in resultScrapClean]
        resultScrapRearr = [(element[0], element[1], element[-2], element[-1]) for element in resultScrapListed]

        resultZip = []
        for element in resultScrapRearr:
            for element2  in CityCleaner(element[2]):
                if element2 in CityCleaner(city):
                    resultZip.append(element)
                    break
        try:
            resultZip = resultZip[0]
            resultZip = [resultZip[0],resultZip[1],resultZip[2],zipcode]
        except IndexError:
            resultZip = []
            for element in resultScrapRearr:
                for element2 in CityCleaner(element[2]):
                    for element3 in CityCleaner(city):
                        if element2 .__contains__(element3):
                            resultZip.append(element)
                            break
            try:
                resultZip = resultZip[0]
                resultZip = [resultZip[0],resultZip[1],resultZip[2],zipcode]
            except IndexError:
                resultZip = []
                for element in resultScrapRearr:
                    for element2 in CityCleaner(element[2]):
                        for city in CityCleaner(element3):
                            if element3.__contains__(element2):
                                resultZip.append(element)
                                break
                if resultZip != []:
                    resultZip = resultZip[0]
                    resultZip = [resultZip[0],resultZip[1],resultZip[2],zipcode]
                elif resultZip ==[] : #ELIMINAR ESTA LÍNEA PARA PODER VERIFICAR ERRORES
                    resultZip = ["ERROR1","ERROR","ERROR",zipcode]
                    
    elif saved == True:
        resultZip = GetThings(cur, selection="Country,Region,City,Zipcode", where=["Zipcode", zipcode], limit=1, simplify = True)

    return resultZip 



# -----------------------------
# Consultas a la BBDD local
# -----------------------------

logger.info("Starting Local Scrapping!")

for pos, element in enumerate(rawDataZipcode):
    try:

        if element[1]=="323903":
            
            if pos in [ele[0]-1 for ele in GetThings(cur, selection="ID", where=["Zipcode", element[1].rstrip()])]:
                logger.info(f"SP - Sin procesar |City: {element[0]} | Zipcode: {element[1]} | Orden del dataframe: {pos}")

            else:
                if GetThings(cur, selection="Zipcode", where=["Zipcode", element[1].rstrip()], limit=1, simplify=True) == None:
                    PrepareCon(con, cur, values=["China", "Zhejiang", "Lishui", "323903",pos], option="insert", verbose=False)
                    logger.info(f"SP - Insertado | City: {element[0]} | Zipcode: {element[1]} | Orden del dataframe: {pos}")
    
                else:
                    zipCodeDef = zipCodeManipulation(city=element[0], zipcode=element[1].rstrip(), saved = True)
                    logger.info(f"SP - Ya guardado en BBDD | City: {element[0]} | Zipcode: {element[1]} | Orden del dataframe: {pos}")
                    logger.info(f"Devuelto de query: {zipCodeDef}")

        if GetThings(cur, selection="Zipcode", where=["Zipcode", element[1].rstrip()], limit=1, simplify=True) == None:  
                
                logger.info(f"Para scrapear, pero no es el caso en este código |Ciudad: {element[0]} | Zipcode: {element[1]} | Orden del dataframe: {pos}")
    
                zipCodeDef = ["ERROR2","ERROR","ERROR",element[1]]
                logger.info(f"No Scrapeado: {zipCodeDef}")

        else:
            if pos in [ele[0]-1 for ele in GetThings(cur, selection="ID", where=["Zipcode", element[1].rstrip()])]:
                logger.info(f"Sin procesar |City: {element[0]} |Zipcode: {element[1]} | Orden del dataframe: {pos}")
                continue
            else:
                logger.info(f"Ya guardado en BBDD  | City: {element[0]} | Zipcode: {element[1]} | Orden del dataframe: {pos}")
                zipCodeDef = zipCodeManipulation(city=element[0], zipcode=element[1].rstrip(), saved = True)
                logger.info(f"Devuelto de query: {zipCodeDef}")

        PrepareCon(con, cur, values=[zipCodeDef[0],zipCodeDef[1],zipCodeDef[2],zipCodeDef[3],pos], option="insert", verbose=False)

    except:
        logger.info(f"No encontrado nada en ciudad: {element[0]}, zipcode: {element[1]}")
        logger.info("--------------------------------------------")
        zipCodeDef= ["ERROR3","ERROR","ERROR",element[1]]
        PrepareCon(con, cur, values=[zipCodeDef[0],zipCodeDef[1],zipCodeDef[2],zipCodeDef[3],pos], option="insert", verbose=False)
        continue


driver.close()



# -----------------------------
# Transformación del scrapeo formateado a dataframe de Pandas
# -----------------------------

sqlToList = cur.execute(f"SELECT Country,Region,City,Zipcode,id_ori FROM {tableMain}").fetchall()

df = pd.DataFrame(sqlToList, columns=["Country","Region","City","Zipcode"])

df.to_csv("ScrappedDB.csv")


# Cierre de base de datos final
con.close()




