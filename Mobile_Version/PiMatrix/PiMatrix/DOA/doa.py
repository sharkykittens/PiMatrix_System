
from matrix_lite import led
from collections import Counter,deque



def estimateDOA(arraydata):
    

    LED_array[0:35]= 'black'
    LED_pointer
    ### initialize arrays
    mic1[0:35] = 'black'
    mic1[14:16] = 'pink'
    mic2[0:35] = 'black'
    mic2[18:20] = 'pink'
    mic3[0:35] = 'black'
    mic3[22:24] = 'pink'
    mic4[0:35] = 'black'
    mic4[26:28] = 'pink'
    mic5[0:35] = 'black'
    mic5[31:33] = 'pink'
    mic6[0:35] = 'black'
    mic6[2:4] = 'pink'
    mic7[0:35] = 'black'
    mic7[6:8] = 'pink'
    mic8[0:35] = 'black'
    mic8[10:12] = 'pink'

    peakvalues = []

    for i in range(len(arraydata)):
        largest_data=max(arraydata[1],key=abs)
        print(largest_data) #debug
        if abs(largest_data) > 2000: #this value can be changed depending on sensitivity
            ind = arraydata[1].index(largest_data) #add the index of loudest mic into peakvalues
            peakvalues.append(ind)

    try:
        loudest_mic = Counter(peakvalues).most_common(1)
        print("loudest mic index") #debug
        print(loudest_mic) #debug
    except:
        print("no loudest mic")
        loudest_mic = None

    ###get the led array of the corresponding mics

    if loudest_mic == 0:
        LED_pointer = mic1
        led.set(LED_array)
        led.set(LED_pointer)

    elif loudest_mic == 1:
        LED_pointer = mic2
        led.set(LED_array)
        led.set(LED_pointer)

    elif loudest_mic == 2:
        LED_pointer = mic3
        led.set(LED_array)
        led.set(LED_pointer)

    elif loudest_mic == 3:
        LED_pointer = mic4
        led.set(LED_array)
        led.set(LED_pointer)

    elif loudest_mic == 4:
        LED_pointer = mic5
        led.set(LED_array)
        led.set(LED_pointer)

    elif loudest_mic == 5:
        LED_pointer = mic6
        led.set(LED_array)
        led.set(LED_pointer)

    elif loudest_mic == 6:
        LED_pointer = mic7
        led.set(LED_array)
        led.set(LED_pointer)

    elif loudest_mic == 7:
        LED_pointer = mic8
        led.set(LED_array)
        led.set(LED_pointer)
    else:
        continue


    # reset the LED and activate the corresponding lights
    
    
    
    


    return loudest_mic
