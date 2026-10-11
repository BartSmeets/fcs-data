"""
Data loading and saving for the FCS Visualiser.
 
Functions here take an AppState instance explicitly rather than reaching into
st.session_state, which keeps them testable outside of a running Streamlit
session (e.g. construct an AppState and call gen_df(state) in plain pytest).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from fcs_studio.dataset._app_state import AppState

FILE_EXTENSION = "*.npy"

__all__ = [
    'basename',
    'list_data_files',
    ]

def list_data_files(directory: Path) -> list[Path]:
    """Return all data files in directory."""
    return list(directory.glob(FILE_EXTENSION))


def basename(path: str) -> str:
    return os.path.basename(path)


def full_path(state: AppState, name: str) -> str:
    """Rebuild a full path from a filename shown in the UI."""
    return os.path.join(state.directory, name)


def parse_filename(filename: str):
    """
    Extract the wavelength and on/off state from a file name.

    The filename is expected to follow the pattern
    `<prefix>_<value>_<IR|noIR>.<extension>`

    Parameters
    ----------
    filename: str
        file directory

    Returns
    -------
    tuple: tuple
        A tuple containing the wavelength and state, or None if no match
    
    """
    stem = Path(filename).stem

    match = re.match(r".*_(.+?)_(IR|noIR)$", stem, re.IGNORECASE,)

    if match is None:
        return None

    return (float(match.group(1)), match.group(2).lower())


def get_all_data(state: AppState):
    """
    Generate a DataFrame containing all files with their corresponding wavelength and IR state

    Returns
    -------
    file_records: DataFrame
        contains file, wavelength, and onoff (ir | noir)
    
    """
    npy_files = sorted(list_data_files(state.directory))
    
    file_records = []

    for f in npy_files:
        parsed = parse_filename(f)

        if parsed is None:
            continue

        wavelength, onoff = parsed
        file_records.append({
                "file": f,
                "wave": wavelength,
                "onoff": onoff
            })

    files_df = pd.DataFrame(file_records)
    return files_df


def gen_csv(state: AppState, idx):
    """
    Export intgerated signals to csv

    """
    export_rows = []
    for i in idx:
        for j, wl in enumerate(state.files_df.wave.unique()):
            export_rows.append({
                "wavelength_nm": wl,
                "mass": state.target_masses[i],
                "ion": state.ion[i, j],
                "ioff": state.ioff[i, j],
                "diff": state.ion[i, j] - state.ioff[i, j],
            })
    result_df = pd.DataFrame(export_rows)

    csv = result_df.to_csv(index=False)
    return csv