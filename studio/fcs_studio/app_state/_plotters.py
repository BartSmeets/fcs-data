from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

if TYPE_CHECKING:
    from fcs_studio.app_state._app_state import AppState


def plot_spec(state: AppState, spectrum_type: str, pointer: bool, pointer_value: float) -> None:
    """
    Plot the mass/time spectrum.

    Parameters
    ----------
    state: AppState
        Session state of the application
    spectrum_type: str ["time" or "mass"]
        Determines the horizontal axis type.
    pointer: bool
        Should a vertical line be plotter as pointer?
    pointer_value: float
        Position of the pointer on the horizontal axis.

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
        prepare_axes(fig, "time (μs)", "accumulated voltage (V)")
    else:  # mass
        fig = px.line(state.dataframe, x="mass", y="voltage", color="name")
        prepare_axes(fig, "mass (amu)", "accumulated voltage (V)")
 
    if pointer:
        fig.add_vline(pointer_value, line_dash="dash", line_color="red")
 
    st.plotly_chart(fig, width='stretch')


def plot_ir(state: AppState, selected_masses, mode):
    idx = [int(np.where(np.asarray(np.round(state.target_masses, 2)) == m)[0][0]) 
                for m in selected_masses]
    fig = _generate_ir_figure(
        sorted(state.files_df.wave.unique()),
        state.ioff[idx, :],
        state.ion[idx, :],
        selected_masses,
        mode,
    )
    st.plotly_chart(fig, width='stretch')


def _generate_ir_figure(wavelengths, ioff, ion, targets, mode):
    diff = ion - ioff  # shape (n_targets, n_wavelengths)
    depl = -np.log(ion / ioff)
    
    fig = go.Figure()
    if mode == "diff":
        for i, mass in enumerate(targets):
            fig.add_trace(go.Scatter(
                x=wavelengths,
                y=diff[i, :],
                mode="lines+markers",
                name=f"m/z {mass}",
                xaxis="x",
            ))

        fig.update_layout(yaxis_title="ΔSignal (IR on − IR off)",)
    else:
        for i, mass in enumerate(targets):
            fig.add_trace(go.Scatter(
                x=wavelengths,
                y=depl[i, :],
                mode="lines+markers",
                name=f"m/z {mass}",
                xaxis="x",
            ))

        fig.update_layout(yaxis_title="Depletion",)

    fig.add_hline(y=0, line_dash="dot", line_color="gray")

    # --- secondary axis: wavenumber (cm^-1) ---
    wl_min, wl_max = min(wavelengths), max(wavelengths)
    wn_at_min = 1e7 / wl_min  # smaller wavenumber
    wn_at_max = 1e7 / wl_max  # larger wavenumber

    fig.update_layout(
        xaxis={
            "title": "Wavelength (nm)",
            "domain": [0, 1],
        },
        xaxis2={
            "title": "Wavenumber (cm⁻¹)",
            "overlaying": "x",
            "side": "top",
            "range": [wn_at_min, wn_at_max],  # reversed to align with wavelength axis
        },
        legend_title="Mass",
        hovermode="closest",
        height=500,
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )

    # dummy invisible trace to force xaxis2 to render
    fig.add_trace(go.Scatter(
        x=[wl_min, wl_max], y=[None, None],
        xaxis="x2", showlegend=False, hoverinfo="skip",
    ))

    return fig