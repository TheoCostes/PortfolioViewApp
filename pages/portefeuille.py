import sys
import numpy as np

sys.path.insert(0, "..")

import streamlit as st
import pandas as pd
import streamlit_echarts
import sqlite3
import logging
from streamlit_extras.chart_container import chart_container
from streamlit_extras.metric_cards import style_metric_cards
import s3fs
from st_files_connection import FilesConnection


def process_data(df_total, df_last):
    df_total['last_update'] = pd.to_datetime(df_total['last_update'], format='mixed')
    df_agg = (
        df_total.groupby(["type_actif", "id_portefeuille", "last_update"])
        .agg({"value": np.sum})
        .reset_index()
    )

    return df_agg


def configure_pie_chart_option():
    return {
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


def plot_portfolio_evolution(df, x, y, color):
    max_ids = df.groupby("last_update")["id_portefeuille"].max().reset_index()
    result_df = pd.merge(max_ids, df, on=["last_update", "id_portefeuille"], how="left")
    with chart_container(result_df):
        st.write("Portfolio evolution par type d'actif")
        st.line_chart(data=result_df, x=x, y=y, color=color, use_container_width=True)


def display_pie_and_evolution(df_agg,df_last, col1, col2):
    df_actif = df_last.groupby("type_actif").sum("value").reset_index()
    df_visu = df_actif[["value", "type_actif"]]
    total = np.sum(df_actif['value'])
    with col1:
        option["series"][0]["data"] = [
            dict(value=round(row["value"]/total * 100,1) , name=row["type_actif"])
            for index, row in df_visu.iterrows()
        ]
        streamlit_echarts.st_echarts(option, height="400px")

    with col2:
        plot_portfolio_evolution(df_agg, "last_update", "value", "type_actif")


def display_asset_value_cards(df, col, type_actifs, masquer_valeurs):
    if masquer_valeurs:
        col[0].metric("Asset value", value="*****")
    else:
        col[0].metric(label="Asset value", value=df["value"].sum().round(2))

    for i, actif in enumerate(type_actifs):
        category_data = df[df["type_actif"] == actif]
        value = category_data["value"].sum().round(2)

        if masquer_valeurs:
            col[i + 1].metric(f"{actif}", value="*****")
        else:
            col[i + 1].metric(f"{actif}", value=value)


# Configuration de la page Streamlit
st.set_page_config(page_title="portefeuille", layout="wide")
logging.basicConfig(level=logging.DEBUG)

conn = st.connection('s3', type=FilesConnection)
df_total = conn.read("dashboard-invest/portefeuille.csv", input_format="csv", ttl=600)

if not st.session_state["authentication_status"]:
    st.warning("**Access is restricted. Please go connect !**")
else:
    try:
        df_last = df_total[(df_total['id_user'] == st.session_state["username"]) & (df_total["id_portefeuille"] == max(df_total["id_portefeuille"]))]

        type_actifs = df_last["type_actif"].unique().tolist()

        col = st.columns(3, gap="large")
        col[0].title("Portefeuille")
        col[2].title("")
        masquer_valeurs = col[2].toggle("mode discret")
        st.write("")

        df_agg = process_data(df_total, df_last)
        option = configure_pie_chart_option()

        col1, col2 = st.columns(2)
        display_pie_and_evolution(df_agg, df_last, col1, col2)

        col = st.columns(len(type_actifs) + 1)
        display_asset_value_cards(df_last, col, type_actifs, masquer_valeurs)

        style_metric_cards()

        for classe in type_actifs:
            # display_expanders(df_last, type_actifs)
            total_par_actif = df_total[df_total["type_actif"] == classe].sort_values(by="value", ascending=False)
            classe_df = df_last[df_last["type_actif"] == classe].sort_values(by="value", ascending=False)

            # Calcul du total
            total = classe_df["value"].sum().round(2)

            expander = st.expander(f"{classe}")
            col1, col2 = expander.columns(2)

            liste_colonne = ["last_update","token", "description", "unit_price", "amount", "value"]
            with col1:
                st.empty()
                # st.dataframe(classe_df[liste_colonne], hide_index=True)
                st.dataframe(total_par_actif[liste_colonne])
                plot_portfolio_evolution(total_par_actif[liste_colonne], "last_update", "value", "token")

            with col2:
                df_visu = classe_df[["value", "token"]]
                option["series"][0]["data"] = [
                    dict(value=row["value"], name=row["token"])
                    for index, row in classe_df.iterrows()
                ]

                streamlit_echarts.st_echarts(option, height="400px")
    except Exception as e:
        uploaded_file = st.file_uploader("Upload a csv file containing portfolio history", type="csv")
        if uploaded_file is not None:
            dataframe = pd.read_csv(uploaded_file)
            st.write(dataframe)
            conn = sqlite3.connect("./data/db.sqlite3")
            dataframe.to_sql("portefeuille_portefeuille", con=conn, index=False, if_exists="append")
            conn.close()
            st.rerun()