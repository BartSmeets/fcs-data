# FCS Data

Python package for handling FCS mass spectrometry data: from reading the raw data files to analysis tools (calibration, baseline correction, integration, peak finding and peak fitting).

## Features

- Load `.npy` data files collected from the FCS
- Time-of-flight to mass calibration
- Automatic baseline correction
- Integration of mass ranges
- Peak finding
- Peak fitting with [`lmfit`](https://lmfit.github.io/lmfit-py/), including ready-made lineshapes (`c60`, `gelius`)
- [FCS Studio](#fcs-studio): an interactive [Streamlit](https://streamlit.io/) app to browse, calibrate and visualise your data

## Installation

Clone the repository and install the package in editable mode:

```bash
git clone https://github.com/BartSmeets/fcs-data.git
cd fcs-data
pip install -e .
```

To also run the [FCS Studio](#fcs-studio) app, install the optional `studio` dependencies:

```bash
pip install -e ".[studio]"
```

### Requirements

- Python 3.10+
- [NumPy](https://numpy.org/) 2.0+
- [SciPy](https://scipy.org/)
- [lmfit](https://lmfit.github.io/lmfit-py/)
- [pybaselines](https://pybaselines.readthedocs.io/)

The `studio` extra additionally installs [Streamlit](https://streamlit.io/), [Plotly](https://plotly.com/python/), [pandas](https://pandas.pydata.org/) and [toml](https://github.com/uiri/toml).

## API overview

### `MassSpec(file, init_params)`

| Member                                              | Description                                                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `file`                                              | Path to the `.npy` file                                                                                |
| `time`                                              | Time axis (µs)                                                                                         |
| `mass`                                              | Mass axis corresponding to `time`                                                                      |
| `voltage`                                           | Baseline-corrected signal (accumulated voltage)                                                        |
| `baseline`                                          | Baseline of the signal                                                                                 |
| `calibrate(G, t_off)`                               | Perform the mass calibration and update `mass`                                                         |
| `fit(model, mass_range, model_params=None)`         | Fit an `lmfit.Model` to part of the data                                                               |
| `integrate(mass_range)`                             | Integrate the spectrum over a mass range                                                               |
| `find_peaks(mass_range, prominence=None, **kwargs)` | Find peaks; returns peak masses, peak heights, FWHMs and the properties from `scipy.signal.find_peaks` |
| `mass_filter(mass_range)`                           | Return the mass and voltage arrays restricted to a mass range                                          |

## Usage

### Loading a mass spectrum

```python
from pathlib import Path
from fcs_data import MassSpec

# init_params = (G, t_off), the initial calibration parameters
ms = MassSpec(Path("data/measurement.npy"), init_params=(G, t_off))

ms.time      # time axis (µs)
ms.mass      # mass axis, from the calibration
ms.voltage   # baseline-corrected signal (accumulated voltage)
ms.baseline  # the baseline that was subtracted
```

The data file is expected to be a `.npy` array with the time (in seconds) in the first column and the signal in the second column. On loading, the package:

1. converts the time axis to µs and discards negative times,
2. inverts the sign of the signal,
3. converts time to mass using the initial calibration,
4. subtracts a baseline calculated with `pybaselines.Baseline.imodpoly` (default settings).

### Mass calibration

The time axis is converted to a mass axis with

```text
mass = G * (time - t_off)²
```

where `G` is a coefficient and `t_off` is a time offset (the exact extraction time cannot be located precisely). The calibration can be updated at any point:

```python
ms.calibrate(G=new_G, t_off=new_t_off)
```

In [FCS Studio](#fcs-studio) these constants are called `a` and `k` respectively.

### Integration

Integrate the spectrum over a mass range using the composite trapezoid rule:

```python
area = ms.integrate(mass_range=(715, 725))
```

### Peak finding

`MassSpec.find_peaks` is a thin wrapper around `scipy.signal.find_peaks`. If no `prominence` is given, it is estimated from the noise level of the spectrum (5 times a robust noise estimate). Any extra keyword arguments (e.g. `height`, `distance`, `width`) are passed on to SciPy.

```python
masses, heights, fwhm, props = ms.find_peaks(mass_range=(700, 760))
```

Use `mass_range=None` to search the whole spectrum.

### Fitting

`MassSpec.fit` fits an `lmfit.Model` to a selected mass range and returns an `lmfit.model.ModelResult`:

```python
from lmfit import Model
from fcs_data import MassSpec
from fcs_data.lineshapes import c60

model = Model(c60)
params = model.make_params(
    h0=1.0, h1=0.6, h2=0.2, h3=0.05,
    center=720.0, width=0.1, a=0.0, b=0.0,   # illustrative starting values
)

result = ms.fit(model, mass_range=(715, 725), model_params=params)
print(result.fit_report())
```

If `model_params` is omitted, the model's own default parameters are used. The mass range must be ascending, otherwise a `ValueError` is raised.

## FCS Studio

The [`studio`](studio/) folder contains **FCS Studio**, an interactive web app built with [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/python/) for quickly inspecting ToF data recorded by the FCS setup, without writing any code. It uses `fcs_data.MassSpec` to load and process the data.

To run it, install the package with the `studio` extra (see [Installation](#installation)) and start the app from the `studio` folder:

```bash
cd studio
streamlit run Home.py
```

The app offers:

- **Home**: select a data folder, overlay one or more spectra on the time or mass axis, adjust the mass calibration and place a pointer on the spectrum.
- **Calibration Tool**: fit the calibration constants from known (time, mass) pairs and store them under a label for later use.
- **IR Spectroscopy**: integrate the signal at the detected masses for a series of laser-on/laser-off measurements (work in progress).

See [`studio/README.md`](studio/README.md) for the details.

## Lineshapes

The `fcs_data.lineshapes` subpackage contains lineshape functions that can be wrapped in an `lmfit.Model`.

| Function | Description                                                                                                                                                                                        |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gelius` | Empirical asymmetric lineshape (originally used in XPS, after Ulrik Gelius): a Gaussian-Lorentzian core with an asymmetry correction on the low-mass side of the peak.                             |
| `c60`    | C60 lineshape: four visible isotope peaks built from `gelius` lineshapes with identical width and asymmetry, but different amplitudes. Consecutive peaks are spaced by one proton mass (1.007276). |

### `gelius` parameters

| Parameter | Description                                                                |
| --------- | -------------------------------------------------------------------------- |
| `x`       | Coordinates (mass axis)                                                    |
| `amp`     | Amplitude                                                                  |
| `center`  | Peak position                                                              |
| `width`   | Controls the FWHM-like width of the peak                                   |
| `a`       | Asymmetric shape parameter                                                 |
| `b`       | Asymmetric strength parameter                                              |
| `m`       | Gaussian-Lorentzian mixing parameter (default `0.0`, i.e. a Gaussian core) |

### `c60` parameters

| Parameter              | Description                                  |
| ---------------------- | -------------------------------------------- |
| `x`                    | Coordinates (mass axis)                      |
| `h0`, `h1`, `h2`, `h3` | Amplitudes of the four visible isotope peaks |
| `center`               | Peak position                                |
| `width`                | Controls the FWHM-like width of the peak     |
| `a`                    | Asymmetric shape parameter                   |
| `b`                    | Asymmetric strength parameter                |

```python
from fcs_data.lineshapes import c60, gelius

y_c60 = c60(x, h0=1.0, h1=0.6, h2=0.2, h3=0.05, center=720.0, width=0.1, a=0.0, b=0.0)
y_peak = gelius(x, amp=1.0, center=720.0, width=0.1, a=0.0, b=0.0)
```
