#!/usr/bin/python

import Adafruit_CharLCD as LCD
from time import sleep
from subprocess import call

from timelapse import TimelapseStep, Timelapse


class SubMenuEntry:

    title = ""
    values = list()
    switchPos = 0

    def __init__(self, title, values = None, confirmationMsg = None):

        self.title = title
        if (values != None):
            self.values = values

    def cycleValuesRight(self):
        self.switchPos = (self.switchPos + 1) % len(self.values)

    def getCurrentValue(self):
        if (len(self.values) > 0):
            return self.values[self.switchPos]
        else:
            return ""

    def action(self, menu = None):
        #overwrite me in inherited classes
        return True



class TopMenuEntry:

    title = ""
    subEntries = list()

    def __init__(self, title, subEntries):
        self.title = title
        self.subEntries = subEntries



class Menu:

    xpos = 0
    ypos = 0
    posOnTop = True

    xels = list()
    lcd = LCD.Adafruit_CharLCDPlate()
    moveSpeed = 0.03
    somethingChanged = True
    sleepTimer = 0
    maxSleepTimer = 100
    lcd_is_on = True

    def __init__(self, xels):
        self.xels = xels

    def nextTopElement(self):
        self.xpos = (self.xpos + 1) % len(self.xels)
        self.ypos = 0

    def prevTopElement(self):
        self.xpos = self.xpos - 1
        if (self.xpos < 0):
            self.xpos = len(self.xels) - 1
        self.ypos = 0

    def nextSubEntry(self):
        self.ypos = (self.ypos + 1) % len(self.xels[self.xpos].subEntries)

    def prevSubEntry(self):
        self.ypos = self.ypos - 1
        if (self.ypos < 0):
            self.ypos = len(self.xels[self.xpos].subEntries) - 1

    def clearMenuLeft(self):
        i = 0
        while (i < 16):
            self.lcd.move_right()
            sleep(self.moveSpeed)
            i = i + 1

    def clearMenuRight(self):
        i = 0
        while (i < 16):
            self.lcd.move_left()
            sleep(self.moveSpeed)
            i = i + 1

    # returns false, when key press should be ignored, because it just woke up the display
    def button_was_pressed(self):
        self.sleepTimer = 0
        self.somethingChanged = True
        if (self.lcd_is_on == False):
            self.lcd.set_backlight(1.0)
            self.lcd.enable_display(True)
            self.lcd_is_on = True
            return False
        return True
        
    def turn_display_off(self):
        self.lcd.set_backlight(0.0)
        self.lcd.enable_display(False)
        self.lcd_is_on = False

    def confirmation(self, msg):
        self.button_was_pressed()
        self.lcd.message(msg)

    def startMenu(self):
        try:
            while (True):
                # check for keypresses
                if (self.lcd.is_pressed(LCD.LEFT)):
                    if (self.button_was_pressed()):
                        if (self.posOnTop == True):
                            self.prevTopElement()
                            self.clearMenuLeft()
                        else:
                            self.posOnTop = True
                            self.ypos = 0
                elif (self.lcd.is_pressed(LCD.RIGHT)):
                    if (self.button_was_pressed()):
                        if (self.posOnTop == True):
                            self.nextTopElement()
                            self.clearMenuRight()
                        else:
                            if (len(self.xels[self.xpos].subEntries[self.ypos].values) > 0):
                                self.xels[self.xpos].subEntries[self.ypos].cycleValuesRight()
                elif (self.lcd.is_pressed(LCD.UP)):
                    if (self.button_was_pressed()):
                        if (self.posOnTop):
                            self.posOnTop = False
                            self.prevSubEntry()
                        else:
                            self.prevSubEntry()
                elif (self.lcd.is_pressed(LCD.DOWN)):
                    if (self.button_was_pressed()):
                        if (self.posOnTop):
                            self.posOnTop = False
                        else:
                            self.nextSubEntry()
                elif (self.lcd.is_pressed(LCD.SELECT)):
                    if (self.button_was_pressed()):
                        self.xels[self.xpos].subEntries[self.ypos].action(self)

                # when a key was pressed, display the new value
                if (self.somethingChanged):
                    self.somethingChanged = False
                    self.lcd.clear()
                    if (self.posOnTop == True):
                        self.lcd.message(self.xels[self.xpos].title + "\n       v        ")
                    else:
                        self.lcd.message(self.xels[self.xpos].subEntries[self.ypos].title + "\n" + str(self.xels[self.xpos].subEntries[self.ypos].getCurrentValue()))
                    # sleep, because otherwise the keypresses cycle the values too fast
                    sleep(0.1)
                # sleep, just to save some cpu resources
                sleep(0.1)
                self.sleepTimer = self.sleepTimer + 1
                if (self.sleepTimer > self.maxSleepTimer):
                    self.turn_display_off()

        except KeyboardInterrupt:
            print("Aborting...")
        self.turn_display_off()




angle = SubMenuEntry("Angle", [360, 315, 270, 225, 180, 135, 90, 45])
direction = SubMenuEntry("Direction", ["left", "right"])
duration = SubMenuEntry("Duration", [5, 10, 15, 30, 45, 60, 75, 90, 105, 120])
durationUnit = SubMenuEntry("Duration Unit", ["minutes", "seconds"])
smooth = SubMenuEntry("Smoothness", ["yes", "no"])

#global for easy passing to other menu entry
tl_steps = list()

class SME_AddStep(SubMenuEntry):
    def action(self, menu):
        global tl_steps

        tls = TimelapseStep(menu.xels[0].subEntries[0].getCurrentValue(), menu.xels[0].subEntries[1].getCurrentValue(), menu.xels[0].subEntries[2].getCurrentValue(), menu.xels[0].subEntries[3].getCurrentValue())
        tl_steps.append(tls)

addStep = SME_AddStep("Add Step")

class SME_ClearSteps(SubMenuEntry):
    def action(self, menu = None):
        global tl_steps
        del tl_steps[:]
        return True

clearSteps = SME_ClearSteps("Clear steps")


class SME_StartTL(SubMenuEntry):
    def action(self, menu):
        if (len(tl_steps) > 0):
            tl = Timelapse(tl_steps)
            tl.startTL(menu)
            tl.stop_motor()
            return True
        else:
            print("No step added")
        return False

tlStart = SME_StartTL("Start TL")


copy = SubMenuEntry("Copy")
abort = SubMenuEntry("Abort")

class SME_PowerOff(SubMenuEntry):
    def action(self, menu = None):
        menu.turn_display_off()
        call(['sudo', 'poweroff'])
        # not that it matters
        return True

poweroff = SME_PowerOff("Power OFF, RLY")

tl = TopMenuEntry("Timelapse", [angle, direction, duration, durationUnit, smooth, addStep, clearSteps, tlStart])
hdCopy = TopMenuEntry("HD Copy", [copy, abort])
poweroff = TopMenuEntry("Power OFF", [poweroff])


menu = Menu([tl, hdCopy, poweroff])
menu.startMenu()

