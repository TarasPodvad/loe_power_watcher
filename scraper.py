from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from config import URL, GROUP_NAME

def fetch_group_lines():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{GROUP_NAME}')]"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        lines = [el.get_text(strip=True) for el in soup.find_all(string=lambda t: GROUP_NAME in t)]

        return "\n".join(lines)

    finally:
        driver.quit()
