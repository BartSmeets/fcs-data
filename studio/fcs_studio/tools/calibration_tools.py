"""
Module for calibrating the mass spectrum

Functions
---------
fit:
    Fit for calibration constants
plot:
    Plot fitting result
apply:
    Apply calibration constants

"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import plotly.express as px
import streamlit as st
import toml
from scipy.optimize import curve_fit

from fcs_studio.app_state import get_state

if TYPE_CHECKING:
    from pandas import DataFrame

MODEL = lambda x, a, k: a * (x - k)**2
CONFIG_DIR = Path(__file__).parent.parent / "config"


def fit(df: DataFrame) -> np.ndarray:
    """
    Fit for the calibration constants.

    Parameters
    ----------
    df: DataFrame
        Dataframe containing the arrival times and corresponding masses.
    
    Returns
    -------
    tuple: (a, k)
        Calibration constants
    """
    data = df.dropna(subset=["Time", "Mass"])
    y = np.array(data['Mass'])
    x = np.array(data['Time'])

    try:
        popt, _ = curve_fit(MODEL, x, y, p0=[0.09, 0.2])
    except (ValueError, TypeError):
        popt = np.array([0, 0])
    
    return popt


def plot(df: DataFrame, popt: tuple[float, float]) -> None:
    """
    Plot the data and the fit result.

    Parameters
    ----------
    df: DataFrame
        Pandas dataframe of the data.
        Must have a "Time" and "Mass" column.
    popt: tuple
        Optimal parameters from fit.

    """
    data = df.dropna(subset=["Time", "Mass"])

    # Data as markers rather than a line (calibration points are discrete)
    fig = px.scatter(data, x="Time", y="Mass")
    fig.update_traces(name="Data", showlegend=True)

    # Smooth fit curve across the data range
    x_fit = np.linspace(0, data["Time"].max() * 1.2, 500)
    y_fit = MODEL(x_fit, *popt)

    a, k = popt
    fig.add_scatter(
        x=x_fit,
        y=y_fit,
        mode="lines",
        name=f"Fit: a={a:.3e}, k={k:.3e}",
    )

    fig.update_layout(legend={'orientation': "h", 'y': 1.02, 'x': 0},  xaxis_title="Time (μs)",
                yaxis_title="Mass (amu)")
    st.plotly_chart(fig, width = "stretch")


def apply(label: str, popt: tuple[float, float] | None = None) -> None:
    """
    Apply calibration constants,
    and store them in `calibration.toml` if new parameters are provided with `popt`.

    Parameters
    ----------
    label: str
        Label for storing or finding the constants in `calibration.toml`
    popt: tuple[float, float] | None, default=None
        Tuple containing the calibration constants.
        If `popt is None` the constants are read from `calibration.toml`
        If `popt is not None`, `popt` is stored in `calibration.toml`.

    """
    state = get_state()
    with open(CONFIG_DIR / 'calibration.toml', 'r') as f:
        defaults = toml.load(f)

    if popt is not None:
        date = datetime.today().strftime("%Y-%m-%d")  # noqa: DTZ002
        suffix = label.strip()
        label = f"{date}_{suffix}" if suffix else date

        # Log new values to label
        defaults[label] = {
            'a': float(popt[0]),
            'k': float(popt[1])
            }
    else:
        # Retreive values from label
        try:
            popt = (defaults[label]['a'], defaults[label]['k'])
        except KeyError:
            st.error(f'Label {label} is not registered in `calibration.toml`')      

    # Update last used
    defaults['last_used']['a'] = float(popt[0])
    defaults['last_used']['k'] = float(popt[1])

    # Dump
    with open(CONFIG_DIR / 'calibration.toml', "w") as toml_file:
        toml.dump(defaults, toml_file)

    # Update Session State
    state.a = float(popt[0])
    state.k = float(popt[1])

