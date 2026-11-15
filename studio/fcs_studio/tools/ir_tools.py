from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from fcs_studio.app_state._app_state import AppState


def split_states(ir_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """
    Split the IR table into its laser-on and laser-off parts.

    Parameters
    ----------
    ir_df: DataFrame
        Table built by `AppState.build_ir`.
        The index holds the wavelengths and the columns are a MultiIndex of (mass, state)
        with state being either "ir" (laser on) or "noir" (laser off).

    Returns
    -------
    (on, off): tuple[DataFrame, DataFrame] | None
        Tables with the wavelengths as index and the masses as columns.
        `None` if either the "ir" or the "noir" files are missing.

    """
    states = ir_df.columns.get_level_values("state")
    if "ir" not in states or "noir" not in states:
        return None

    on = ir_df.xs("ir", axis=1, level="state")
    off = ir_df.xs("noir", axis=1, level="state")
    return on, off


def filter_signal(state: AppState, m_threshold: float, cv_threshold: float) -> list[float]:
    """
    Filter the stable and physical signals, based on thresholds.

    A mass is kept when:
    1) it has a value for every wavelength, with the laser both on and off,
    2) the mean laser-off integral is larger than `m_threshold`,
    3) the std / mean of the laser-off integral is smaller than `cv_threshold`
       (a stable signal does not fluctuate between wavelengths).

    Parameters
    ----------
    state: AppState
        AppState containing at least `ir_df`
    m_threshold: float
        minimum signal intensity (of the integral)
    cv_threshold: float
        maximum ratio of std / mean

    Returns
    -------
    valid_masses: list[float]
        list of the masses that pass the filter

    """
    states = split_states(state.ir_df)
    if states is None:
        return []
    on, off = states

    complete = ~(on.isna().any() | off.isna().any())
    mean = off.mean()
    cv = off.std(ddof=0) / mean

    keep = complete & (mean > m_threshold) & (cv < cv_threshold)
    return [float(m) for m in off.columns[keep]]
