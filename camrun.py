# TODO:
#   make something to transmit unique IDs from the MBs
#   activate real code in __main__ then

'''
Changes 2020 03 02 as per Odni specs
by Javi Montero
1. Change the logic order
    1- Play music
    2- Get timestamp with microseconds
    3- Take photo on rpi6
    4- Upload to aws
    5- Wait 1''
    6- Take video on rpi7
    7- Upload video on rpi7
    9- Upload photo to aws 

2. Change the filenames to include timestamp to prevent overwritting
3. Change the filenames to include uuid and the Raspi origin (rpi6, rpi7)
    Example filename: rpi6-userID-timestamp.jpg
    rpi6-user1-20200302-100507906574.jpg
    Associated timestamp filename: rpi6-user1-20200302-100507906574_timestamp.txt
    Content of associated timestamp file: 2020-03-02 10:05:07:906574
 '''

 
import datetime, serial, socket, subprocess, time

import pygame
pygame.mixer.init()

from picamera import PiCamera

DELAY = 1
TRIGGER_DELAY = 105

PORT = "/dev/ttyACM0"
BAUD = 115200

last_timestamp = datetime.datetime(1970, 1, 1)

def init_serial():
    print("Start serial connection")

    ser = serial.Serial(PORT)
    ser.baudrate = BAUD
    ser.parity   = serial.PARITY_NONE
    ser.databits = serial.EIGHTBITS
    ser.stopbits = serial.STOPBITS_ONE

    return ser


def get_rpi7_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0].rstrip("10") + "20"
    sock.close()

    return ip
  

def get_rpi_type():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0].split(".")[-1]
    sock.close()

    rpi_type = "6"
    if ip == "20":
        rpi_type = "7"

    print("RPi type: ", rpi_type)
    return rpi_type 


def process_user(camera, user_id):
    rpi_type = get_rpi_type()    

    if rpi_type == "6":


        rpi7_ip = get_rpi7_ip()
        time.sleep(3)

        # Play music
        pygame.mixer.music.load("/home/pi/camrun/welcome.mp3")
        pygame.mixer.music.play()

        # Take photo
        #time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_stamp = datetime.datetime.now()#.strftime("%Y-%m-%d %H:%M:%S:%f") # Microseconds
        camera.capture('/home/pi/camrun/rpi6.jpg')        
        
        
        # Upload to AWS
        firebase_upload(rpi_type, user_id, time_stamp, '/home/pi/camrun/rpi6.jpg')
        time.sleep(DELAY)

        # Take video on RPI7
        command = "ssh pi@" + rpi7_ip + " python3 /home/pi/camrun/take_video.py"
        # ssh pi@192.168.43.20 python3 /home/pi/camrun/take_video.py
        subprocess.call([command], shell=True)
        subprocess.call(['ssh pi@' + rpi7_ip + ' sudo rm /home/pi/camrun/rpi7.mp4'], shell=True)
        subprocess.call(['ssh pi@' + rpi7_ip + ' MP4Box -add /home/pi/camrun/rpi7.h264 -new /home/pi/camrun/rpi7.mp4'], shell=True)
        # ssh pi@192.168.43.20 MP4Box -add /home/pi/camrun/rpi7.h264 -new /home/pi/camrun/rpi7.mp4

        remote_filename = "rpi7-"+user_id+"-"+time_stamp.strftime("%Y%m%d-%H%M%S%f")+".mp4"

        subprocess.call(['ssh pi@' + rpi7_ip + ' "aws s3 cp /home/pi/camrun/rpi7.mp4 s3://user-runs/"' + user_id + '/' + remote_filename], shell=True)
        # ssh pi@192.168.43.20 "aws s3 cp /home/pi/camrun/rpi7.mp4 s3://user-runs/123456789/"


def firebase_upload(rpi_type, user_id, time_stamp, file):

    print("id, time, file: ", user_id, ' | ', time_stamp, ' | ', file)
    
    remote_filename = "rpi" + rpi_type + "-" + user_id + "-" + time_stamp.strftime("%Y%m%d-%H%M%S%f") + ".jpg"

    if time_stamp:
        time_stamp_file = file.replace('.jpg', '_timestamp.txt')
        with open(time_stamp_file, 'w') as f:
            f.write(time_stamp.strftime("%Y-%m-%d-%H:%M:%S:%f")) # User friendly timestamp

        remote_stamp_file = remote_filename[:-4] + '_timestamp.txt'
        command = "/usr/local/bin/aws s3 cp " + time_stamp_file +" s3://user-runs/" + user_id + '/' + remote_stamp_file
        subprocess.call([command], shell=True)

    command = "/usr/local/bin/aws s3 cp " + file +" s3://user-runs/" + user_id + '/' + remote_filename
    subprocess.call([command], shell=True)
    # DO I NEED TO DELETE FILES AFTER UPLOAD?


def wait_for_id(ser, camera):
    global last_timestamp
    while True:
        tmp = ser.readline()

        if tmp:
            # Check time difference
            current_timestamp = datetime.datetime.now()
            delta = current_timestamp - last_timestamp
            print("time diff is : ", delta.total_seconds())
            if (delta.total_seconds() > TRIGGER_DELAY):
                # Save new last_timestamp
                last_timestamp = current_timestamp
                
                # Get uid
                uid = ''
                # MB sender uid needs to have exactly 3 characters
                for c in tmp[-6:-3]:  
                    uid += chr(c)
                uid = uid.lstrip("x01")
                print("\n\nUSER ID: ", uid, "\n\n")
                
                # Take photo and video
                process_user(camera, uid)
                
                # Delay before checking new trigger
                time.sleep(0.1)
            else:
                # Save new last_timestamp
                last_timestamp = current_timestamp


if __name__ == "__main__":
    camera = PiCamera()
    #process_user(camera)  # TESTING!

    ser = init_serial()
    wait_for_id(ser, camera)
    ser.close()
    camera.close()
