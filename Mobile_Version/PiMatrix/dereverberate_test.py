import numpy as np
import soundfile as sf
from tqdm import tqdm
import scipy
from scipy.io import wavfile
from nara_wpe.wpe import wpe
from nara_wpe.wpe import get_power
from nara_wpe.utils import stft, istft, get_stft_center_frequencies
from nara_wpe import project_root

stft_options = dict(size=256, shift=64)
a = scipy.io.wavfile.read("/home/pi/Desktop/PiMatrix_firmware/PiMatrix/test.wav")
signal_list = np.array(a[0], dtype=float)

y = np.stack(signal_list, axis=0)
Y = stft(y, **stft_options).transpose(2, 0, 1)
Z = wpe(
    Y,
    taps=10,
    delay=3,
    iterations=5,
    statistics_mode='full'
).transpose(1, 2, 0)
z = istft(Z, size=stft_options['size'], shift=stft_options['shift'])
#print(z)