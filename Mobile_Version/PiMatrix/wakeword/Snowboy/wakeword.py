import snowboydecoder
import sys
import signal
import os
import time
from matrix_lite import led


interrupted = False
led_array = ['black' for i in range(35)]
led_array[0] = 'darkturquoise'
led.set(led_array)
time.sleep(3) #buffer time for emergency script lock device
#os.system('sudo ifconfig wlan0 down') #wifi
#os.system('vcgencmd display_power 0') #HDMI
#led.set(['red','black','black','black','black','orange','black','black','black','black','yellow','black','black','black','black','green','black','black','black','black','blue','black','black','black','black','indigo','black','black','black','black','violet','black''black''black''black'])

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

#if len(sys.argv) == 1:
#    print("Error: need to specify model name")
#    print("Usage: python demo.py your.model")
#    sys.exit(-1)

model = '/home/pi/Desktop/PiMatrix_firmware/PiMatrix/wakeword/Snowboy/Hello_Matrix.pmdl'
this_model = '/home/pi/Desktop/PiMatrix_firmware/PiMatrix/wakeword/Snowboy/Hello_Pi1.pmdl'
models = [model,this_model]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

sensitivity = [0.5] *len(models)
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=snowboydecoder.start_program,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
os._exit(1)

