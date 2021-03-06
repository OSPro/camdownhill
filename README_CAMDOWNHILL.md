# CamRun


## Installation

Install Raspbian on three SD cards and start each of the RPis.
Connect an active speaker to RPi6.

### Wifi

For this device, the three RPis need to be connected to the same wifi network.
Enter in the terminal of each RPi:

    sudo nano /etc/dhcpcd.conf

In the now open file, got to the bottom and add the following lines:

    interface wlan0
    static ip_address=X.Y.Z.10/24
    static routers=X.Y.Z.1
    static domain_name_servers=X.Y.Z.1 8.8.8.8 8.8.4.4

Here, X.Y.Z are the first three parts of the routers ip (find that ip by entering "ip addr"
in the terminal of a RPi connected to the wifi network and look for the section "wlan0").
IP has to be 10 for the RPi6, 20 for the second RPi7.
Press ctrl-x, then y to close the editor.

Enter in the terminal of each RPi:

    sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

Add at the end of the file:

    network={
        ssid="NAME"
        psk="PASSWORD"
        priority=1
    }

With NAME being the name of your wifi network and PASSWORD being the password.
Press ctrl-x, then y to close the editor.

Then enter in the terminal

    sudo reboot

### Update

Enter in the terminal of each RPi:

    sudo apt-get update && sudo apt-get upgrade -y

### Dependencies

Enter in the terminal of each RPi:

    sudo apt-get install gpac -y

### Camrun

Enter in the terminal of each RPi:

    cd /home/pi
    git clone https://github.com/OSPro/camdownhill.git

### SSH and camera

Enter in the terminal of each RPi:

    sudo raspi-config

Go to Interfaces -> SSH, enable SSH, go to Interfaces -> Camera and enable the camera. 
Now, close raspi-config and reboot.then reboot.

### Database

[DON'T DO THIS!]
This required creating an AWS user before like shown in

    https://aws.amazon.com/getting-started/tutorials/backup-to-s3-cli/

[/DON'T DO THIS!]

Enter in the terminal of each RPi:
	# Request root permission
	sudo su 
	# Enter raspberry as password if asked
    pip3 install awscli
	# Configure AWS
    aws configure

Enter
    
	AKIAJOVO2X3UICHURSLQ

and press enter. Enter

	MgD7s8okAy4gAF4zJ1kDup4XIiD6pmdXNXoe/4HW

and press enter. Enter

     us-east-1

and press enter. Enter

    json

end press enter.

[DON'T DO THIS!]
Create a new AWS bucket:

    aws s3 mb s3://user-runs

Upload file

    aws s3 cp /home/pi/camrun/FILENAME s3://user-runs/

Delete file

    aws s3 rm s3://user-runs/FILENAME

[/DON'T DO THIS!]

### Exchange ssh key

On the RPi6, enter in the terminal
	# Request root permission
    sudo su
	# Generate SSH key pair
	ssh-keygen

Confirm all questions with enter. Then, enter in the terminal

    ssh-copy-id pi@X.Y.Z.20

with the X.Y.Z being the same as above and "raspberry" as the password when asked.

### Autostart

Do this for RPi6.

On the RPi6, enter in the terminal
	# Request root permission
    sudo su
	# Enter Crontab Editor
    crontab -e

Select the editor you are familiar to (i.e. nano)

Go to the bottom of file and add the following lines at the end of file:

	@reboot /home/pi/camrun/start.sh >> /home/pi/camrun/log.txt 2>&1  &

Press ctrl-o to save, then ctrl-x to close the editor

## Configuration

### Delay to take video

To configure the trigger delay with the RPi6,
open the file camrun.py on the RPi6 with

    nano /home/pi/camrun/camrun.py

and change the line

    TRIGGER_DELAY = 105

to the desired trigger delay.

### Access AWS data

Open this URL:

    https://console.aws.amazon.com/s3/home?region=us-east-2

Use this username and passowrd:

    akggohigh2020@gmail.com
	Yanaitw2wcCaaba1

(or search for s3 in https://console.aws.amazon.com/)
