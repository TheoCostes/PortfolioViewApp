import streamlit as st
import logging

# Configuration de la page Streamlit
st.set_page_config(page_title="settings", layout="wide")
logging.basicConfig(level=logging.DEBUG)

if not st.session_state["authentication_status"]:
    st.warning("**Access is restricted. Please go connect !**")
else :
    st.title("Settings Page")
    st.warning("This page is under construction...")