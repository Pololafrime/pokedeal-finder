import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="PokéDeal Finder", page_icon="💳", layout="wide")
st.title("💳 PokéDeal Finder — Version Finale")
st.markdown("Récupère plusieurs pages d'annonces Pokémon depuis Vinted avec images et liens cliquables !")

# =====================
# Paramètres utilisateur
# =====================
search_text = st.text_input("Rechercher une carte ou mot-clé", "pokemon")
max_price = st.slider("Prix maximum (€)", 0, 500, 100)
num_pages = st.slider("Nombre de pages à récupérer", 1, 5, 2)

# =====================
# Récupération multi-pages
# =====================
annonces = []

headers = {"User-Agent": "Mozilla/5.0"}

for page in range(1, num_pages+1):
    url = f"https://www.vinted.fr/catalog?search_text={search_text}&page={page}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        st.warning(f"Impossible de récupérer la page {page} : {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("div", {"data-testid": "item-card"})

    for item in items:
        # Titre
        title_tag = item.find("h3")
        title = title_tag.text.strip() if title_tag else "N/A"

        # Prix
        price_tag = item.find("div", {"data-testid": "price"})
        price_text = price_tag.text.strip().replace("€", "").replace(",", ".") if price_tag else "0"
        try:
            price = float(price_text)
        except:
            price = 0

        # Lien
        link_tag = item.find("a", href=True)
        link = "https://www.vinted.fr" + link_tag['href'] if link_tag else ""

        # Image
        img_tag = item.find("img")
        img_url = img_tag['src'] if img_tag else ""

        annonces.append({
            "Nom": title,
            "Prix (€)": price,
            "Lien": f"[Voir annonce]({link})",
            "Image": img_url,
            "Score Rentabilité": round((price*1.2 - price) / (price*1.2) * 100, 1)
        })

    time.sleep(1)  # pause pour ne pas surcharger le site

# =====================
# Création DataFrame et filtrage
# =====================
df = pd.DataFrame(annonces)
df_filtered = df[df["Prix (€)"] <= max_price].sort_values("Score Rentabilité", ascending=False)

# =====================
# Affichage Streamlit avec images
# =====================
if not df_filtered.empty:
    for idx, row in df_filtered.iterrows():
        st.markdown(f"### {row['Nom']}")
        st.image(row['Image'], width=150)
        st.markdown(f"**Prix :** {row['Prix (€)']} € | **Score Rentabilité :** {row['Score Rentabilité']} %")
        st.markdown(f"{row['Lien']}")
        st.markdown("---")
else:
    st.info("Aucune annonce ne correspond aux filtres sélectionnés.")

st.info("Les scores de rentabilité sont basés sur une estimation simple (+20% prix marché).")

