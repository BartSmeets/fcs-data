from __future__ import annotations

from typing import TYPE_CHECKING

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