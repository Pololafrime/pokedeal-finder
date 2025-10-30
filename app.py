import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# =====================
# CONFIGURATION DE LA PAGE
# =====================
st.set_page_config(page_title="PokéDeal Finder", page_icon="💳", layout="wide")
st.title("💳 PokéDeal Finder — Leboncoin (version stable Render)")
st.markdown("Scrape les vraies annonces Pokémon depuis Leboncoin 🕵️‍♂️")

# =====================
# PARAMÈTRES UTILISATEUR
# =====================
search_text = st.text_input("Rechercher une carte ou un mot-clé", "pokemon")
max_price = st.slider("Prix maximum (€)", 0, 500, 100)
num_pages = st.slider("Nombre de pages à scanner", 1, 3, 1)

# =====================
# FONCTION DE SCRAPING
# =====================
def scrape_leboncoin(search_text, num_pages):
    # ⚙️ Configuration Chrome headless
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920x1080")

    # ✅ Nouvelle méthode compatible Selenium 4.10+
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    annonces = []

    for page in range(1, num_pages + 1):
        url = f"https://www.leboncoin.fr/recherche?category=39&text={search_text}&page={page}"
        st.write(f"🔎 Lecture de la page {page} : {url}")
        driver.get(url)
        time.sleep(3)

        cards = driver.find_elements(By.CSS_SELECTOR, "[data-qa-id='aditem_container']")
        for card in cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_title']").text
                price = card.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_price']").text
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                img = card.find_element(By.TAG_NAME, "img").get_attribute("src")
                annonces.append({
                    "Nom": title,
                    "Prix": price,
                    "Lien": link,
                    "Image": img
                })
            except Exception:
                continue

    driver.quit()
    return pd.DataFrame(annonces)

# =====================
# INTERFACE UTILISATEUR
# =====================
if st.button("🔄 Lancer le scan Leboncoin"):
    with st.spinner("Recherche d'annonces Pokémon en cours..."):
        df = scrape_leboncoin(search_text, num_pages)

        if df.empty:
            st.error("Aucune annonce trouvée 😔")
        else:
            # Nettoyage du prix
            df["Prix (€)"] = (
                df["Prix"]
                .str.replace("€", "")
                .str.replace("\u202f", "")
                .str.replace(",", ".")
                .str.extract(r"(\d+\.?\d*)")[0]
                .astype(float)
            )

            df = df[df["Prix (€)"] <= max_price]

            st.success(f"{len(df)} annonces trouvées ✅")

            for _, row in df.iterrows():
                with st.container():
                    cols = st.columns([1, 3])
                    with cols[0]:
                        if pd.notna(row["Image"]):
                            st.image(row["Image"], width=120)
                    with cols[1]:
                        st.markdown(f"### {row['Nom']}")
                        st.markdown(f"💰 **Prix :** {row['Prix (€)']} €")
                        st.markdown(f"[🔗 Voir l'annonce]({row['Lien']})")
                        st.markdown("---")
