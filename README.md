# PiTL

PiTL (Pi TimeLapse) is a stepper motor attached to a raspberry pi, controlled via Adafruit's 16x2 character LCD.

Features:

 * Top menu and sub menus
 * Automatic display switch off when idle
 * Definition of multiple steps for a timelapse
 * Each step has the following attributes (which can be easily adjustable)
  * Angle (45/90/135/180/225/270/315/360 degrees)
  * Direction (left/right)
  * Duration (5/10/15/30/45/60/75/90/105/120)
  * Duration unit (minutes/seconds)
 * Smooth transitions

##Setup

###Hardware parts:

A Raspberry Pi, of course, version 1/2/3, doesn't matter.

A [28BYJ48 DC 5V 4-Phase 5-Wire Arduino Stepper Motor with ULN2003 Driver Board](https://www.amazon.de/gp/product/B00ATA5MFE/ref=oh_aui_detailpage_o08_s00?ie=UTF8&psc=1)

The [LCD to control the motor](https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/overview?view=all#overview)

Optional (I used these parts to attach the camera to the motor):  

 * [A flexible coupling](https://www.amazon.de/gp/product/B01C6OXJBE/ref=oh_aui_detailpage_o07_s00?ie=UTF8&psc=1)

 * [A 1/4" to 1/4" screw](https://www.amazon.de/gp/product/B01A6EFCBQ/ref=oh_aui_detailpage_o08_s00?ie=UTF8&psc=1)


###Software parts:

First, [set up your Pi for I2C](http://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c).

Download and install [Adafruit's CharLCD library](https://github.com/adafruit/Adafruit_Python_CharLCD).

In your home directory clone this repository or download the files. 

Make the menu.py and timelapse.py executable:

    chmod u+x /home/pi/pitl/*.py

Put this in your crontab to start PiTL after reboot automatically:

    @reboot /home/pi/pitl/menu.py

## Usage

In the top menu (where each entry is displayed with a down arrow) the left and right buttons switch between the top menu entries, the up and down buttons cycle through the sub entries.

In the sub entries the right button changes values, the left button lets you return to the top menu.

When a sub entry has no values to change, the select button fires the specified action.

