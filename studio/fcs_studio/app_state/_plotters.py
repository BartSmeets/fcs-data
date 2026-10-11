from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.express as px
import streamlit as st

if TYPE_CHECKING:
    from fcs_studio.app_state._app_state import AppState


def plot_spec(state: AppState, spectrum_type: str, pointer: bool, pointer_value: float):
    """
    Plot the mass/time spectrum.
    """
    def prepare_axes(fig, xlabel, ylabel):
        fig.update_layout(
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            legend={"yanchor": "bottom", "y": 1.02, "xanchor": "left", "orientation": "h"},
            legend_title_text="",
            xaxis={"showgrid": True},
            uirevision=True,
        )
 
    if spectrum_type == "time":
        fig = px.line(state.dataframe, x="time", y="voltage", color="name")
        prepare_axes(fig, "time (us)", "accumulated voltage (V)")
    else:  # mass
        fig = px.line(state.dataframe, x="mass", y="voltage", color="name")
        prepare_axes(fig, "mass (amu)", "accumulated voltage (V)")
 
    if pointer:
        fig.add_vline(pointer_value, line_dash="dash", line_color="red")
 
    st.plotly_chart(fig, width='stretch')