import logging
import sqlite3
import yaml
import os
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

import streamlit as st


def setup_user_auth():
    """Setup username and password"""
    if not os.path.isfile(os.path.join(".", "config_auth.yaml")):
        logging.debug("Creating config_auth.yaml")
        logging.debug(os.path.isfile(os.path.join(".", "config_auth.yaml")))
        data = {
            'credentials': {
                'usernames': {
                    "admin": {
                        "email": "tharic100@gmail.com",
                        "name": "admin",
                        "password": "admin",
                    },
                }
            },
            'cookie': {
                "expiry_days": 30,
                "key": "user",
                "name": "session_state"
            },
            'preauthorized': {
                "emails": "- tharic100@gmail.com"
            }
        }

        with open('./config_auth.yaml', 'w') as file:
            yaml.dump(data, file)


def setup_database():
    setup_user_auth()

    conn = sqlite3.connect('./data/db.sqlite3')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS transaction_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
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
            """)

    c.execute('''CREATE TABLE IF NOT EXISTS portefeuille_portefeuille
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name VARCHAR, 
                  symbole VARCHAR,
                  type VARCHAR)
            ''')

    conn.commit()
    c.close()
    conn.close()


st.title("Bienvenue sur l'app de suivie de portefeuille !")
setup_database()

with open('./config_auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

tabs1, tabs2 = st.tabs(["Login", "Register"])
with tabs1:
    authenticator.login('Login', 'main')


    if st.session_state["authentication_status"]:
        authenticator.logout('Logout', 'main', key='unique_key')
        st.write(f'Welcome *{st.session_state["name"]}*')
        st.title('Some content')
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                st.success('Password modified successfully')
                with open('./config_auth.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)
with tabs2:
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
            with open('./config_auth.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
