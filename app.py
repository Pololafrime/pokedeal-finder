import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

st.set_page_config(page_title="PokéDeal Finder", page_icon="💳", layout="wide")
st.title("💳 PokéDeal Finder — Leboncoin + Selenium")
st.markdown("Scrape les vraies annonces Pokémon depuis Leboncoin avec un navigateur automatisé 🕵️‍♂️")

# =====================
# Paramètres utilisateur
# =====================
search_text = st.text_input("Rechercher une carte ou mot-clé", "pokemon")
max_price = st.slider("Prix maximum (€)", 0, 500, 100)
num_pages = st.slider("Nombre de pages à scanner", 1, 3, 1)

# =====================
# Fonction de scraping
# =====================
def scrape_leboncoin(search_text, num_pages):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    annonces = []

    for page in range(1, num_pages + 1):
        url = f"https://www.leboncoin.fr/recherche?category=39&text={search_text}&page={page}"
        st.write(f"🔎 Lecture de la page {page} ...")
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
    return annonces

# =====================
# Bouton de lancement
# =====================
if st.button("🔄 Lancer le scan Leboncoin"):
    with st.spinner("Recherche d'annonces Pokémon en cours..."):
        annonces = scrape_leboncoin(search_text, num_pages)
        if not annonces:
            st.error("Aucune annonce trouvée 😔")
        else:
            df = pd.DataFrame(annonces)

            # Nettoyage du prix
            df["Prix (€)"] = (
                df["Prix"]
                .str.replace("€", "")
                .str.replace("\u202f", "")
                .str.replace(",", ".")
                .astype(float, errors="ignore")
            )

            df = df[df["Prix (€)"] <= max_price]

            st.success(f"{len(df)} annonces trouvées ✅")
            for _, row in df.iterrows():
                st.markdown(f"### {row['Nom']}")
                if row["Image"]:
                    st.image(row["Image"], width=150)
                st.markdown(f"**Prix :** {row['Prix (€)']} €")
                st.markdown(f"[Voir l'annonce]({row['Lien']})")
                st.markdown("---")




