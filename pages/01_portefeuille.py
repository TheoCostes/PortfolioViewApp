import sys
import numpy as np

sys.path.insert(0, "..")

import streamlit as st
import pandas as pd
import streamlit_echarts
import sqlite3
from datetime import datetime
import logging
from streamlit_extras.chart_container import chart_container
from streamlit_extras.metric_cards import style_metric_cards

from utils_api import get_prices


def connect_to_database():
    conn = sqlite3.connect("./data/db.sqlite3")
    cursor = conn.cursor()
    data = cursor.execute(f"SELECT * FROM portefeuille_portefeuille where id_user = '{st.session_state['username']}'")
    df_total = pd.DataFrame(data, columns=[x[0] for x in cursor.description])
    conn.close()
    return df_total


def update_prices(df, first_time=False):
    df = get_prices(df)
    df["id_portefeuille"] = df["id_portefeuille"].apply(lambda x: x + 1)
    df["last_update"] = pd.to_datetime(df["last_update"], format="mixed")
    if first_time:
        df["id"] = df["id"].apply(lambda x: x + len(df) + 1)
        conn = sqlite3.connect("./data/db.sqlite3")
        df.to_sql("portefeuille_portefeuille", con=conn, index=False, if_exists="append")
        conn.close()
    return df


def process_data(df_total, df_last):
    df_total['last_update'] = pd.to_datetime(df_total['last_update'], format='mixed')
    df_agg = (
        df_total.groupby(["id_portefeuille", "type_actif"])
        .agg({"value": np.sum, "last_update": np.max})
        .reset_index()
    )
    df_agg["last_update"] = pd.to_datetime(df_agg["last_update"], format="mixed")
    df_agg = (
        df_agg.groupby(
            ["id_portefeuille", pd.Grouper(key="last_update", freq="D"), "type_actif"]
        )["value"]
        .sum()
        .reset_index()
    )
    df_agg = pd.concat(
        [
            df_agg,
            df_last.groupby(["last_update", "type_actif"])
            .agg({"value": np.sum, "id_portefeuille": np.max})
            .reset_index(),
        ]
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

    with col1:
        option["series"][0]["data"] = [
            dict(value=row["value"], name=row["type_actif"])
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


def display_expanders(df, type_actifs):
    for classe in type_actifs:
        classe_df = df[df["type_actif"] == classe].sort_values(by="value", ascending=False)
        total = classe_df["value"].sum().round(2)

        expander = st.expander(f"{classe}")
        col1, col2 = expander.columns(2)

        liste_colonne = ["token", "description", "unit_price", "amount", "value"]
        with col1:
            st.empty()
            st.dataframe(classe_df[liste_colonne], hide_index=True)

        with col2:
            df_visu = classe_df[["value", "token"]]
            option["series"][0]["data"] = [
                dict(value=row["value"], name=row["token"])
                for index, row in classe_df.iterrows()
            ]

            streamlit_echarts.st_echarts(option, height="400px")


# Configuration de la page Streamlit
st.set_page_config(page_title="portefeuille", layout="wide")
logging.basicConfig(level=logging.DEBUG)

if not st.session_state["authentication_status"]:
    st.warning("**Access is restricted. Please go connect !**")
else:
    try:
        df_total = connect_to_database()
        df_last = df_total[df_total["id_portefeuille"] == max(df_total["id_portefeuille"])]

        type_actifs = df_last["type_actif"].unique().tolist()

        col = st.columns(3, gap="large")
        col[0].title("Portefeuille")
        col[2].title("")
        masquer_valeurs = col[2].toggle("mode discret")
        st.write("")

        if datetime.strptime(df_last["last_update"].min(), "%Y-%m-%d %H:%M:%S").date() < datetime.now().date():
            with st.spinner("Récupération des prix ..."):
                df_last = update_prices(df_last, first_time=True)
        else:
            with st.spinner("Récupération des prix ..."):
                df_last = update_prices(df_last)

        df_agg = process_data(df_total, df_last)

        option = configure_pie_chart_option()

        col1, col2 = st.columns(2)
        display_pie_and_evolution(df_agg, df_last, col1, col2)

        col = st.columns(len(type_actifs) + 1)
        display_asset_value_cards(df_last, col, type_actifs, masquer_valeurs)

        style_metric_cards()

        for classe in type_actifs:
            # display_expanders(df_last, type_actifs)
            classe_df = df_last[df_last["type_actif"] == classe].sort_values(by="value", ascending=False)

            # Calcul du total
            total = classe_df["value"].sum().round(2)

            expander = st.expander(f"{classe}")
            col1, col2 = expander.columns(2)

            liste_colonne = ["token", "description", "unit_price", "amount", "value"]
            with col1:
                st.empty()
                st.dataframe(classe_df[liste_colonne], hide_index=True)

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