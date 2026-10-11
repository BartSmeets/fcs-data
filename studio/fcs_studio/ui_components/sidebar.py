from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st

from .folder_dialog import select_folder

if TYPE_CHECKING:
    from fcs_studio.app_state._app_state import AppState


def directory(state: AppState):
    with st.sidebar:
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
        st.session_state.setdefault("dir_input", str(state.directory))
        state.directory = Path(st.text_input("Directory", key="dir_input"))


def calibration(state: AppState):
    with st.sidebar, st.container(border=True):
        st.write("### Mass Calibration")
        st.write("$m = a(t-k)^2$")
    
        col1, col2 = st.columns(2)
        with col1:
            state.a = st.number_input(
                "a", min_value=0.0, step=1e-8, value=state.a, format="%.8f"
            )
        with col2:
            state.k = st.number_input("k", step=1e-8, value=state.k, format="%.8f")
        st.button("Apply", on_click=state.build_dataframe())