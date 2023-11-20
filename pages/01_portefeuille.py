import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit_echarts
from streamlit_extras.switch_page_button import switch_page
import sqlite3

st.set_page_config(page_title="portefeuille", layout="wide")

st.title("Portefeuille")

# expander1 = st.expander(f"Portefeuille CASH",)
# expander2 = st.expander(f"Portefeuille Crypto IMMO")
# expander3 = st.expander(f"Portefeuille Crypto")
# expander4 = st.expander(f"Portefeuille PEA")


conn = sqlite3.connect("./data/db.sqlite3")
cursor = conn.cursor()
data = cursor.execute("SELECT * FROM portefeuille_portefeuille")
df = pd.DataFrame(data, columns=[x[0] for x in cursor.description])
conn.close()

type_actifs = df["type_actif"].unique().tolist()


# Fonction pour calculer le total par classe d'actif
def calculer_total_par_classe(df):
    total_par_classe = df.groupby("type_actif")["value"].sum().reset_index()
    return total_par_classe


# Calcul et affichage des totaux à gauche
total_par_classe = calculer_total_par_classe(df)

option = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "Access From",
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "label": {"show": False, "position": "center"},
            "emphasis": {"label": {"show": True, "fontSize": 40, "fontWeight": "bold"}},
            "labelLine": {"show": False},
            "data": [0],
        }
    ],
}

# Affichage des expanders
for classe in type_actifs:
    classe_df = df[df["type_actif"] == classe].sort_values(by="value", ascending=False)

    # Calcul du total
    total = classe_df["value"].sum().round(2)

    liste_colonne = ["token", "description", "unit_price", "amount", "value"]

    expander =  st.expander(f"{classe} - Total: {total} €")
    col1, col2 = expander.columns(2)
    with col1:
        st.dataframe(classe_df[liste_colonne], hide_index=True)

    with col2:
        df_visu = classe_df[["value","token"]]
        option['series'][0]['data'] = [dict(value=row['value'], name=row['token']) for index, row in classe_df.iterrows()]

        streamlit_echarts.st_echarts(option,height="400px")

