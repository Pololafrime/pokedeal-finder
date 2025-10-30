import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="PokéDeal Finder", page_icon="💳", layout="wide")
st.title("💳 PokéDeal Finder — Leboncoin")
st.markdown("Récupère les annonces Pokémon depuis Leboncoin avec images et liens cliquables !")

# =====================
# Paramètres utilisateur
# =====================
search_text = st.text_input("Rechercher une carte ou mot-clé", "pokemon")
max_price = st.slider("Prix maximum (€)", 0, 500, 100)
num_pages = st.slider("Nombre de pages à récupérer", 1, 3, 1)  # Leboncoin limite souvent

# =====================
# Récupération multi-pages
# =====================
annonces = []
headers = {
    "User-Agent": "Mozilla/5.0"
}

for page in range(1, num_pages+1):
    url = f"https://www.leboncoin.fr/recherche?category=39&text={search_text}&page={page}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        st.warning(f"Impossible de récupérer la page {page} : {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("li", {"data-qa-id": "aditem_container"})

    for item in items:
        # Titre
        title_tag = item.find("p", {"data-qa-id": "aditem_title"})
        title = title_tag.text.strip() if title_tag else "N/A"

        # Prix
        price_tag = item.find("span", {"data-qa-id": "aditem_price"})
        price_text = price_tag.text.strip().replace("€", "").replace("\u202f", "").replace(",", ".") if price_tag else "0"
        try:
            price = float(price_text)
        except:
            price = 0

        # Lien
        link_tag = item.find("a", href=True)
        link = "https://www.leboncoin.fr" + link_tag['href'] if link_tag else ""

        # Image
        img_tag = item.find("img")
        img_url = img_tag['src'] if img_tag else ""

        # Score rentabilité sécurisé
        try:
            score = round((price*1.2 - price) / (price*1.2) * 100, 1)
        except:
            score = 0

        annonces.append({
            "Nom": title,
            "Prix (€)": price,
            "Lien": f"[Voir annonce]({link})",
            "Image": img_url,
            "Score Rentabilité": score
        })

    time.sleep(1)  # pause pour limiter les requêtes

# =====================
# Création DataFrame et filtrage
# =====================
df = pd.DataFrame(annonces)

# Colonnes numériques sécurisées
for col in ["Prix (€)", "Score Rentabilité"]:
    if col not in df.columns:
        df[col] = 0
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Filtrer par prix max
df_filtered = df[df["Prix (€)"] <= max_price].sort_values("Score Rentabilité", ascending=False)

# =====================
# Affichage Streamlit
# =====================
if not df_filtered.empty:
    for idx, row in df_filtered.iterrows():
        st.markdown(f"### {row['Nom']}")
        if row['Image']:
            st.image(row['Image'], width=150)
        st.markdown(f"**Prix :** {row['Prix (€)']} € | **Score Rentabilité :** {row['Score Rentabilité']} %")
        st.markdown(f"{row['Lien']}")
        st.markdown("---")
else:
    st.info("Aucune annonce ne correspond aux filtres sélectionnés.")

st.info("Les scores de rentabilité sont basés sur une estimation simple (+20% prix marché).")



