from __future__ import absolute_import, division, print_function
import cProfile
import sys
from time import time
import itertools
import numpy as np
import scipy as sp
import scipy.misc
import scipy.constants
from scipy import pi
import util

# 16 element unit circle in the y-z plane
antx = sp.arange(16)
circarray = sp.array([0*antx, sp.cos(antx), sp.sin(antx)]).T

wavelength = sp.constants.c/2.477e9
print(wavelength)

# each element is a cartesian coordinate of the sensor with respect to center in metres (x,y,z)
matrix_array = np.array([[0.02, -0.048, 0], [-0.02, -0.048, 0], [-0.048, -0.02, 0], [-0.048, 0.02, 0],
                         [-0.02, 0.048, 0], [0.02, 0.048, 0], [0.048, 0.02, 0], [0.048, -0.02, 0]])

nsamp = 21
snr = -6

s1_aoa = (pi/2, 0)
s2_aoa = (pi/2+pi/6, -pi/6)
s1 = util.makesamples(matrix_array, s1_aoa[0], s1_aoa[1], nsamp)
s2 = util.makesamples(matrix_array, s2_aoa[0], s2_aoa[1], nsamp)
print("s1")
print(s1)
print("s2")
print(s2)

samples = s2 + s1
samples = util.awgn(samples, snr)
print("samples")
print(samples)

# add noise to s1 and s2
s1 = util.awgn(s1, snr)
s2 = util.awgn(s2, snr)
