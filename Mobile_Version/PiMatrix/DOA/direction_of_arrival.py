"""
Reads sample data and then returns estimates of direction of arrival

takes in array of 8 channel data, finds which channels give the maximum and return the corresponding microphone

also lights up the corresponding LED according to the signal source

"""

from matrix_lite import led


def estimateDOA():
    LED_array = [0]
    LED_pointer = 0
    mic1 = []
    mic2 = []

    # reset the LED
    LED_array[LED_pointer] = "black"
    led.set(LED_pointer)
    LED_pointer = 5  # whatever new value
    LED_array[LED_pointer] = 'pink'  # or whatever color
