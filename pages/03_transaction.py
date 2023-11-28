from datetime import datetime
from math import ceil
import streamlit as st
import sqlite3
import pandas as pd
import logging

# TODO : edit une transaction


logging.basicConfig(level=logging.DEBUG)

# Initialiser les paramètres de page Streamlit
st.set_page_config(
    page_title="Transactions",
    layout="wide",
)

# Initialiser l'état de session pour la suppression de transactions
if "delete_transaction" not in st.session_state:
    st.session_state["delete_transaction"] = dict()

# Définir l'état initial de l'expander
expanded_state = False


def paginate_dataframe(dataframe, page_size, page_num):
    """Paginer le DataFrame"""
    if page_size is None:
        return None
    offset = page_size * (page_num - 1)
    return dataframe[offset : offset + page_size]


def delete_rows(session_state, transaction_df_page):
    """Supprimer les lignes sélectionnées de la base de données"""
    conn = sqlite3.connect("./data/db.sqlite3")
    cursor = conn.cursor()
    for id, state in session_state.items():
        if id.split("_")[0] == "delete" and state:
            transaction_to_delete_df = transaction_df_page.loc[
                transaction_df_page["id"] == int(id.split("_")[1])
            ]
            transaction_to_delete = transaction_to_delete_df.to_dict(orient="index")[
                transaction_to_delete_df.index[0]
            ]
            update_portefeuille(
                transaction_to_delete,
                transaction_to_delete["type_transaction"],
                delete=True,
            )
            cursor.execute(
                f"DELETE FROM transaction_history WHERE id = ?", (id.split("_")[1],)
            )
    conn.commit()
    conn.close()


def add_token_to_db(record_dict):
    """Ajouter un token à la base de données"""
    conn = sqlite3.connect("./data/db.sqlite3")
    cursor = conn.cursor()
    insert_query = f"INSERT INTO transactions_token ({', '.join(record_dict.keys())})\
                    VALUES ({', '.join(['?' for _ in record_dict.values()])})"
    cursor.execute(insert_query, tuple(record_dict.values()))
    conn.commit()
    conn.close()


def add_database_record(record_dict):
    """Ajouter un enregistrement à la base de données"""
    conn = sqlite3.connect("./data/db.sqlite3")
    cursor = conn.cursor()
    insert_query = f"INSERT INTO transaction_history ({', '.join(record_dict.keys())})\
                    VALUES ({', '.join(['?' for _ in record_dict.values()])})"
    cursor.execute(insert_query, tuple(record_dict.values()))
    conn.commit()
    conn.close()


def update_portefeuille(new_transaction, type_transaction, delete=None):
    conn = sqlite3.connect("./data/db.sqlite3")
    cursor = conn.cursor()
    df_portefeuille = pd.read_sql_query(
        "select * from portefeuille_portefeuille", con=conn
    )
    df_copy_port = df_portefeuille[
        df_portefeuille["id_portefeuille"] == max(df_portefeuille["id_portefeuille"])
    ]
    df_copy_port["last_update"] = datetime.today().date().strftime("%Y-%m-%d")
    update_token_portefeuille(
        conn,
        df_copy_port,
        df_portefeuille,
        new_transaction,
        type_token="1",
        delete=delete,
    )

    if type_transaction == "Swap":
        update_token_portefeuille(
            conn,
            df_copy_port,
            df_portefeuille,
            new_transaction,
            type_token="2",
            delete=delete,
        )


def update_token_portefeuille(
    conn, df_copy_port, df_portefeuille, new_transaction, type_token="1", delete=None
):
    if delete:
        ratio_delete = -1
    else:
        ratio_delete = 1
    len_df = len(df_copy_port)
    max_id = max(df_copy_port["id"])
    max_id_portefeuille = max(df_copy_port["id"])
    if new_transaction["token" + type_token] not in df_portefeuille["token"].unique():
        new_token_portefeuille = {
            "id": max_id + 1,
            "id_portefeuille": max_id_portefeuille + 1,
            "last_update": datetime.today().date().strftime("%Y-%m-%d"),
            "type_actif": new_transaction["type_actif" + type_token],
            "token": new_transaction["token" + type_token],
            "description": new_transaction["description" + type_token],
            "amount": ratio_delete * new_transaction["amount" + type_token],
            "unit_price": new_transaction["unit_price" + type_token],
            "value": new_transaction["value" + type_token],
        }
        pd.concat(
            [df_copy_port, pd.DataFrame(new_token_portefeuille, index=[0])],
            ignore_index=True,
        )

    else:
        df_copy_port.loc[
            df_copy_port["token"] == new_transaction["token" + type_token], ["amount"]
        ] += (ratio_delete * new_transaction["amount" + type_token])
    df_copy_port["id"] = df_copy_port["id"].apply(lambda x: x + len_df + 1)
    df_copy_port["id_portefeuille"] = df_copy_port["id_portefeuille"].apply(
        lambda x: x + 1
    )
    df_copy_port.to_sql(
        "portefeuille_portefeuille", con=conn, index=False, if_exists="append"
    )
    conn.close()


