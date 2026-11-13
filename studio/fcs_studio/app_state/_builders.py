from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import streamlit as st

from fcs_data import MassSpec

if TYPE_CHECKING:
    from fcs_studio.app_state._app_state import AppState


def build_dataframe(state: AppState):
    """
    Build DataFrame from selected files and rebuild `state.dataframe`

    Parameters
    ----------
    state: AppState
        Session state of the application

    """
    init_param = [state.a, state.k]
    rows = []

    for name in state.data_files:
        path = state.directory / name
        try:
            data = MassSpec(path, init_param)
        except OSError:
            st.warning(f"Could not read '{name}' — skipping.")
            continue

        df = pd.DataFrame(
            {
                "time": data.time,
                "mass": data.mass,
                "voltage": data.voltage,
                "name": [name] * len(data.time),
            }
        )

        rows.append(df)

    state.dataframe = (
        pd.concat(rows, ignore_index=True)
        if rows
        else pd.DataFrame({"time": [], "mass": [], "voltage": [], "name": []})
    )


def build_ir(
        state: AppState, 
        prominence: float | None = None,
        tol: float = 0.5,
        **peak_kwargs,
    ):
    """
    Build IR Spectrum from all files in selected directory
    and update session state

    Parameters
    ----------
    state: AppState
        Session state of the application
    prominence: float | None, default=None
        Prominence, see `scipy.signal.find_peaks()`.
        If `None`, a prominence is estimated from the noise level
    tol: float, default=0.5
        Tolerance for detecting mass overlap
    **peak_kwargs:
        Passed to `scipy.signals.curve_fit`

    """
    npy_files = sorted(state.directory.glob("*.npy"))

    # Load all spectra
    mass_spectra = []
    for file in npy_files:
        # Read file
        parsed = _parse_filename(file)
        if parsed is None:
            continue 
        massspec = MassSpec(file, (state.a, state.k))

        # Store data
        wavelength, onoff = parsed
        mass_spectra.append((wavelength, onoff, massspec))

    if not mass_spectra:
        return

    # Pass 1: Find peaks
    found = [
        ms.find_peaks(prominence=prominence, **peak_kwargs)
        for _, _, ms in mass_spectra
    ]
    all_masses = np.concatenate([f[0] for f in found])
    all_widths = np.concatenate([f[3] for f in found])
    
    if all_masses.size == 0:
        return
    mass_axis, width_axis = _clean_masses(all_masses, all_widths, tol=tol)

    # Pass 2: Read every file at reference mass
    frames = []
    for wavelength, onoff, ms in mass_spectra:
        integrals = [
            ms.integrate(mass_range = (m0 - w, m0 + w)) 
            for m0, w in zip(mass_axis, width_axis)
        ]

        # Store data
        frames.append({
            "file": file,
            "wavelength": wavelength,
            "state": onoff,
            "mass": mass_axis,
            "intensity": integrals,
        })

    long = pd.concat(frames, ignore_index=True)

    ir_table = long.pivot_table(
        index="wavelength", 
        columns=["mass", "state"], 
        values="intensity", 
        dropna=False,
    )
    state.ir_df = ir_table.sort_index().sort_index(axis=1)


def _parse_filename(file: Path):
    """
    Extract the wavelength and on/off state from a file name.

    The filename is expected to follow the pattern
    `<prefix>_<value>_<IR|noIR>.<extension>`

    Parameters
    ----------
    filename: Path
        file path

    Returns
    -------
    tuple: tuple
        A tuple containing the wavelength and state, or None if no match
    
    """
    stem = file.stem

    match = re.match(r".*_(.+?)_(IR|noIR)$", stem, re.IGNORECASE,)

    if match is None:
        return None

    return (float(match.group(1)), match.group(2).lower())


def _clean_masses(
        masses: np.ndarray, 
        widths: np.ndarray | None = None,
        tol: float = 0.5):
    """
    Sort and remove duplicate masses

    Paramters
    ---------
    masses: np.ndarray
        Array of masses that needs to be cleaned
    tol: float, default=0.5
        Tolerance for detecting mass overlap

    Returns
    -------
    filtered masses: np.ndarray
    
    """
    order = np.argsort(masses)
    m = masses[order]
    breaks = np.where(np.diff(m) > tol)[0] + 1

    mass_axis = np.array([c.mean() for c in np.split(m, breaks)])
    
    if widths is None:
        return mass_axis
    w = widths[order]

    width_axis = np.array([np.nanmedian(c) for c in np.split(w, breaks)])
    
    return mass_axis, width_axis
