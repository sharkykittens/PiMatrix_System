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
import music
from scipy.io import wavfile
import wave
import pyximport

pyximport.install()

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
s2_aoa = (pi/2+pi/6, 0)
s1 = util.makesamples(matrix_array, s1_aoa[0], s1_aoa[1], nsamp)
#s2 = util.makesamples(matrix_array, s2_aoa[0], s2_aoa[1], nsamp)
print("s1")
print(s1)
#print("s2")
#print(s2)

samples = s1
samples = util.awgn(samples, snr)
print("samples")
print(samples)

a = scipy.io.wavfile.read("wavfile.wav")
b = np.array(a[1], dtype=float)


R = music.covar(b)
print(R)
est = music.Estimator(matrix_array,R,nsignals=1)

## perform DOA search

print("s1 is {}".format(s1_aoa))
#print("s2 is {}".format(s2_aoa))
s1_est = music.Estimator(matrix_array,music.covar(s1),nsignals=1)
#s2_est = music.Estimator(matrix_array,music.covar(s2),nsignals=1)
# s1
t1 = time()
s1_res = s1_est.doasearch()[0]
t1 = time() - t1
s1_err = sp.rad2deg(util.aoa_diff_rad(s1_res,s1_aoa))
print("s1: found {} in {}s, error {} deg".format(s1_res,t1,s1_err))
# s2
#t2 = time()
#s2_res = s2_est.doasearch()[0]
#t2 = time() - t2
#s2_err = sp.rad2deg(util.aoa_diff_rad(s2_res,s2_aoa))
#print("s2: found {} in {}s, error {} deg".format(s2_res,t2,s2_err))
# both signals
bothres = est.doasearch()
print("Both signals:\n{}".format(bothres))
# timing
print("Both signals in degrees:")
print(np.rad2deg(s1_aoa))
print(np.rad2deg(s1_res))
#print(np.rad2deg(s2_aoa))
#print(np.rad2deg(s2_res))
