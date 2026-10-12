"""
FCS Studio

Streamlit app for browsing, calibrating and plotting FCS data.

"""
from pathlib import Path

import streamlit as st

from fcs_studio.app_state import get_state
from fcs_studio.ui_components import sidebar, user_input

CONFIG_DIR = Path(__file__).parent.parent / "config"


def main():
    # Setup
    st.title("FCS Studio")

    state = get_state()

    # Sidebar
    sidebar.directory()
    sidebar.calibration()

    user_input.data_selection()

    # Plotting    
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
            
