from math import ceil
import streamlit as st
import sqlite3
import pandas as pd
import logging

# TODO : edit une transaction

logging.basicConfig(level=logging.DEBUG)

# Initialiser les paramètres de page Streamlit
st.set_page_config(page_title="Transactions", layout="wide", )

# Initialiser l'état de session pour la suppression de transactions
if "delete_transaction" not in st.session_state:
    st.session_state["delete_transaction"] = dict()

# Définir l'état initial de l'expander
expanded_state = False

def paginate_dataframe(dataframe, page_size, page_num):
    """Paginer le DataFrame"""
    if page_size is None:
        return None
    logging.debug(f'{page_size} | {page_num}')
    offset = page_size * (page_num - 1)
    return dataframe[offset: offset + page_size]

def delete_rows(session_state):
    """Supprimer les lignes sélectionnées de la base de données"""
    conn = sqlite3.connect("./data/db.sqlite3")
    cursor = conn.cursor()
    for id, state in st.session_state.items():
        if id.split('_')[0] == "delete" and state:
            cursor.execute(f"DELETE FROM transaction_history WHERE id = ?",
                           (id.split('_')[1],))
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


def update_portefeuille(request_post, type_transaction):
    if not Portefeuille.objects.filter(token=request_post['token1']):
        Portefeuille.objects.create(token=request_post['token1'],
                                    amount=request_post['amount1'],
                                    unit_price=float(
                                        request_post['unit_price1']),
                                    value=float(request_post['value1']),
                                    type_actif=request_post['type_actif_token1'],
                                    description=request_post['descriptif1'],
                                    last_update=now()
                                    )
    else:
        token_1 = Portefeuille.objects.get(token=request_post['token1'])
        print("here", token_1.amount, request_post['amount1'])
        token_1.amount += float(request_post['amount1'])
        token_1.unit_price = float(request_post['unit_price1'])
        token_1.last_update = now()
        token_1.save()

    if type_transaction == "Swap":
        if not Portefeuille.objects.filter(token=request_post['token2']):
            Portefeuille.objects.create(token=request_post['token2'],
                                        amount=request_post['amount2'],
                                        unit_price=float(
                                            request_post['unit_price2']),
                                        value=float(request_post['value2']),
                                        type_actif=request_post['type_actif_token2'],
                                        description=request_post['descriptif2'],
                                        last_update=now())
        else:
            token_2 = Portefeuille.objects.get(token=request_post['token2'])
            token_2.amount += float(request_post['amount2'])
            token_2.unit_price = float(request_post['unit_price1'])
            token_2.last_update = now()
            token_2.save()


def ajouter_transaction():
    """Ajouter une transaction"""
    global expanded_state
    conn = sqlite3.connect("./data/db.sqlite3")

    df_type_transaction = pd.read_sql_query("SELECT * FROM transactions_type_transac", conn)['name']
    df_portefeuille = pd.read_sql_query("SELECT * FROM portefeuille_portefeuille", conn)

    df_token = pd.read_sql_query("SELECT * FROM transactions_token", conn)
    df_type_actif = df_token['type']

    conn.close()

    with st.container():
        date = st.date_input('Date', format="DD/MM/YYYY")
        type_transaction = st.selectbox('Type transaction',
                                        df_type_transaction,
                                        index=None,
                                        placeholder="Transaction",
                                        )

        if type_transaction:
            type_actif1 = st.selectbox('Type actif 1',
                                       df_type_actif.unique(),
                                       index=None,
                                       placeholder="Type actif",
                                       )
            token1 = st.selectbox('Token 1',
                                  df_token['symbole'].unique().tolist() + ['autres'],
                                  index=None,
                                  placeholder="Token",
                                  )
            if token1 == 'autres':
                token1 = st.text_input('Token 1')
                description1 = st.text_input('Description 1')
                st.write(f'Description 1 = {description1}')
            else:
                description1 = df_token[df_token['symbole'] == token1]['name'].to_string(index=False)
                st.write(f'Description 1 = {description1}')
            amount1 = st.number_input('Amount 1',
                                      value=0.0
                                      )
            unit_price1 = st.number_input('Unit price 1',
                                          value=0.0
                                          )
            value1 = st.number_input('Value 1',
                                     value=0.0
                                     )
        if type_transaction == "Swap":
            st.divider()
            type_actif2 = st.selectbox('Type actif 2',
                                       df_type_actif.unique(),
                                       index=None,
                                       placeholder="Type actif",
                                       )
            token2 = st.selectbox('Token 2',
                                  df_token['symbole'].unique(),
                                  index=None,
                                  placeholder="Token",
                                  )
            description2 = df_token[df_token['symbole'] == token2]['name'].to_string(index=False)
            st.write(f'Description 2 = {description2}')
            amount2 = st.number_input('Amount 2',
                                      value=0.0
                                      )
            unit_price2 = st.number_input('Unit price 2',
                                          value=0.0
                                          )
            value2 = st.number_input('Value 2',
                                     value=0.0
                                     )
        else:
            type_actif2 = None
            token2 = None
            description2 = None
            amount2 = None
            unit_price2 = None
            value2 = None

        if st.button('Ajouter la transaction'):

            new_record = {
                "id" : max(df["id"]+1),
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
                "value2": value2
            }

            if token1 not in df_portefeuille['token'].unique():
                new_token1 = {
                    "type": type_actif1,
                    "symbole": token1,
                    "name": description1,
                }
                add_token_to_db(new_token1)
            if token2 not in df_portefeuille['token'].unique() and token2 is not None:
                new_token2 = {
                    "type": type_actif2,
                    "symbole": token2,
                    "name": description2,
                }
                add_token_to_db(new_token2)

            st.sidebar.write(new_record)
            add_database_record(new_record)
            st.success("Lignes ajoutées avec succès.")
            expanded_state = False
            st.rerun()


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
        placeholder.checkbox("edit", key="delete_" + str(row['id']))

    # Bouton pour supprimer les lignes sélectionnées
    if placeholder_button_delete.button("Supprimer les lignes sélectionnées"):
        # selected_rows = dataframe[dataframe["edit"] == True]
        delete_rows(st.session_state)
        st.success("Lignes supprimées avec succès.")
        st.rerun()


# Exemple de DataFrame
conn = sqlite3.connect("./data/db.sqlite3")
df = pd.read_sql_query("SELECT * FROM transaction_history", conn)
df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True)
df.sort_values(by='date', ascending=False, inplace=True)
conn.close()

# Afficher la table avec pagination et colonne de sélection
st.title('Transactions')

with st.expander('Ajouter une transaction', expanded=expanded_state):
    ajouter_transaction()

display_table_with_pagination(df)
