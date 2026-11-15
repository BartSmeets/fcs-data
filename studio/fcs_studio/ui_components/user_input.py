"""
Module for reusable user input widgets

* data_selection:
    Generates a `st.multiselect` for selecting the data files
* select_folder:
    Open a new thread with a tkinter filedialog for selecting the data directory.

"""
import subprocess
import sys

import streamlit as st

from fcs_studio.app_state import get_state

FILE_EXTENSION = "*.npy"


def data_selection():
    """
    Generates a `st.multiselect` for selecting the data files

    Updates session state

    """
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


def select_folder(initial_dir: str = "") -> str | None:
    """
    Select Folder

    Open a new thread with a tkinter filedialog for selecting the data directory.

    Parameters
    ----------
    initial_dir: str, default=""
        Directory that opens when the filedialog is generated.

    Returns
    -------
    directory: str | None

    """
    code = (
        "import tkinter as tk\n"
        "from tkinter import filedialog\n"
        "root = tk.Tk()\n"
        "root.withdraw()\n"
        "root.attributes('-topmost', True)\n"
        f"print(filedialog.askdirectory(title='Select Directory', initialdir={initial_dir!r}) or '')\n"
        "root.destroy()\n"
    )
    result = subprocess.run([sys.executable, "-c", code], check=False, capture_output=True, text=True)
    return result.stdout.strip() or None