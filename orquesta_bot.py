from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# --------------------------------
# CONFIGURACIÓN ORQUESTA
# --------------------------------
URL = "http://orquesta.resonanceuy.local:8080"
USUARIO = "cpereira"
PASSWORD = "Reso2024**"   # <-- Cande, acá poné tu pass real

# Texto que debe seleccionar en los combos
PRODUCTO_TEXTO = "PosLink"

# --------------------------------
# INICIAR CHROME
# --------------------------------
def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    return driver

# --------------------------------
# LOGIN EN ORQUESTA
# --------------------------------
def login_orquesta(driver):
    wait = WebDriverWait(driver, 20)

    # Campo usuario
    usuario_input = wait.until(
        EC.visibility_of_element_located((By.ID, "txtUsuario"))
    )
    usuario_input.clear()
    usuario_input.send_keys(USUARIO)

    # Campo password
    pass_input = wait.until(
        EC.visibility_of_element_located((By.ID, "txtPassword"))
    )
    pass_input.clear()
    pass_input.send_keys(PASSWORD)

    # Botón ingresar
    btn_ingresar = wait.until(
        EC.element_to_be_clickable((By.ID, "btnIngresar"))
    )
    btn_ingresar.click()

    print(">>> LOGIN OK")

    # Esperar que cargue el menú
    wait.until(
        EC.presence_of_element_located((By.LINK_TEXT, "Registro de gestiones"))
    )

# --------------------------------
# IR A REGISTRO DE GESTIONES
# --------------------------------
def abrir_registro_gestiones(driver):
    wait = WebDriverWait(driver, 20)

    link = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Registro de gestiones"))
    )
    link.click()

    print(">>> ENTRÉ A REGISTRO DE GESTIONES")

    # Esperar el título de la página
    wait.until(
        EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Registros de gestiones')]"))
    )

# --------------------------------
# SELECCIONAR PRODUCTO = POSLINK
# --------------------------------
def seleccionar_producto(driver):
    wait = WebDriverWait(driver, 20)

    # Caja de texto del combo Producto
    input_prod = wait.until(
        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_rcbProducto_Input"))
    )

    input_prod.click()
    time.sleep(0.5)

    input_prod.send_keys(PRODUCTO_TEXTO)
    time.sleep(1)

    input_prod.send_keys(Keys.ENTER)

    print(">>> FILTRO PRODUCTO = POSLINK aplicado")

# --------------------------------
# PROGRAMA PRINCIPAL
# --------------------------------
def main():
    print(">>> INICIANDO SCRIPT ORQUESTA – versión estable <<<")

    driver = iniciar_driver()
    login_orquesta(driver)
    abrir_registro_gestiones(driver)
    seleccionar_producto(driver)

    print(">>> TODO OK – listo para agregar más filtros")

    time.sleep(9999)

if __name__ == "__main__":
    main()
