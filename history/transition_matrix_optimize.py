"""
The simsignal optimizations are left in place; no successful optimization of
the current bottleneck has been found. Now, seeing if the transition matrix
routine that produces an error can be optimized.
Current testing notes:
T.M is dramatically sped up, but the bottleneck is the Hamiltonian.
"""

import numpy as np

from scipy.linalg import eigh
from scipy.sparse import kron, csc_matrix, csr_matrix, lil_matrix, bmat


def nlist(length):
    """
    creates a list (length) long of empty lists.
    This is probably redundant with a built-in python/numpy/scipy function,
    so consider replacing in future.
    Input:
        :param length: number of empty lists in list
    Returns:
        a list of [] x length

    """
    # noinspection PyUnusedLocal
    return [[] for l in range(length)]


def popcount(n=0):
    """
    Computes the popcount (binary Hamming weight) of integer n
    input:
        :param n: an integer
    returns:
        popcount of integer (binary Hamming weight)

    """
    return bin(n).count('1')


# noinspection PyShadowingNames
def is_allowed(m=0, n=0):
    """
    determines if a transition between two spin states is allowed or forbidden.
    The transition is allowed if one and only one spin (i.e. bit) changes
    input: integers whose binary codes for a spin state
        :param n:
        :param m:
    output: 1 = allowed, 0 = forbidden

    """
    return popcount(m ^ n) == 1


def transition_matrix(n):
    """
    Creates a matrix of allowed transitions.
    The integers 0-n, in their binary form, code for a spin state (alpha/beta).
    The (i,j) cells in the matrix indicate whether a transition from spin state
    i to spin state j is allowed or forbidden.
    See the is_allowed function for more information.

    input:
        :param n: size of the n,n matrix (i.e. number of possible spin states)

    :returns: a transition matrix that can be used to compute the intensity of
    allowed transitions.
    """
    # function was optimized by only calculating upper triangle and then adding
    # the lower.
    T = lil_matrix((n, n))  # sparse matrix created
    for i in range(n-1):
        for j in range(i+1, n):
            if is_allowed(i, j):
                T[i, j] = 1
    T = T + T.T
    return T


# noinspection PyShadowingNames
def hamiltonian(freqlist, couplings):
    """
    Computes the spin Hamiltonian for spin-1/2 nuclei.
    inputs for n nuclei:
        :param freqlist: a list of frequencies in Hz of length n
        :param couplings: a sparse n x n matrix of coupling constants in Hz
    Returns: a sparse Hamiltonian matrix
    """
    nspins = len(freqlist)
    print('Defining unit matrices')
    # Define Pauli matrices
    # change below back to csr if no improvement
    sigma_x = csc_matrix(np.matrix([[0, 1/2], [1/2, 0]]))
    sigma_y = csc_matrix(np.matrix([[0, -1j/2], [1j/2, 0]]))
    sigma_z = csc_matrix(np.matrix([[1/2, 0], [0, -1/2]]))
    unit = csc_matrix(np.matrix([[1, 0], [0, 1]]))
    print('Unit matrices defined')

    print('Generating lists of Lx/y/z matrices')
    # The following empty lists will be used to store the
    # Cartesian spin operators. Consider appending to empty lists instead, or
    # finding a way to store them in an array?

    Lx = nlist(nspins)
    Ly = nlist(nspins)
    Lz = nlist(nspins)

    for n in range(nspins):
        Lx_current = 1
        Ly_current = 1
        Lz_current = 1
        for k in range(nspins):
            # Need to use scipy kron, not np.kron with sparse matrices
            if k == n:  # Diagonal element

                Lx_current = kron(Lx_current, sigma_x)
                Ly_current = kron(Ly_current, sigma_y)
                Lz_current = kron(Lz_current, sigma_z)
            else:
                Lx_current = kron(Lx_current, unit)
                Ly_current = kron(Ly_current, unit)
                Lz_current = kron(Lz_current, unit)

        Lx[n] = Lx_current
        Ly[n] = Ly_current
        Lz[n] = Lz_current

    print('Lx/y/z matrices compiled')
    print('Calculating Hamiltonian')
    # Hamiltonian operator
    H = csc_matrix((2**nspins, 2**nspins))

    # Zeeman interactions:
    for n in range(nspins):
        H = H + freqlist[n] * Lz[n]
    print('Diagonal elements computed')
    # Scalar couplings

    # Testing with MATLAB discovered J must be /2.
    # Believe it is related to the fact that in the SpinDynamics.org simulation
    # freqs are *2pi, but Js by pi only. Video is supposed to explain why.

    for n in range(nspins):
        for k in range(nspins):
            if n != k:
                # noinspection PyTypeChecker
                H += (couplings[n, k] / 2) * (Lx[n] * Lx[k] +
                                              Ly[n] * Ly[k] +
                                              Lz[n] * Lz[k])
    print('Hamiltonian computed')
    return H


# noinspection PyPep8Naming
def simsignals(H, nspins):
    """
    Solves the spin Hamiltonian H and returns a list of (frequency, intensity)
    tuples. Nuclei must be spin-1/2.
    Inputs:
        :param H: a sparse spin Hamiltonian
        :param nspins: number of nuclei
    :return spectrum: a list of (frequency, intensity) tuples.

    """
    # This routine was optimized for speed by vectorizing the intensity
    # calculations, replacing a nested-for signal-by-signal calculation.

    print('Calculating eigensystem')

    # This calculation apparently must be done on a dense matrix, because eig
    # functions on sparse matrices can't return all answers?!
    # Using eigh so that answers have only real components and no residual small
    # j components b/c of rounding errors
    E, V = eigh(H.todense())  # V will be eigenvectors, v will be frequencies
    print('Eigensystem solved; converting eigenvectors to sparse')

    # Eigh still leaves residual 0j terms, so:
    V = np.asmatrix(V.real)

    Vcol = csc_matrix(V)
    print('V converted to csc matrix.')

    Vrow = csr_matrix(Vcol.T)
    print('V.T created as csr matrix.')

    m = 2 ** nspins
    print('Calculating the transition matrix')
    T = transition_matrix(m)
    print('Transition matrix calculated')

    print('Collecting spectrum')
    spectrum = []
    print('Creating intensity matrix')
    I = Vrow * T * Vcol
    print('Intensity matrix created')
    print('Squaring intensity matrix')
    I = np.square(I.todense())
    print('Intensity matrix squared')
    for i in range(m-1):
        for j in range(i+1, m):
            if I[i, j] > 0.01:  # consider making this minimum intensity
                                # cutoff a function arg, for flexibility
                v = abs(E[i] - E[j])
                spectrum.append((v, I[i, j]))
    print('Spectrum obtained.')
    return spectrum


# noinspection PyUnreachableCode,PyPep8Naming
def nspinspec(freqs, couplings):
    """
    Function that calculates a spectrum for n spin-half nuclei.
    Inputs:
        :param freqs: a list of n nuclei frequencies in Hz
        :param couplings: an n x n sparse matrix of couplings in Hz. The order
        of nuclei in the list corresponds to the column and row order in the
        matrix, e.g. couplings[0][1] and [1]0] are the J coupling between
        the nuclei of freqs[0] and freqs [1].
    """
    nspins = len(freqs)
    H = hamiltonian(freqs, couplings)
    return simsignals(H, nspins)


if __name__ == '__main__':
    from nspin import reich_list
    from nmrplot import nmrplot as nmrplt

    test_freqs, test_couplings = reich_list()[8]
    test_spectrum = nspinspec(test_freqs, test_couplings)
    nmrplt(test_spectrum, y=24)
