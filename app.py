import streamlit as st
import pandas as pd

st.set_page_config(page_title="PokéDeal Finder", page_icon="💳", layout="wide")
st.title("💳 PokéDeal Finder")
st.markdown("Trouve les **meilleures affaires Pokémon** sur Vinted et Leboncoin !")

data = {
    "Nom": ["Dracaufeu Base Set", "Mew ex", "Pikachu Promo", "Lugia GX"],
    "Prix (€)": [150, 35, 5, 45],
    "Prix Marché (€)": [200, 50, 10, 60],
    "Lien": [
        "https://www.vinted.fr/item/dracaufeu",
        "https://www.leboncoin.fr/item/mewex",
        "https://www.vinted.fr/item/pikachu",
        "https://www.leboncoin.fr/item/lugia"
    ]
}

df = pd.DataFrame(data)
df["Score Rentabilité"] = ((df["Prix Marché (€)"] - df["Prix (€)"]) / df["Prix Marché (€)"] * 100).round(1)

prix_max = st.slider("Prix maximum (€)", 0, 300, 100)
filtre = df[df["Prix (€)"] <= prix_max]

st.dataframe(
    filtre.sort_values("Score Rentabilité", ascending=False),
    use_container_width=True
)

st.success("Version de démonstration — récupération en ligne des annonces à venir 🔍")
