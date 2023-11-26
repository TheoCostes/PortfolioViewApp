import sqlite3

import streamlit as st


def setup_database():
    conn = sqlite3.connect('./data/db.sqlite3')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS transaction_history
                 (id INTEGER AUTOINCREMENT, 
                  date VARCHAR,
                  type_transaction VARCHAR,
                  type_actif1 VARCHAR,
                  token1 VARCHAR,
                  description1 VARCHAR,
                  amount1 REAL,
                  unit_price1 REAL,
                  value1 REAL,
                  type_actif2 VARCHAR,
                  token2 VARCHAR,
                  description2 VARCHAR,
                  amount2 REAL,
                  unit_price2 REAL,
                  value2 REAL)
            ''')

    c.execute('''CREATE TABLE IF NOT EXISTS portefeuille_portefeuille
                     (id INTEGER AUTOINCREMENT, 
                      id_portefeuille INTEGER, 
                      last_update VARCHAR,
                      type_actif VARCHAR,
                      token VARCHAR,
                      description VARCHAR,
                      amount REAL,
                      unit_price REAL,
                      value REAL)
                ''')

    c.execute('''CREATE TABLE IF NOT EXISTS transactions_token
                 (id INTEGER AUTOINCREMENT,
                  name VARCHAR, 
                  symbole VARCHAR,
                  type VARCHAR)
            ''')

    conn.commit()
    c.close()
    conn.close()


st.title("Bienvenue sur l'app de suivie de portefeuille !")
setup_database()
st.write(f'{st.session_state}')


