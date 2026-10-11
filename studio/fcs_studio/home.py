"""
FCS Studio

Streamlit app for browsing, calibrating and plotting FCS data.

"""
from pathlib import Path

import streamlit as st
import toml

from .app_state import get_state
from .ui_components import sidebar

FILE_EXTENSION = "*.npy"
CONFIG_DIR = Path(__file__).parent / "config"

def main():
    # ---------------------------------------------------
    # Setup
    # ---------------------------------------------------
    st.set_page_config(
        page_title="FCS Studio",
        page_icon="https://static-00.iconduck.com/assets.00/python-icon-512x509-pb65l7gl.png",
        layout="wide",
    )
    st.write("# FCS Studio")

    with open(CONFIG_DIR / 'calibration.toml', 'r') as f:
            defaults = toml.load(f)
    state = get_state(defaults)

    # --------------------------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------------------------

    sidebar.directory(state)
    sidebar.calibration(state)

    all_files = list(state.directory.glob(FILE_EXTENSION))
    file_names = [path.name for path in all_files]

    # --------------------------------------------------------------------------
    # Data selection
    # --------------------------------------------------------------------------

    if "selected_files" not in st.session_state:
        st.session_state.selected_files = state.data_files

    st.multiselect(
        "Select Data",
        file_names,
        key="selected_files",
    )

    state.data_files = st.session_state.selected_files

    if state.data_files != state.data_files_old:
        state.data_files_old = state.data_files.copy()
        state.build_dataframe()

    # --------------------------------------------------------------------------
    # Plotting
    # --------------------------------------------------------------------------
    
    if state.data_files:
        col1, col2 = st.columns([3, 1])
    
        with col2:
            SPECTRUM_DICT = {"Time": "time", "Mass": "mass"}
            spectrum_label = st.radio("Spectrum Type", ["Mass", "Time"])
    
            axis_series = state.dataframe[SPECTRUM_DICT[spectrum_label]]
            axis_min = float(axis_series.min())
            axis_max = float(axis_series.max())
    
            with st.container(border=True):
                pointer = st.toggle("Pointer")
                pointer_value = st.number_input(
                    "Pointer",
                    min_value=axis_min,
                    max_value=axis_max,
                    value=axis_min,
                    label_visibility="collapsed",
                )
    
        with col1:
            state.plot_spectrum(SPECTRUM_DICT[spectrum_label], pointer, pointer_value)
            
