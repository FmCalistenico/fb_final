from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import getpass
import logging
from datetime import datetime
import random

class FacebookCommentClicker:
    def __init__(self, urls, scroll_count=100, click_delay=2):
        self.setup_logging()
        self.urls = urls
        self.max_scroll_count = scroll_count
        self.click_delay = click_delay
        self.user = getpass.getuser()
        self.comment_boxes = set()
        self.comentarios_respuestas = []

    def setup_logging(self):
        log_directory = "facebook_logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        log_filename = os.path.join(
            log_directory, 
            f'facebook_comments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()

            # Configuración de datos de usuario para evitar inicios de sesión manuales
            user_data_dir = f"C:\\Users\\{self.user}\\AppData\\Local\\Google\\Chrome\\User Data"
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument("--profile-directory=Default")
            options.add_argument("--disable-notifications")

            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            self.logger.error(f"Error al configurar el driver: {e}")
            raise

    def click_main_page(self, driver):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            body = driver.find_element(By.TAG_NAME, 'body')
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(body, 100, 100)
            actions.click()
            actions.perform()
            time.sleep(1)
            self.logger.info("Clic realizado en la página principal")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en la página principal: {e}")
            return False

    def click_comment_box(self, driver, element, current_scroll_count):
        try:
            actions = ActionChains(driver)
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                element
            )
            time.sleep(1.5)

            driver.execute_script("""
                arguments[0].style.border = '3px solid green';
                arguments[0].style.backgroundColor = 'lightgreen';
            """, element)

            actions.move_to_element(element)
            actions.click()
            actions.perform()
            time.sleep(random.uniform(1, 2))

            tipo_comentario = "Positivo" if current_scroll_count < self.max_scroll_count * 0.5 else "Neutro"
            respuesta = responder_comentario(tipo_comentario)
            comentario = element.get_attribute("aria-label") or "Comentario sin texto"

            self.comentarios_respuestas.append({
                "Comentario": comentario,
                "Respuesta": respuesta,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            element.send_keys(respuesta)
            time.sleep(0.5)
            element.send_keys(Keys.RETURN)

            self.logger.info(f"Comentario realizado: {respuesta}")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en el elemento: {e}")
            return False

    def perform_scroll(self, driver):
        try:
            scroll_height = random.randint(300, 500)
            driver.execute_script(f"window.scrollBy({{top: {scroll_height}, left: 0, behavior: 'smooth'}});")
            time.sleep(random.uniform(1.5, 2.5))
            return True
        except Exception as e:
            self.logger.error(f"Error durante el scroll: {e}")
            return False

    def scan_and_click_page(self, driver):
        try:
            current_scroll_count = 0
            if not self.click_main_page(driver):
                self.logger.error("No se pudo hacer clic inicial en la página principal")
                return
            time.sleep(3)

            while current_scroll_count < self.max_scroll_count:
                comment_boxes_found = False
                elements = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']")
                for element in elements:
                    if self.click_comment_box(driver, element, current_scroll_count):
                        comment_boxes_found = True
                        break

                if not comment_boxes_found:
                    self.perform_scroll(driver)

                current_scroll_count += 1
        except Exception as e:
            self.logger.error(f"Error durante el escaneo: {e}")

    def run(self):
        driver = None
        try:
            driver = self.setup_driver()
            for url in self.urls:
                self.logger.info(f"Iniciando navegación a {url}")
                driver.get(url)
                time.sleep(5)
                self.scan_and_click_page(driver)
        except Exception as e:
            self.logger.error(f"Error en la ejecución principal: {e}")
        finally:
            if driver:
                driver.quit()
                self.logger.info("Navegador cerrado correctamente")


def responder_comentario(tipo):
    respuestas = {
        "Positivo": ["¡Gracias por tu buen comentario!", "¡Nos alegra que te haya gustado!"],
        "Neutro": ["Gracias por tu opinión.", "Valoramos tus comentarios."]
    }
    return random.choice(respuestas.get(tipo, ["Gracias por tu comentario."]))


if __name__ == "__main__":
    urls = ["https://web.facebook.com/profeMikhailKrasnov"]
    clicker = FacebookCommentClicker(urls=urls, scroll_count=5, click_delay=2)
    clicker.run()
