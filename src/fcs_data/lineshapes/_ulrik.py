import numpy as np


def ulrik(
        x: np.ndarray,
        amp: float, 
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
    amp: float
        Amplitude
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
    Model:
        lmfit model for ulrik lineshape
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
        
    return amp * np.where(
        x > center, 
        GL(x, center, width, m), 
        GL(x, center, width, m) + w(a,b) * (AW(x, center, width, a) - G(x, center, width)))