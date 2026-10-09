from pathlib import Path

import numpy as np
from lmfit import Model, Parameters
from lmfit.model import ModelResult
from pybaselines import Baseline


class MassSpec:
    """
    Class that handles the mass spectrum data

    Provides intuitive access to the different axes and properties (e.g. self.time instead of data[:, 0])

    Attributes
    ----------
    file: Path
        Path to the `.npy` that stores the data.
    voltage: ndarray
        Array containing the (baseline-corrected) signal intensity as accumulated voltage
    time: ndarray
        Array containing the original time axis of the data
    mass: ndarray
        Array containing the assigned masses corresponding to `time`.
        These values are obtained from `self.calibrate` upon initiation,
        but can be updated later.
    baseline: ndarray
        Array containing the signal intesity (accumulated voltage) of the baseline.
        Calculated using the default settings of `pybaselines.Baseline`.
    
    Methods
    -------
    calibrate(G, t_off):
        Performs mass calibration and updates `self.mass`.
    fit(model, model_params, mass_range):
        Performs a fit of the `model` to the data.
    """
    def __init__(self, file: Path, init_params: tuple[float, float]):
        """
        Load the data and perform a first calibration

        Parameters
        ----------
        file: Path
            File path to a `.npy` file collected from the FCS
        init_params: tuple
            Initial calibration parameters

        """
        # Read data
        self.file = file
        raw_data = np.load(file)

        # Read Axes
        time = raw_data[:, 0] * 1e6    # us
        self.voltage = - raw_data[time >= 0, 1]
        self.time = time[time >= 0]
        self.calibrate(*init_params)

        # Baseline Correction
        baseline_fitter = Baseline(x_data=self.mass)
        self.baseline = baseline_fitter.imodpoly(self.voltage)[0]
        self.voltage -= self.baseline

    def calibrate(self, G: float, t_off: float) -> np.ndarray:
        """
        Performs the mass calibration, i.e., convert the time axis into a mass axis

        Parameters
        ----------
        G: float
            Coefficient
        t_off: float
            Time offset <- Inability to locate the exact extraction timing
        
        """
        self.G, self.t_off = G, t_off
        self.mass = G * (self.time - t_off)**2

    def fit(self, model: Model, mass_range: tuple[float, float], model_params: Parameters | None = None) -> ModelResult:
        """
        Fit a `lmfit.Model` to part of the data.

        Common models are defined in `fcs_data.fit_models`

        Parameters
        ----------
        model: Model
            Fit model
        mass_range: tuple[float, float]
            Mass range oto include in the fit.
        model_params: Parameters | None, default=None
            Model parameters

        Returns
        -------
        ModelResult
            `lmfit` result

        """
        # Set range
        if mass_range[0] >= mass_range[1]:
            raise ValueError(f"The range should be ascending, now {mass_range}.")
        
        mask = (self.mass >= mass_range[0]) & (self.mass <= mass_range[1])            
        x = self.mass[mask]
        y = self.voltage[mask]

        if model_params is None:
            return model.fit(y, x=x)
        else:
            return model.fit(y, model_params, x=x)
