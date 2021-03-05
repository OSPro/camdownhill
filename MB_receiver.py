from microbit import *

import radio

radio.config(group=132, queue=1)
radio.on()


while True:
    result = radio.receive_full()

    if result != None:
        if int(result[1]) >= -51:
            display.scroll(result[0])
            print(result[0])
