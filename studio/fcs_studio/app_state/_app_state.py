"""
Application state for the FCS Visualiser

A single AppState instance lives in st.session_state['app_state'] and is passed to functions that need it.

"""

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import toml

from ._builders import build_dataframe
from ._plotters import plot_spec

CONFIG_DIR = Path(__file__).parent.parent / "config"


def _empty_dataframe() -> pd.DataFrame:
    return pd.DataFrame({"time": [], "mass": [], "voltage": [], "name": []})
 
 
def _empty_figure():
    return px.line([])


@dataclass
class IntegrationMassSettings:
    main_mass: float = 58.933
    main_num: int = 40
    messenger_mass: float = 18
    messenger_num: int = 2


@dataclass
class AppState:
    a: float
    k: float

    directory: Path = field(default_factory=Path.home)
    data_files: list[str] = field(default_factory=list)
    data_files_old: list[str] = field(default_factory=list)

    dataframe: pd.DataFrame = field(default_factory=_empty_dataframe)
    figure: object = field(default_factory=_empty_figure)

    intmass: IntegrationMassSettings | None = None
    files_df = None
    target_masses = None
    ioff = None
    ion = None

    def build_dataframe(self) -> None:
        """
        Build DataFrame from selected files and rebuild `state.dataframe`
    
        """
        build_dataframe(self)

    def plot_spectrum(self, spectrum_type: str, pointer: bool | None = None, pointer_value: float = 0.0):
        plot_spec(self, spectrum_type, pointer, pointer_value)


def get_state() -> AppState:
    """
    Return the single AppState for this session, creating it on first run.
    
    """
    if "state" not in st.session_state:
        with open(CONFIG_DIR / 'calibration.toml', 'r') as f:
            defaults = toml.load(f)

        st.session_state["state"] = AppState(
            a = defaults["last_used"]["a"],
            k = defaults["last_used"]["k"],
        )
        
    return st.session_state["state"]