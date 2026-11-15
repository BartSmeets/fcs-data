# FCS Studio

[![Streamlit](https://img.shields.io/badge/Powered_by-Streamlit-red?logo=streamlit)](https://streamlit.io/)

An interactive web app to quickly browse, calibrate and visualise ToF data recorded by the FCS setup. The data is loaded and processed with [`fcs_data`](../README.md).

## Running the app

From the root of the repository, install `fcs-data` together with the app dependencies:

```bash
pip install -e ".[studio]"
```

Then start the app from this folder:

```bash
cd studio
streamlit run Home.py
```

`fcs_studio` itself does not need to be installed: running Streamlit from the `studio` folder is enough to make it importable.

> The **Select Directory** button opens a folder dialog with `tkinter`. This ships with Python on Windows and macOS; on Linux you may need to install it separately (e.g. `sudo apt install python3-tk`). You can always type the path into the **Directory** field instead.

## Pages

### Home

- Pick a data directory in the sidebar and select one or more `.npy` files to overlay in a single plot.
- Switch between the time (µs) and mass (amu) axis.
- Set the mass calibration in the sidebar, by loading a stored configuration or by entering `a` and `k` manually.
- Toggle a pointer to mark a position on the spectrum.

### Calibration Tool

1. Select a spectrum and read off the arrival times of peaks with a known mass.
2. Enter the (time, mass) pairs in the table.
3. The tool fits `m = a(t - k)²` and plots the result next to your data.
4. Give the result a label and press **Apply** to store it and use it as the current calibration.

Here `a` and `k` correspond to `G` and `t_off` in `fcs_data.MassSpec`.

### IR Spectroscopy

For a series of IR laser measurements, this page integrates the signal at the detected masses and compares laser-on with laser-off signals as a function of wavelength. It can show the difference or the depletion, and masses can be filtered on a minimum integral value and a maximum std/mean ratio.

This page is currently being reworked.

**File names.** All `.npy` files in the selected directory that should be included must be named

```text
<prefix>_<value>_<IR|noIR>.npy
```

where `<value>` is the wavelength and `IR` / `noIR` marks laser on / off. Files that do not match this pattern are skipped.

## Calibration settings

The calibration constants are stored in `fcs_studio/config/calibration.toml`. This file is machine-specific, ignored by git, and created automatically from `calibration.toml.example` the first time the app runs.

```toml
[last_used]        # constants used when the app starts
a = 0.0925...
k = 0.3077...

[2026-11-15_my-label]   # added by the Calibration Tool: <date>_<label>
a = 0.0925...
k = 0.3077...
```

Entries are listed in the sidebar of the Home and IR Spectroscopy pages.

## Project layout

```text
studio/
├── Home.py                  # entry point (home page)
├── pages/                   # one thin wrapper per extra page; Streamlit builds the navigation from these
│   ├── 1_Calibration_Tool.py
│   └── 2_IR_Spectroscopy.py
└── fcs_studio/              # the app itself
    ├── app_state/           # AppState (kept in st.session_state), data/IR builders and plotting
    ├── config/              # calibration.toml(.example)
    ├── pages/               # page layouts: home, calibration, ir_spectroscopy
    ├── tools/               # calibration fit and IR filtering
    └── ui_components/       # reusable widgets: sidebar and data selection
```

The files in `pages/` only set up the page and call `main()` of the matching module in `fcs_studio/pages/`. To add a page, create the layout in `fcs_studio/pages/` and add a small wrapper in `pages/`. Shared state is accessed with `get_state()` from `fcs_studio.app_state`.
