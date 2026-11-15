import streamlit as st

from fcs_studio.app_state import get_state
from fcs_studio.tools import ir_tools
from fcs_studio.ui_components import sidebar

# Your imports
# from analysis.ir import filter, integrated_signals
# from app.data_io import gen_csv, get_all_data
# from app.plotting import plot_on_off_difference

def main():
    """
    Build the IR Spectroscopy page

    """
    st.title("IR Spectroscopy")

    state = get_state()

    sidebar.directory()
    sidebar.calibration()

    # Input
    _ = st.text_input(
        "Data folder",
        value= state.directory,
        disabled=True
    )

    with st.expander("Files"):
        files = state.directory.glob("*.npy")
        st.dataframe(files)

    # Buttons
    # This markdown is needed to nicely space the buttons
    # Source - https://stackoverflow.com/a/77332142
    st.markdown("""
                <style>
                    div[data-testid="stColumn"] {
                        width: fit-content !important;
                        flex: unset;
                    }
                    div[data-testid="stColumn"] * {
                        width: fit-content !important;
                    }
                </style>
                """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        _ = st.button("🔄 Refresh folder")
    with col2:
        if st.button("Run Integration", disabled=(not state.directory.exists())):
            state.build_ir()

    if state.ir_df is not None:
        if not st.toggle("difference | depletion mode", value=False):
            mode = "diff"
        else:
            mode = "depl"

        # Filter
        col1, col2 = st.columns(2)
        with col1:
            m_threshold = st.number_input("Minimum integral value",
                                          min_value=0.0,
                                          value=0.0)
        with col2:
            cv_threshold = st.number_input("Maximum std/mean value",
                                           min_value=0.0,
                                           value=0.5)
        valid_masses = ir_tools.filter_signal(state, m_threshold, cv_threshold)

        selected_masses = st.multiselect(
            "Masses to show",
            options = valid_masses,   # only offer masses that actually have data
            default = valid_masses,
        )

        state.plot_ir(selected_masses, mode)