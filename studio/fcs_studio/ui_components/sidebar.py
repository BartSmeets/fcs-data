"""
Module containing the sidebar elements:

* directory():
    Selection panel for selecting the data directory
* calibration():
    Panel for setting the calibration constants

"""
from pathlib import Path

import streamlit as st
import toml

from fcs_studio.app_state import get_state
from fcs_studio.tools.calibration_tools import apply

from .user_input import select_folder

CONFIG_DIR = Path(__file__).parent.parent / "config"


def directory():
    """
    Selection panel for selecting the data directory
    
    Contains:
    * Select button linked to `select_folder`
    * Refresh button
    * Text element that reads the directory

    Updates session state

    """
    state = get_state()
    
    with st.sidebar:
        st.title('Data Directory')
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Select Directory"):
                selected = select_folder(str(state.directory))
                if selected:
                    state.directory = Path(selected)
                    st.session_state["dir_input"] = str(state.directory)

        with col2:
            st.button("Refresh Files")

        # initialize the widget value once
        directory_text = st.text_input("Directory", value=str(state.directory))

        if directory_text != str(state.directory):
            state.directory = Path(directory_text)

        if directory_text:
            state.directory = Path(directory_text)

        st.divider()


def calibration():
    """
    Panel for calibration details

    Contains:
    * Selectbox for label in `calibration.toml`
    * Readout of the current calibration constants
    * Expander for manual input

    Updates session state

    """
    # Settings
    state = get_state()
    with open(CONFIG_DIR / 'calibration.toml', 'r') as f:
        defaults = toml.load(f)

    options = ["last_used"] + list(reversed(
        [k for k in defaults if k != "last_used"]
    ))

    with st.sidebar:
        st.title("Mass Calibration: $m = a(t-k)^2$")

        st.metric("a", f'{state.a:.5f} amu/μs²')
        st.metric("k", f'{state.k:.5f} μs')

        # Config loading
        col1, col2 = st.columns([4,1])
        with col1:
            label = st.selectbox('Configuration label', options)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True) # Space the button
            if st.button("Load"):
                apply(label)
                st.rerun()

        # Manual Input
        with st.expander("Manual Input"):
            col1, col2 = st.columns(2)
            with col1:
                state.a = st.number_input(
                    "a", min_value=0.0, step=1e-8, value=state.a, format="%.8f"
                )
            with col2:
                state.k = st.number_input("k", step=1e-8, value=state.k, format="%.8f")
        
            if st.button("Apply"):
                apply('manual', (state.a, state.k))
                st.rerun()

        # Finalise
        state.build_dataframe()

        st.divider()