import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="PokéDeal Finder", page_icon="💳", layout="wide")
st.title("💳 PokéDeal Finder — Live Vinted")
st.markdown("Trouve les meilleures **affaires Pokémon** sur Vinted en temps réel !")

# =====================
# 1️⃣ Paramètres utilisateur
# =====================
search_text = st.text_input("Rechercher une carte ou mot-clé", "pokemon")
max_price = st.slider("Prix maximum (€)", 0, 500, 100)

# =====================
# 2️⃣ Récupérer les annonces depuis Vinted
# =====================
url = f"https://www.vinted.fr/api/v2/items?search_text={search_text}&per_page=50"
headers = {
    "User-Agent": "Mozilla/5.0"  # Permet de passer quelques restrictions
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    st.error(f"Erreur lors de la récupération des annonces : {e}")
    st.stop()

# =====================
# 3️⃣ Extraire les infos essentielles
# =====================
annonces = []
for item in data.get('items', []):
    prix = float(item.get('price', 0))
    annonces.append({
        "Nom": item.get('title', 'N/A'),
        "Prix (€)": prix,
        "Lien": "https://www.vinted.fr" + item.get('path', ''),
        # Score de rentabilité simulé : prix marché estimé - prix annonce
        "Score Rentabilité": round((prix*1.2 - prix) / (prix*1.2) * 100, 1)  # +20% prix marché hypothétique
    })

df = pd.DataFrame(annonces)

# =====================
# 4️⃣ Filtrer selon le prix max
# =====================
df_filtered = df[df["Prix (€)"] <= max_price].sort_values("Score Rentabilité", ascending=False)

# =====================
# 5️⃣ Affichage Streamlit
# =====================
st.dataframe(df_filtered, use_container_width=True)

st.info("➡️ Les scores de rentabilité sont calculés sur une estimation simple (+20% prix marché).")
st.markdown("⚠️ Pour une vraie analyse, il faudra connecter une base de prix marché (CardMarket / eBay).")
