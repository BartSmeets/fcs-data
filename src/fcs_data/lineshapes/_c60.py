import numpy as np

from ._ulrik import ulrik

_PROTON = 1.007276  # Mass of a proton

def c60(
        x: np.ndarray,
        h0: float,
        h1: float,
        h2: float,
        h3: float,
        center: float,
        width: float,
        a: float,
        b: float,
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
    return sum(ulrik(x, h, center + i*_PROTON, width, a, b) for i, h in enumerate(hs))