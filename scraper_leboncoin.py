from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Configuration du navigateur sans interface
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Lancer Chrome headless
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

search_text = "pokemon"
max_pages = 2
annonces = []

for page in range(1, max_pages + 1):
    url = f"https://www.leboncoin.fr/recherche?category=39&text={search_text}&page={page}"
    print(f"🔎 Page {page}: {url}")
    driver.get(url)
    time.sleep(3)  # attendre le chargement JS

    cards = driver.find_elements(By.CSS_SELECTOR, "[data-qa-id='aditem_container']")
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_title']").text
            price = card.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_price']").text
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            img = card.find_element(By.TAG_NAME, "img").get_attribute("src")
            annonces.append({"Nom": title, "Prix": price, "Lien": link, "Image": img})
        except:
            continue

driver.quit()

# Conversion en DataFrame
df = pd.DataFrame(annonces)
df.to_csv("leboncoin_pokemon.csv", index=False)
print(f"✅ {len(df)} annonces récupérées et sauvegardées dans leboncoin_pokemon.csv")
