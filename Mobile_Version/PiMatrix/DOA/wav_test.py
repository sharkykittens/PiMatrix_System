import wave
import scipy
import numpy
from scipy.io import wavfile


a = scipy.io.wavfile.read("/home/pi/Desktop/PiMatrix_firmware/PiMatrix/test.wav")
b = numpy.array(a[1], dtype=float)
"""
for i in range(len(b)):
    for j in range(len(b[i])):
        if b[i][j] > 2000:
            print(b[i])
print(len(numpy.array(a[1])))
"""

print(b)