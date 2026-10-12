from pathlib import Path

import streamlit as st
import toml

from fcs_studio.app_state import get_state
from fcs_studio.tools.calibration import apply

from .folder_dialog import select_folder

CONFIG_DIR = Path(__file__).parent.parent / "config"


def directory():
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
    # Settings
    state = get_state()
    with open(CONFIG_DIR / 'calibration.toml', 'r') as f:
        defaults = toml.load(f)

    options = ["last_used"] + list(reversed(
        [k for k in defaults if k != "last_used"]
    ))

    with st.sidebar:
        st.title("Mass Calibration")
        st.write("$m = a(t-k)^2$")

        # Config loading
        label = st.selectbox('Configuration label', options)
        
        if st.button("Load"):
            apply(label)

        # Manual Input
        col1, col2 = st.columns(2)
        with col1:
            state.a = st.number_input(
                "a", min_value=0.0, step=1e-8, value=state.a, format="%.8f"
            )
        with col2:
            state.k = st.number_input("k", step=1e-8, value=state.k, format="%.8f")
    
        if st.button("Apply"):
            apply('manual', (state.a, state.k))

        # Finalise
        state.build_dataframe()

        st.divider()