import numpy as np

from nmrtools.firstorder import *
from nmrtools.firstorder import _normalize  # temporary
from nmrtools.nmrplot import mplplot_stick
from tests.simulation_data import rioux


def test_doublet():
    refspec = [(95, 0.5), (105, 0.5)]
    testspec = sorted(doublet([(100, 1)], 10))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_multiplet():
    # Inputs: simulate n-propanol
    refspec = sorted([
        (1193.0, 0.5), (1200.0, 0.5), (1200.0, 0.5), (1207.0, 0.5),
        (432.5, 0.0625), (439.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (446.5, 0.0625), (453.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (446.5, 0.0625),
        (453.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (460.5, 0.0625), (467.5, 0.0625),
        (293.0, 0.75), (300.0, 0.75), (300.0, 0.75), (307.0, 0.75)])
    v1 = (1200, 2)
    v2 = (450, 2)
    v3 = (300, 3)
    J12 = 7
    J23 = 7
    m1 = multiplet(v1, [(J12, 2)])
    m2 = multiplet(v2, [(J12, 2), (J23, 3)])
    m3 = multiplet(v3, [(J23, 2)])

    testspec = sorted(m1 + m2 + m3)
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_reduce_peaks():
    refspec = [(293.0, 0.75), (300.0, 1.5), (307.0, 0.75),
               (432.5, 0.0625), (439.5, 0.3125), (446.5, 0.625),
               (453.5, 0.625), (460.5, 0.3125), (467.5, 0.0625),
               (1193.0, 0.5), (1200.0, 1.0), (1207.0, 0.5)]
    tobereduced = sorted([
        (1193.0, 0.5), (1200.0, 0.5), (1200.0, 0.5), (1207.0, 0.5),
        (432.5, 0.0625), (439.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (446.5, 0.0625), (453.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (446.5, 0.0625),
        (453.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (460.5, 0.0625), (467.5, 0.0625),
        (293.0, 0.75), (300.0, 0.75), (300.0, 0.75), (307.0, 0.75)
    ])
    testspec = sorted(reduce_peaks(tobereduced))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_normalize():
    intensities = [1, 3, 4]
    _normalize(intensities)
    assert intensities == [0.125, 0.375, 0.5]
    double_intensities = [1, 3, 3, 1]
    _normalize(double_intensities, 2)
    assert double_intensities == [0.25, 0.75, 0.75, 0.25]


def test_normalize_spectrum():
    pass


def test_first_order():
    refspec = [(293.0, 0.75), (300.0, 1.5), (307.0, 0.75),
               (432.5, 0.0625), (439.5, 0.3125), (446.5, 0.625),
               (453.5, 0.625), (460.5, 0.3125), (467.5, 0.0625),
               (1193.0, 0.5), (1200.0, 1.0), (1207.0, 0.5)]
    v1 = (1200, 2)
    v2 = (450, 2)
    v3 = (300, 3)
    J12 = 7
    J23 = 7
    m1 = first_order(v1, [(J12, 2)])
    m2 = first_order(v2, [(J12, 2), (J23, 3)])
    m3 = first_order(v3, [(J23, 2)])
    testspec = reduce_peaks(sorted(m1 + m2 + m3))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_first_order_spin_system():
    v, J = rioux()
    spectrum = first_order_spin_system(v, J)
    print(spectrum)
    x = np.array([i[0] for i in spectrum])
    y = np.array([i[1] for i in spectrum])
    mplplot_stick(x, y)
    assert 1 == 1


# work in progress
# def test_spectrum_from_signals():
#     signals = [((1200, 2), [(7, 2)])]
#     pass
