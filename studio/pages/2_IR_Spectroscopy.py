import streamlit as st
from fcs_studio.pages import ir_spectroscopy

st.set_page_config(
    page_title="FCS Studio",
    page_icon="https://static-00.iconduck.com/assets.00/python-icon-512x509-pb65l7gl.png",
    layout="wide",
)

ir_spectroscopy.main()
