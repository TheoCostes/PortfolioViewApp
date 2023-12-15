import streamlit as st
import logging

# Configuration de la page Streamlit
st.set_page_config(page_title="dashboard", layout="wide")
logging.basicConfig(level=logging.DEBUG)

if not st.session_state["user_logged_in"]:
    st.warning("**Access is restricted. Please go connect !**")
else :
    st.title("Dashboard Page")
    st.warning("This page is under construction...")