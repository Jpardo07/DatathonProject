
# Importación de librerías


from selenium import webdriver # Webscrapping bot
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromiumOptions

from selenium.webdriver.common.by import By


import logging # Para generar logs
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

import datetime
import os
import time


import pandas as pd # Manejo de dataframes


# Variables a modificar para adaptar el código


urlToScrap ="https://images.google.com/"
deleteOldLogs = True

pathToDF = ""
fileToDF = "UrlMissing.csv"

webdriverToUse = "firefox"


# Pequeñas funciones de apoyo

# Esta función se ha creado para mejorar comprensión de código en la configuración de logs
def UTCFormatter(logFormatter):
    '''
    Recibe un formatter de logeo
    Devuelve el horario a tiempo GMT
    '''
    logFormatter.converter = time.gmtime
    return logFormatter


# Configuración de logs


# Se inicia el proceso de registro de logs a nivel de INFO.
logger = logging.getLogger('ScrapLog')
logger.setLevel(logging.INFO)

# Variables que determinan apartados posteriores
timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H-%M-%S')
filename=f'ScrapImages{timestamp}.log'
formatter = logging.Formatter('[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')


'''
Indican como se debe crear el archivo de log
Si "deleteOldLogs" es True, sólo se conservará el último archivo de log
'''

if deleteOldLogs ==True:
    listFilesinCWD = os.listdir(os.getcwd())
    for element in listFilesinCWD:
        if element.endswith(".log"):
            os.remove(os.path.join(os.getcwd(), element))

fileHandler = logging.FileHandler(filename=filename)
logging.Formatter.converter = time.gmtime

fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(UTCFormatter(formatter))
logger.addHandler(fileHandler)


# Importación de datos
df = pd.read_csv(f"{pathToDF}{fileToDF}")


# Lógica del Scrapping

def ScrapFunction(prodToScrap, urlToScrap, driver):
    try:
        logger.info(f"Started with: {prodToScrap}")

        driver.implicitly_wait(5)
        driver.delete_all_cookies()
        driver.implicitly_wait(5)
        driver.get(urlToScrap)
        driver.implicitly_wait(5)
        
        try:
            acceptCookie = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/span/div/div/div/div[3]/button[2]/div")
            acceptCookie.click()
        except:
            pass
        
        selectImageBox = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input")

        selectImageBox.send_keys(prodToScrap)
        selectImageBox.send_keys(Keys.ENTER)
        driver.implicitly_wait(5)
        
        selectImage = driver.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[4]/div[1]/div/div/div/div[1]/div[1]/span/div[1]/div[1]/div[1]/a[1]/div[1]/img")
        selectImage.click()

        driver.implicitly_wait(5)
        driver.refresh()
        driver.implicitly_wait(5)

        urlImage = driver.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[4]/div[2]/div[3]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[2]/div/a/img").get_attribute("src")

        logger.info(f"Scrapped: {urlImage}")

        return urlImage

    except:
        logger.info(f"FUNCTIONERROR: {prodToScrap}")
        return None


print("Starting Webscrapping!")


if webdriverToUse != "firefox":
    opts = ChromiumOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--incognito")
    opts.add_argument("start-maximized")
    opts.add_argument("window-size=1920,1080")
    opts.add_argument("--headless")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=opts)
else:
    opts = FirefoxOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--incognito")
    opts.add_argument("start-maximized")
    opts.add_argument("window-size=1920,1080")
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

driver.set_page_load_timeout(30)
driver.set_window_size(1920, 1080)

for position, element in enumerate(df["name"].tolist()):
    try:
        urlScrapped = ScrapFunction(element,urlToScrap,driver)
        df.loc[df.index[position], 'url'] = urlScrapped
        if position % 10:
            df.to_csv("Scrap.csv")
    except:
        logger.info(f"Scrapped: {urlImage}")
        if position % 10:
            df.to_csv("Scrap.csv")
        continue

driver.close()


# Exportación de datos

df.to_csv("ScrapDef.csv", index=False)


