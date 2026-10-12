import pandas as pd
import streamlit as st

from fcs_studio.app_state import get_state
from fcs_studio.tools import calibration
from fcs_studio.ui_components import sidebar, user_input


def main():
    st.title("Calibration Tool")

    state = get_state()

    sidebar.directory()
    user_input.data_selection()

    # Input
    with st.container(border=False):
        col1, col2 = st.columns(2)
        with col1:
            st.header("Data")
            state.plot_spectrum('time')

        # Input
        with col2:
            st.header("User Input")
            edited_df = st.data_editor(pd.DataFrame({'Time':[], 'Mass':[]}), num_rows="dynamic", width=500)

    st.divider()

    # Output
    with st.container(border=False):
        col1, col2 = st.columns(2)
        with col1:
            st.header("Fit Result")
            popt = calibration.fit(edited_df)
            calibration.plot(edited_df, popt)

        with col2:
            st.header('Export')
            st.write("$m = a(t-k)^2$")
           
            with st.form("Export"):
                st.metric("a", f'{popt[0]:.5f} amu/μs²')
                st.metric("k", f'{popt[1]:.5f} μs')

                label = st.text_input("Label")
                submitted = st.form_submit_button("Apply")

            if submitted:
                st.write(str(popt), str(label))
                calibration.apply(label, popt)