def ajouter_transaction():
    """Ajouter une transaction"""
    global expanded_state
    conn = sqlite3.connect("./data/db.sqlite3")

    df_type_transaction = pd.read_sql_query(
        "SELECT * FROM transactions_type_transac", conn
    )["name"]
    df_portefeuille = pd.read_sql_query("SELECT * FROM portefeuille_portefeuille", conn)

    df_token = pd.read_sql_query("SELECT * FROM transactions_token", conn)
    df_type_actif = df_token["type"]

    conn.close()

    with st.container():
        date = st.date_input("Date", format="DD/MM/YYYY")
        type_transaction = st.selectbox(
            "Type transaction",
            df_type_transaction,
            index=None,
            placeholder="Transaction",
        )

        if type_transaction:
            type_actif1 = st.selectbox(
                "Type actif 1",
                df_type_actif.unique(),
                index=None,
                placeholder="Type actif",
            )
            token1 = st.selectbox(
                "Token 1",
                df_token["symbole"].unique().tolist() + ["autres"],
                index=None,
                placeholder="Token",
            )
            if token1 == "autres":
                token1 = st.text_input("Token 1")
                description1 = st.text_input("Description 1")
                st.write(f"Description 1 = {description1}")
            else:
                description1 = df_token[df_token["symbole"] == token1][
                    "name"
                ].to_string(index=False)
                st.write(f"Description 1 = {description1}")
            amount1 = st.number_input("Amount 1", value=0.0)
            unit_price1 = st.number_input("Unit price 1", value=0.0)
            value1 = st.number_input("Value 1", value=0.0)
        if type_transaction == "Swap":
            st.divider()
            type_actif2 = st.selectbox(
                "Type actif 2",
                df_type_actif.unique(),
                index=None,
                placeholder="Type actif",
            )
            token2 = st.selectbox(
                "Token 2",
                df_token["symbole"].unique(),
                index=None,
                placeholder="Token",
            )
            description2 = df_token[df_token["symbole"] == token2]["name"].to_string(
                index=False
            )
            st.write(f"Description 2 = {description2}")
            amount2 = st.number_input("Amount 2", value=0.0)
            unit_price2 = st.number_input("Unit price 2", value=0.0)
            value2 = st.number_input("Value 2", value=0.0)
        else:
            type_actif2 = None
            token2 = None
            description2 = None
            amount2 = None
            unit_price2 = None
            value2 = None

        if st.button("Ajouter la transaction"):
            new_record = {
                "id": max(df["id"] + 1),
                "date": date,
                "type_transaction": type_transaction,
                "type_actif1": type_actif1,
                "token1": token1,
                "description1": description1,
                "amount1": amount1,
                "unit_price1": unit_price1,
                "value1": value1,
                "type_actif2": type_actif2,
                "token2": token2,
                "description2": description2,
                "amount2": amount2,
                "unit_price2": unit_price2,
                "value2": value2,
            }

            if token1 not in df_token["symbole"].unique():
                new_token1 = {
                    "type": type_actif1,
                    "symbole": token1,
                    "name": description1,
                }
                add_token_to_db(new_token1)
            if token2 not in df_token["symbole"].unique() and token2 is not None:
                new_token2 = {
                    "type": type_actif2,
                    "symbole": token2,
                    "name": description2,
                }
                add_token_to_db(new_token2)

            update_portefeuille(new_record, type_transaction)
            add_database_record(new_record)
            st.success("Lignes ajoutées avec succès.")
            expanded_state = False
            st.rerun()


def display_table_with_pagination(dataframe, page_size=10):
    col1, col2, col3, col4 = st.columns((2, 2, 1, 1))
    st.sidebar.write(st.session_state)
    page_size = col1.selectbox(
        "nombre de ligne par page", [10 + i * 5 for i in range(10)]
    )
    total_num = ceil(len(dataframe) // page_size) + 1
    page_num = col2.selectbox(
        "", [i + 1 for i in range(total_num)], format_func=lambda x: "page " + str(x)
    )
    col4.write("")
    col4.write("")
    placeholder_button_delete = col4.empty()
    transaction_df_page = paginate_dataframe(dataframe, page_size, page_num)
    # transaction_df_page['edit'] = st.checkbox('', key=)
    col_name = dataframe.columns

    cols = st.columns(len(col_name) + 1)

    # header
    for col, name in zip(cols, col_name):
        col.write("**" + name + "**")

    # rows
    for idx, row in transaction_df_page.iterrows():
        cols = st.columns(len(col_name) + 1)
        for id_col, col_ in enumerate(col_name):
            cols[id_col].write(
                row[col_],
            )

        placeholder = cols[-1].empty()
        placeholder.checkbox("edit", key="delete_" + str(row["id"]))

    # Bouton pour supprimer les lignes sélectionnées
    if placeholder_button_delete.button("Supprimer les lignes sélectionnées"):
        # selected_rows = dataframe[dataframe["edit"] == True]
        delete_rows(st.session_state, transaction_df_page)
        st.success("Lignes supprimées avec succès.")
        st.rerun()


# Exemple de DataFrame
conn = sqlite3.connect("./data/db.sqlite3")
df = pd.read_sql_query("SELECT * FROM transaction_history", conn)
df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)
df.sort_values(by="date", ascending=False, inplace=True)
conn.close()


# Afficher la table avec pagination et colonne de sélection
st.title("Transactions")

with st.expander("Ajouter une transaction", expanded=expanded_state):
    ajouter_transaction()

display_table_with_pagination(df)
