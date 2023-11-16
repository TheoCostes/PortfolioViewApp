import datetime

import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import sqlite3
import sys

sys.path.insert(0, "..")

st.set_page_config(page_title="transaction", layout="wide")

if "dict_edit_transaction" not in st.session_state:
    st.session_state["dict_edit_transaction"] = dict()


def paginate_dataframe(dataframe, page_size, page_num):
    if page_size is None:
        return None
    offset = page_size * (page_num - 1)
    return dataframe[offset : offset + page_size]


conn = sqlite3.connect("./data/db.sqlite3")
cursor = conn.cursor()

st.title("Transactions")

test = cursor.execute("SELECT name FROM sqlite_master  WHERE type='table'")
st.write(f"{test.fetchall()}")

transaction_db = cursor.execute("SELECT * FROM transaction_history").fetchall()
col_name = [description[0] for description in cursor.description]

transaction_df = pd.DataFrame(transaction_db, columns=col_name)
transaction_df.drop("id", inplace=True, axis=1)
col_name.remove("id")

page_size = st.selectbox("nombre de ligne par page", [10 + i * 5 for i in range(10)])
total_num = len(transaction_df) // page_size
page_num = st.selectbox("", [i + 1 for i in range(total_num)], format_func=lambda x: "page " + str(x))
transaction_df_page = paginate_dataframe(
    transaction_df, page_size, page_num
)

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
    show_more = placeholder.button("edit", key=idx, type="primary")

    # if button pressed
    if show_more:
        # rename button
        placeholder.button("cancel", key=str(idx) + "_")

        # do stuff
        with st.form("Modification de la transaction :"):
            all_token = cursor.execute("select * from transactions_token").fetchall()
            col_name_token = [description[0] for description in cursor.description]
            all_token_df = pd.DataFrame(all_token, columns=col_name_token)
            type_actif_list = all_token_df["type"].unique().tolist()
            symbole_list = all_token_df["symbole"].unique().tolist()

            st.session_state["dict_edit_transaction"]["date"] = st.date_input(
                "Date",
                value=datetime.datetime.strptime(row['date'],"%d/%m/%Y")
            )
            st.session_state["dict_edit_transaction"]["type_actif1"] = st.selectbox(
                "Type actif 1",
                type_actif_list,
                index=type_actif_list.index(row['type_actif1']),
            )
            st.session_state["dict_edit_transaction"]["token1"] = st.selectbox(
                "Token 1", all_token_df["symbole"],
                index=symbole_list.index(row['token1']),
            )

            st.session_state["dict_edit_transaction"]["amount1"] = st.number_input(
                "Amount 1", value=row["amount1"]
            )
            st.session_state["dict_edit_transaction"]["unit_price1"] = st.number_input(
                "Unit price 1", value=row["unit_price1"]
            )
            st.session_state["dict_edit_transaction"]["value1"] = st.number_input(
                "Value 1", value=row["value1"]
            )
            if row["type_transaction"] == "swap":
                st.divider()
                st.session_state["dict_edit_transaction"]["type_actif2"] = st.selectbox(
                    "Type actif 2", type_actif_list,
                    index=type_actif_list.index(row['type_actif2']),
                )
                st.session_state["dict_edit_transaction"]["token2"] = st.selectbox(
                    "Token 2", all_token_df["symbole"],
                    index=symbole_list.index(row['token2']),
                )
                st.session_state["dict_edit_transaction"]["amount2"] = st.number_input(
                    "Amount 2"
                )
                st.session_state["dict_edit_transaction"][
                    "unit_price2"
                ] = st.number_input("Unit price 2")
                st.session_state["dict_edit_transaction"]["value2"] = st.number_input(
                    "Value 2"
                )
            if st.form_submit_button("Valider"):
                try:
                    sql_update_query = f"""
                    Update transaction_history set """

                    for k, v in st.session_state["dict_edit_transaction"].items():
                        sql_update_query += f"{k} = {v}, "
                    sql_update_query[:-2] += f" where id = {idx}"
                    st.write(sql_update_query)
                    cursor.execute(sql_update_query)
                    conn.commit()
                except sqlite3.Error as error:
                    print("Failed to update sqlite table", error)
        st.write("This is some more stuff with a checkbox")
        temp = st.selectbox("Select one", ["A", "B", "C"])
        st.write("You picked ", temp)
        st.write("---")

cursor.close()
conn.close()
