"""The plt module provides convenience functions for creating matplotlib plots,
plus applying Lorentzian distributions about signals.

The plt module provides the following functions:

* add_lorentzians: Creates lineshape data from a provided linspace (array of x
  coordinates) and peaklist).
* mplplot: Creates a lineshape plot from a peaklist and returns the x, y plot
data.
* mplplot_stick: Creates a "stick" (matplotlib "stem" plot) plot from a
peaklist and returns the x, y plot data.
* mplplot_lineshape: Creates a lineshape plot from provided x, y lineshape data
and returns the x, y plot data.

"""

import matplotlib.pyplot as plt
import numpy as np

from nmrtools.math import lorentz


def add_lorentzians(linspace, peaklist, w):
    """
    Given a numpy linspace, a spectrum as a list of (frequency, intensity)
    tuples, and a linewidth, returns an array of y coordinates for the
    total line shape.

    Arguments
    ---------
    linspace : array-like
        Normally a numpy.linspace of x coordinates corresponding to frequency
        in Hz.
    peaklist : [(float, float)...]
        A list of (frequency, intensity) tuples.
    w : float
        Peak width at half maximum intensity.

    Returns
    -------
    [float...]
        an array of y coordinates corresponding to intensity.
    """
    # TODO: consider naming, and confusion with .math.add_peaks
    # TODO: function looks clunky. Refactor?
    result = lorentz(linspace, peaklist[0][0], peaklist[0][1], w)
    for v, i in peaklist[1:]:
        result += lorentz(linspace, v, i, w)
    return result


def mplplot(peaklist, w=1, y_min=-0.01, y_max=1, points=800, limits=None):
    """
    A matplotlib plot of the simulated lineshape for a peaklist.

    Parameters
    ----------
    peaklist : [(float, float)...]
        A list of (frequency, intensity) tuples.
    w : float
        Peak width at half height
    y_min : float or int
        Minimum intensity for the plot.
    y_max : float or int
        Maximum intensity for the plot.
    points : int
        Number of data points.
    limits : (float, float)
        Frequency limits for the plot.

    Returns
    -------
    x, y : numpy.array
        Arrays for frequency (x) and intensity (y) for the simulated lineshape.
    """
    peaklist.sort()
    if limits:
        try:
            l_limit, r_limit = limits
            l_limit = float(l_limit)
            r_limit = float(r_limit)
        except Exception as e:
            print(e)
            print('limits must be a tuple of two numbers')
            raise
        if l_limit > r_limit:
            l_limit, r_limit = r_limit, l_limit
    else:
        l_limit = peaklist[0][0] - 50
        r_limit = peaklist[-1][0] + 50
    x = np.linspace(l_limit, r_limit, points)
    plt.ylim(y_min, y_max)
    plt.gca().invert_xaxis()  # reverses the x axis
    y = add_lorentzians(x, peaklist, w)
    # noinspection PyTypeChecker
    plt.plot(x, y)
    plt.show()
    return x, y
    # TODO: or return plt? Decide behavior


def mplplot_stick(peaklist, y_min=-0.01, y_max=1, limits=None):
    """A  matplotlib plot of a spectrum in "stick" (stem) style.

    Parameters
    ----------
    peaklist : [(float, float)...]
        A list of (frequency, intensity) tuples.
    y_min : float or int
        Minimum intensity for the plot.
    y_max : float or int
        Maximum intensity for the plot.
    limits : (float, float)
        Frequency limits for the plot.

    Returns
    -------
    numpy.array, numpy.array
        The arrays of x and y coordinates used for the plot.
    """
    fig, ax = plt.subplots()
    if limits:
        try:
            l_limit, r_limit = limits
            l_limit = float(l_limit)
            r_limit = float(r_limit)
        except Exception as e:
            print(e)
            print('limits must be a tuple of two numbers')
            raise
        if l_limit > r_limit:
            l_limit, r_limit = r_limit, l_limit
    else:
        l_limit = sorted(peaklist)[0][0] - 50
        r_limit = sorted(peaklist)[-1][0] + 50
    x, y = zip(*peaklist)
    # If the next two lines are omitted, there is no baseline from the outer
    # peaks to the left/right limits. Until a matplotlib solution is found,
    # using this hack of adding two outer miniscule peaks to extend the
    # baseline.
    x = np.append(x, [l_limit, r_limit])
    y = np.append(y, [0.001, 0.001])
    plt.xlim(r_limit, l_limit)
    plt.ylim(y_min, y_max)
    ax.stem(x, y, markerfmt=' ', basefmt='C0-')
    plt.show()
    return x, y
    # TODO: or return plt object? Decide behavior.


def mplplot_lineshape(x, y, y_min=None, y_max=None, limits=None):
    """
    A matplotlib plot that accepts arrays of x and y coordinates.

    Parameters
    ----------
    x : array-like
        The list of x coordinates.
    y : array-like
        The list of y coordinates.
    y_min : float or int
        Minimum intensity for the plot. Default is -10% max y.
    y_max : float or int
        Maximum intensity for the plot. Default is 110% max y.
    limits : (float, float)
        Frequency limits for the plot.

    Returns
    -------
    x, y : The original x, y arguments.
    """
    if limits:
        try:
            l_limit, r_limit = limits
            l_limit = float(l_limit)
            r_limit = float(r_limit)
        except Exception as e:
            print(e)
            print('limits must be a tuple of two numbers')
            raise
        if l_limit > r_limit:
            l_limit, r_limit = r_limit, l_limit
    else:
        l_limit = min(x)  #x[0]  # assumes x already sorted low->high
        r_limit = max(x)  #x[-1]

    if y_min is None or y_max is None:  # must test vs None so that 0 = True
        margin = max(y) * 0.1
        if y_min is None:
            y_min = min(y) - margin
        if y_max is None:
            y_max = max(y) + margin
    plt.xlim(r_limit, l_limit)  # should invert x axis
    plt.ylim(y_min, y_max)
    plt.plot(x, y)
    plt.show()
    return x, y
