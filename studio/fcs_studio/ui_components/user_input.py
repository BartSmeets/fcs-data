"""
Module for reusable user input widgets

* data_selection:
    Generates a `st.multiselect` for selecting the data files

"""
import streamlit as st

from fcs_studio.app_state import get_state

FILE_EXTENSION = "*.npy"


def data_selection():
    state = get_state()
    all_files = list(state.directory.glob(FILE_EXTENSION))
    file_names = [path.name for path in all_files]

    # Data selection
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