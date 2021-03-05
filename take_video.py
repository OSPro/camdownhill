import time

from picamera import PiCamera

camera = PiCamera()

# what is the max resolution?
# camera.resolution = (2592, 1944)

LENGTH = 60


def take_video():    
    camera.start_recording('/home/pi/camrun/rpi7.h264')
    time.sleep(LENGTH)
    camera.stop_recording()


if __name__ == "__main__":
    take_video()
