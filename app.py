import streamlit as st
import yaml
from st_files_connection import FilesConnection
import logging

from yaml import SafeLoader
import s3fs
import streamlit_authenticator as stauth

st.title("Bienvenue sur l'app de suivie de portefeuille !")

logging.debug("debut connexion")
conn = st.connection('s3', type=FilesConnection)
logging.debug("connexion reussi !")
df = conn.read("dashboard-invest/portefeuille.csv", input_format="csv", ttl=600)

logging.debug("df recup !")
logging.debug(df)
# Print results.
st.dataframe(df)


# setup_database()

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

def reset_password():
    global file, e
    if st.button('Reset password'):
        try:
            if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                st.success('Password modified successfully')
                with open('./config_auth.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)





if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    st.sidebar.success(f'Connnexion Réussi ! Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    with tabs1:
        authenticator.login('Login', 'main')
        st.error('Username/password is incorrect')
        reset_password()
elif st.session_state["authentication_status"] is None:
    with tabs1:
        authenticator.login('Login', 'main')
        st.warning('Please enter your username and password')
        reset_password()



with tabs2:
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
            with open('./config_auth.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)


