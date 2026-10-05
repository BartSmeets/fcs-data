import numpy as np
from lmfit import Model
from lmfit.model import ModelResult
from scipy.stats import binom

from utils.load_data import Data

_PROTON = 1.007276  # Mass of a proton
_PC13 = 0.0107  # Abundance of C13


def ulrik(x: np.ndarray, 
          center: float, 
          width: float, 
          a: float, 
          b:float, 
          m: float=0.0
          ) -> np.ndarray:
    """
    Emperical asymmetric lineshape used in XPS by Ulrik Gelius, Uppsala Sweden.
    Seems to work quite well for our mass spec too.

    The model consists of a symmetric Gaussian-Lorentzian peak (GL) and an
    additional asymmetry correction applied only on the low-x side of the peak:
    
        I(x) = GL(x) for x > center
        I(x) = GL(x) + w(a,b) * (AW(x) - G(x)) for x <= center

    where G is a Gaussian reference peak, AW is an asymmetric Gaussian-like
    function, and w(a,b) scales the asymmetry contribution.
    
    Parameters
    ----------
    x: ndarray
        Coordinates
    center: float
        Peak position
    width: float
        Controls the FWHM-like width of the peak
    a: float
        Asymmetric shape parameter
    b: float
        Asymmetric strength parameter
    m: float, default=0
        Gaussian-Lorentzian mixing parameter

    Returns
    -------
    lineshape: np.ndarray

    """
    def GL(x, center, width, m):
        """
        Symmetric core.
        Gaussian-Lorentzian lineshape.

        """
        teller = -4 * np.log(2) * (1 - m) * (x - center)**2 / (width**2)
        noemer = (1 + 4 * m * (x - center)**2 / (width**2))
        return np.exp(teller) / noemer

    def G(x, center, width):
        """
        Gaussian reference peak

        """
        return np.exp(-4 * np.log(2) * (x - center)**2 / width**2)
    
    def w(a, b):
        """
        Assymetry weighing function

        """
        return b * (0.7 + 0.3 / (a + 0.01))
    
    def AW(x, center, width, a):
        """
        Asymmetric Gaussian-like function

        """
        teller = 2 * np.sqrt(np.log(2)) * (x - center)
        noemer = width - a*2*np.sqrt(np.log(2))*(x - center)
        return np.exp(-(teller/noemer)**2)
        
    return np.where(
        x > center, 
        GL(x, center, width, m), 
        GL(x, center, width, m) + w(a,b) * (AW(x, center, width, a) - G(x, center, width)))


def c60(x: np.ndarray, 
        h0: float, 
        h1: float, 
        h2: float, 
        h3: float, 
        center: float, 
        width: float, 
        a: float, 
        b: float
        ) -> np.ndarray:
    """
    C60 lineshape consisting of four visible isotope peaks.

    Combines four `ulrik` lineshapes with identical width and asymmetry,
    but varying amplitudes (h) and center (obviously).

    Parameters
    ----------
    x: ndarray
        Coordinates
    h0, h1, h2, h3: float
        amplitudes of the four visible isotope peaks
    center: float
        Peak position
    width: float
        Controls the FWHM-like width of the peak
    a: float
        Asymmetric shape parameter
    b: float
        Asymmetric strength parameter

    Returns
    -------
    lineshape: ndarray
        Lineshape of the C60

    """
    hs = (h0, h1, h2, h3)
    return sum(h * ulrik(x, center + i*_PROTON, width, a, b) for i, h in enumerate(hs))


def fit_reference(data: Data, window: tuple[float], center: float | None = None):
    """
    Fit the C60 model to the reference data.
    This will fit a simple C60 lineshape to the data within a given window.

    Parameters
    ----------
    data: Data
        data object
    window: tuple[float]
        Range of the x-coordinate of the data to fit to
    center: float | None, default = None
        initial guess of the center position.
        If None, the maximum within the range will be considered the center

    Returns
    -------
    result: ModelResult
        fitting result

    """
    # Read data and set range
    mask = (data.mass >= window[0]) & (data.mass < window[1])
    x = data.mass[mask]
    y = data.voltage[mask]

    # First guess for amplitude
    if center is None:
        index = np.argmax(y)
        center = x[index]
        amp = y[index]
    else:
        index = np.argmin(np.abs(x - center))
        amp = y[index]

    # Model
    model = Model(c60)
    params = model.make_params(
        h0 = amp,
        h1 = amp * binom.pmf(1, 60, _PC13) / binom.pmf(0, 60, _PC13),
        h2 = amp * binom.pmf(2, 60, _PC13) / binom.pmf(0, 60, _PC13),
        h3 = amp * binom.pmf(3, 60, _PC13) / binom.pmf(0, 60, _PC13),
        center = center,
        width = 1.0,
        a = 0.5,
        b = 0.5,
    )

    return model.fit(y, params, x=x)


def fit_doped(data: Data, 
              reference: ModelResult, 
              window: tuple[float], 
              added_mass: float, 
              free_shape: bool = False,
              ):
    """
    Fit a composite model of two C60s to the data within a certain range:

    model(x; center, c1, c2, w) = c1 * c60(x; center, w) + c2 * c60(x; center + added_mass, w)

    where `center`, `c1`, `c2` and `w` are fitting parameters for
    the peak position, 
    scaling factor of the first and second peak,
    and an added width with respect to the reference peak.

    Parameters
    ----------
    data: Data
        Data object
    reference: ModelResult
        Fitting result of the reference peak
        Is used to set the lineshape and initial guess for the fit
    window: tuple[float]
        Range of the x-coordinate of the data to fit to
    added_mass: float
        Mass shift (x-coordinate) of the dopant
    free_shape: bool, default = False
        Whether the asymmetric shape should be fitted too.

    Returns
    -------
    result: ModelResult

    """
    # Read data and set range
    mask = (data.mass >= window[0]) & (data.mass < window[1])
    x = data.mass[mask]
    y = data.voltage[mask]

    ref = reference.best_values

    model = Model(c60, prefix='p1_') + Model(c60, prefix='p2_')
    params = model.make_params()

    # To Fit
    params.add("center", value=ref['center'])
    params.add("c1", value = np.max(y) / ref['h0'], min = 0.0)
    params.add("c2", value = np.max(y) / ref['h0'], min = 0.0)
    params.add("w", value = 0.0)

    # Tie parameters together
    params["p1_center"].set(expr="center")
    params["p2_center"].set(expr=f"center + {added_mass}")
    for prefix, c in [["p1_", "c1"], ["p2_", "c2"]]:
        params[prefix + "width"].set(expr=f"{ref['width']} + w")
        for i in range(4):
            params[f"{prefix}h{i}"].set(expr=f"{c} * {ref[f'h{i}']}")

    # Shape parameters
    for prefix in ["p1_", "p2_"]:
        for key in ("a", "b"):
            params[prefix + key].set(value=ref[key], vary=free_shape)

    return model.fit(y, params, x=x)
