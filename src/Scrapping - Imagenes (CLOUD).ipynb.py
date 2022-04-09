# %% [markdown]
# ### Importación de librerías

# %%
from selenium import webdriver # Webscrapping bot
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromiumOptions

from selenium.webdriver.common.by import By

# %%
import logging # Para generar logs
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

import datetime
import os
import time

# %%
import pandas as pd #Manejo de dataframes

# %% [markdown]
# ### Variables a modificar para adaptar el código

# %%
urlToScrap ="https://images.google.com/"
deleteOldLogs = True

pathToDF = ""
fileToDF = "ProdsToScrap.csv"

webdriverToUse = "chromium"

# %% [markdown]
# ### Pequeñas funciones de apoyo

# %%
# Esta función se ha creado para mejorar comprensión de código en la configuración de logs

def UTCFormatter(logFormatter):
    '''
    Recibe un formatter de logeo
    Devuelve el horario a tiempo GMT
    '''
    logFormatter.converter = time.gmtime
    return logFormatter

# %% [markdown]
# ### Configuración de logs

# %%
# Se inicia el proceso de registro de logs a nivel de INFO.
logger = logging.getLogger('ScrapLog')
logger.setLevel(logging.INFO)

# Variables que determinan apartados posteriores
timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H-%M-%S')
filename=f'ScrapImages{timestamp}.log'
formatter = logging.Formatter('[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

# %%
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

# %% [markdown]
# ### Importación de datos

# %%
df = pd.read_csv(f"{pathToDF}{fileToDF}")
df.drop(columns=df.columns[0], axis=1, inplace=True)

# %%
print(df.shape)
df.head(2)

# %% [markdown]
# ### Lógica del Scrapping

# %%
def ScrapFunction(prodToScrap, urlToScrap, webdriverUsed="chromium"):

    logger.info(f"Started with: {prodToScrap}")

    if webdriverToUse != "firefox":
        opts = ChromiumOptions()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--incognito")
        opts.add_argument("start-maximized")
        opts.add_argument("window-size=1920,1080")
        # opts.add_argument("--headless")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=opts)
    else:
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--incognito")
        opts.add_argument("window-size=1400,600")
        driver = webdriver.Firefox(options=opts)


    driver.set_page_load_timeout(30)
    driver.set_window_size(1920, 1080)

    driver.get(urlToScrap)
    driver.delete_all_cookies()

    acceptCookie = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/span/div/div/div/div[3]/button[2]/div")
    acceptCookie.click()
    driver.implicitly_wait(8)

    selectImageBox = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input")
    driver.implicitly_wait(8)
    selectImageBox.send_keys(prodToScrap)
    selectImageBox.send_keys(Keys.ENTER)

    selectImage = driver.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[4]/div[1]/div/div/div/div[1]/div[1]/span/div[1]/div[1]/div[1]/a[1]/div[1]/img")
    selectImage.click()

    driver.implicitly_wait(8)
    driver.refresh()
    driver.implicitly_wait(8)

    urlImage = driver.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[4]/div[2]/div[3]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[2]/div/a/img").get_attribute("src")

    print(urlImage)

    logger.info(f"Scrapped: {urlImage}")
    
    driver.close()

    return urlImage

# %%
print("Starting Webscrapping!")

for position, element in enumerate(df["name"].iloc[:10].tolist()):
    urlScrapped = ScrapFunction(element,urlToScrap,webdriverUsed=webdriverToUse)
    df.loc[df.index[position], 'url'] = urlScrapped

# %%
df.head()

# %%
df.to_csv("Test1.csv")


