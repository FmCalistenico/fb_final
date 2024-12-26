from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    WebDriverException, 
    NoSuchElementException, 
    ElementClickInterceptedException
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import logging
from datetime import datetime
import random

class FacebookCommentClicker:
    def __init__(self, urls, scroll_count=100, click_delay=2):
        self.setup_logging()
        self.urls = urls
        self.max_scroll_count = scroll_count
        self.click_delay = click_delay
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
            options.add_argument("--disable-notifications")
            options.add_argument("--headless")  # Headless mode for deployment
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")
            options.add_argument("--window-size=1920,1080")

            # Optional: Set binary location if needed
            chrome_binary = os.getenv("CHROME_BINARY", "/usr/bin/google-chrome")
            if os.path.exists(chrome_binary):
                options.binary_location = chrome_binary

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
            body.click()
            time.sleep(1)
            self.logger.info("Clic realizado en la página principal")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en la página principal: {e}")
            return False

    def click_comment_box(self, driver, element):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1.5)
            element.click()
            response = responder_comentario("Neutro")
            element.send_keys(response)
            element.send_keys(Keys.RETURN)
            self.logger.info(f"Comentario realizado: {response}")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en el elemento: {e}")
            return False

    def perform_scroll(self, driver):
        try:
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(1.5)
            return True
        except Exception as e:
            self.logger.error(f"Error durante el scroll: {e}")
            return False

    def load_more_comments(self, driver):
        try:
            more_buttons = driver.find_elements(By.XPATH, "//span[contains(text(),'Ver más comentarios')]")
            for btn in more_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(2)
            return True
        except Exception as e:
            self.logger.error(f"Error al cargar más comentarios: {e}")
            return False

    def scan_and_click_page(self, driver):
        try:
            for _ in range(self.max_scroll_count):
                self.load_more_comments(driver)
                comment_boxes = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']")
                for box in comment_boxes:
                    self.click_comment_box(driver, box)
                self.perform_scroll(driver)
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
    urls = ["https://www.facebook.com/"]
    clicker = FacebookCommentClicker(urls=urls, scroll_count=5, click_delay=2)
    clicker.run()
