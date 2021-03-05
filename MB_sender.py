import time

from microbit import *
import radio

device_uid = "MB1"

radio.config(group=132, queue=1)
radio.on()

while True:   
    display.scroll(device_uid)

    radio.send(device_uid)
    time.sleep(0.5)
