import sys
sys.path.insert(0, "..")

import streamlit as st
import pandas as pd
import streamlit_echarts
import sqlite3
from datetime import datetime
import logging
from streamlit_extras.chart_container import chart_container
from streamlit_extras.metric_cards import style_metric_cards


from  utils_api import get_prices

st.set_page_config(page_title="portefeuille", layout="wide")
logging.basicConfig(level=logging.DEBUG)


st.title("Portefeuille")


conn = sqlite3.connect("./data/db.sqlite3")
cursor = conn.cursor()
data = cursor.execute("SELECT * FROM portefeuille_portefeuille")
df_total = pd.DataFrame(data, columns=[x[0] for x in cursor.description])
df = df_total[df_total['last_update'] == max(df_total['last_update'])]
df_agg = df_total.groupby(['last_update', 'type_actif']).sum('value').reset_index()

df_agg['last_update'] = pd.to_datetime(df_agg['last_update'], format='mixed')
df_agg = df_agg.groupby([pd.Grouper(key='last_update', freq='D'), 'type_actif'])['value'].mean().reset_index()

logging.debug('='*100)
type_actifs = df["type_actif"].unique().tolist()

if datetime.strptime(df['last_update'].min(), "%Y-%m-%d, %H:%M:%S").date() < datetime.now().date():
    with st.spinner('Récupération des prix ...'):
        df = get_prices(df)
        logging.debug(df['last_update'].min())
        logging.debug(df)
        logging.debug(len(df))
        df['id'] = df['id'].apply(lambda x : x + len(df) + 1)
        logging.debug(df)
        df.to_sql("portefeuille_portefeuille", con=conn, index=False, if_exists='append')
        conn.close()
else:
    logging.debug("NOT IN RESEARCH PRICE !!!!)")
    conn.close()


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
            "emphasis": {"label": {"show": True, "fontSize": 30, "fontWeight": "bold"}},
            "labelLine": {"show": False},
            "data": [0],
        }
    ],
}

def plot_portfolio_evolution(df, x, y , color):
    with chart_container(df):
        st.write("Portfolio evolution par type d'actif")
        st.line_chart(data=df, x=x, y=y,
                      color=color, use_container_width=True)


liste_colonne = ["token", "description", "unit_price", "amount", "value"]

col1, col2 = st.columns(2)
df_actif = df.groupby('type_actif',).sum('value').reset_index()
logging.debug("df_actif")
logging.debug(df_actif[['type_actif', 'value']])
df_visu = df_actif[["value", "type_actif"]]

with col1:
    option['series'][0]['data'] = [dict(value=row['value'], name=row['type_actif']) for index, row in df_visu.iterrows()]
    streamlit_echarts.st_echarts(option, height="400px")

with col2:
    plot_portfolio_evolution(df_agg, 'last_update', 'value', 'type_actif')

latest_date = df_agg['last_update'].max()
filtered_df = df_agg[df_agg['last_update'] == latest_date]


# Pour chaque catégorie, créer une "card" Streamlit avec la valeur correspondante
col = st.columns(len(type_actifs)+1)
col[0].metric(label='Asset value', value=filtered_df['value'].sum().round(2))
for i, actif in enumerate(type_actifs):
    category_data = filtered_df[filtered_df['type_actif'] == actif]
    value = category_data['value'].round(2).iloc[0]  # Prendre la première valeur (peut-être ajuster en fonction de vos données)

    # Créer une "card" Streamlit
    col[i+1].metric(f"{actif}", value=value)
style_metric_cards()

# Affichage des expanders
for classe in type_actifs:
    classe_df = df[df["type_actif"] == classe].sort_values(by="value", ascending=False)

    # Calcul du total
    total = classe_df["value"].sum().round(2)

    expander = st.expander(f"{classe}")
    col1, col2 = expander.columns(2)

    with col1:
        st.empty()
        st.dataframe(classe_df[liste_colonne], hide_index=True)

    with col2:
        df_visu = classe_df[["value","token"]]
        option['series'][0]['data'] = [dict(value=row['value'], name=row['token']) for index, row in classe_df.iterrows()]

        streamlit_echarts.st_echarts(option,height="400px")

