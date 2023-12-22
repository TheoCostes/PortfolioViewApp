import streamlit as st
import yaml
from st_files_connection import FilesConnection
import logging

from yaml import SafeLoader
import s3fs
import streamlit_authenticator as stauth
import hmac
import requests


def log_out():
    """Logs out the user."""
    st.session_state["user_logged_in"] = False


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["user_logged_in"] = True
            del st.session_state["password"]  # Don't store the username or password.
        else:
            st.session_state["user_logged_in"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("user_logged_in", False):
        return True

    # Show inputs for username + password.
    st.title("Bienvenue sur l'app Connectez vous pour acceder au dashboard")

    if st.button("Register"):
        try:
            return new_user()
        except:
            st.error("😕 User not known or password incorrect")
    if st.button("Log in"):
        login_form()
    if "user_logged_in" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

def new_user():
    """Registers a new user."""
    def register_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Register", on_click=register_user)

    def register_user():
        """Registers a new user."""
        if st.session_state["username"] in st.secrets["passwords"]:
            st.error("😕 Username already taken")
        else:
            st.secrets["passwords"][st.session_state["username"]] = st.session_state[
                "password"
            ]
            st.session_state["user_logged_in"] = True
            del st.session_state["password"]  # Don't store the username or password.

    # Show inputs for username + password.
    st.title("Register a new user")
    register_form()
    if "user_logged_in" in st.session_state:
        st.success("🎉 User registered successfully")
        return True
    return False

if not check_password():
    st.stop()

st.title(f"Bienvenue sur l'app {st.session_state['username']}!")
st.write("Page Portefeuille : résume l'état de votre portefeuille")
st.write("Page Transactions : permet de saisir vos transactions")
st.write("Page Dashboard : en developpement...")

st.write(st.secrets)

st.write(st.session_state)


logging.debug("debut connexion")
conn = st.connection('s3', type=FilesConnection)
logging.debug("connexion reussi !")
df = conn.read("dashboard-invest/portefeuille.csv", input_format="csv", ttl=600)

# Print results.
st.dataframe(df)


url = "https://api.connect.debank.com/v1/user/complex_protocol_list"
access_key_debank = st.secrets["ACCES_KEY_DEBANK"]
headers = {
    "Authorization": f"Bearer {access_key_debank}",
    "Content-Type": "application/json",
}

address = "0x0e038adF84b1829c393cFd39262070Eef2f2a065"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Traitement des données
    st.write(data)
else:
    print("Erreur de requête:", response.status_code)
    st.write("Erreur de requête:", response.status_code)
# setup_database()