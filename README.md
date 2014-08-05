# Ammonia RPi

Indirect measurement of ammonia concentration.

## Setup RPi serial port

### Disable Serial Port Login

To enable the serial port for your own use you need to disable login on the port. There are two files that need to be edited. The first and main one is `/etc/inittab`. This file has the command to enable the login prompt and this needs to be disabled. Edit the file and scroll down to the end. You will see a line similar to:

```
T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100
```

Disable it by adding a `#` character to the beginning.

### Reboot

In order to enable the changes you have made, you will need to reboot the Raspberry Pi:

```
sudo shutdown -r now
```

### References

 * https://www.atlas-scientific.com/_files/code/pi_sample_code.pdf

## Setup RPi for I2C

### Enable the hardware I2C driver

Edit `/etc/modules` and add:

```
i2c-bcm2708
i2c-dev
```

to the end of the file. Then save and reboot to enable the driver.

### Add SMBus support (which includes I2C) to Python

Run:

```
sudo apt-get install python-smbus, i2c-tools
```

`i2c-tools` isn't strictly required, but it's a useful package since you can use it to scan for any I2C or SMBus devices connected to your board. If you know something is connected, but you don't know it's 7-bit I2C address, this library has a great little tool to help you find it:

```
sudo i2cdetect -y 1
```

This will search `/dev/i2c-1` for all address, and if an Adafruit LCD Plate is connected, it should show up at 0x20.

Once both of these packages have been installed, you have everything you need to get started accessing I2C and SMBus devices in Python.

### Install LCD Pi Plate Python library

The LCD Pi Plate Python code for Pi is available on Github at: https://github.com/adafruit/Adafruit_Python_CharLCD

The easiest way to get the code onto your Pi is to hook up an Ethernet cable, and clone it directly using `git`, which is installed by default on most distros. Simply run the following commands from your home directory:

```
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus python-pip git
sudo pip install RPi.GPIO
git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
cd Adafruit_Python_CharLCD
sudo python setup.py install
```

References

 * https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/usage
