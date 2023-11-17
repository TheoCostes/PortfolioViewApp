from math import ceil

import streamlit as st
import sqlite3
import pandas as pd

import logging
logging.basicConfig(level=logging.DEBUG)

st.set_page_config(page_title="test", layout="wide")


if "delete_transaction" not in st.session_state:
    st.session_state["delete_transaction"] = dict()


def paginate_dataframe(dataframe, page_size, page_num):
    if page_size is None:
        return None
    logging.debug(f'{page_size} | {page_num}')
    offset = page_size * (page_num - 1)
    return dataframe[offset: offset + page_size]


def change_state(row):
    st.session_state['delete_transaction'][row['id']] = True



# Fonction pour afficher la table avec pagination et colonne de sélection
def display_table_with_pagination(dataframe, page_size=10):
    col1, col2, col3, col4 = st.columns((2, 2, 1, 1))

    page_size = col1.selectbox("nombre de ligne par page", [10 + i * 5 for i in range(10)])
    total_num = ceil(len(dataframe) // page_size) + 1
    logging.debug(total_num)
    page_num = col2.selectbox("", [i + 1 for i in range(total_num)], format_func=lambda x: "page " + str(x))
    col4.write('')
    col4.write('')
    placeholder_button_delete = col4.empty()
    transaction_df_page = paginate_dataframe(
        dataframe, page_size, page_num
    )
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
        placeholder.checkbox("edit",key="delete_" + str(row['id']))

    # Bouton pour supprimer les lignes sélectionnées
    if placeholder_button_delete.button("Supprimer les lignes sélectionnées"):
        # selected_rows = dataframe[dataframe["edit"] == True]
        delete_rows(st.session_state)
        st.success("Lignes supprimées avec succès.")
        st.rerun()


# Fonction pour supprimer les lignes sélectionnées de la base de données
def delete_rows(session_state):
    conn = sqlite3.connect("./data/db.sqlite3")
    cursor = conn.cursor()
    for id, state in st.session_state.items():
        if id.split('_')[0] == "delete" and state:
            cursor.execute(f"DELETE FROM transaction_history WHERE id = ?",
                           (id.split('_')[1],))
    conn.commit()
    conn.close()


# Exemple de DataFrame
conn = sqlite3.connect("./data/db.sqlite3")
cursor = conn.cursor()
data = cursor.execute("SELECT * FROM transaction_history")
df = pd.DataFrame(data, columns=[x[0] for x in cursor.description]).query("token1 == 'TEST1'")
conn.close()

# Afficher la table avec pagination et colonne de sélection
st.title('Transactions')
st.sidebar.write(st.session_state)
display_table_with_pagination(df)