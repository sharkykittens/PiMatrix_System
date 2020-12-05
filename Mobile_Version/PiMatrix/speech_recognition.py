from pocketsphinx import AudioFile 



for phrase in AudioFile(audio_file='/home/pi/Desktop/PiMatrix_firmware/PiMatrix/test.wav'):
    print(phrase)
