#!/usr/bin/python

import time
import math
import RPi.GPIO as GPIO

class TimelapseStep:

    angle = 0
    direction = ""
    duration = 0
    timePerStep = 0.0
    motorSteps = 512
    steps = 0
    tps = list()

    def __init__(self, angle, direction, duration, durationUnit):
        self.angle = angle
        self.direction = direction
        self.duration = duration
        self.steps = int(self.motorSteps / 360.0 * angle)
        self.timePerStep = duration / self.steps / 8
        if (durationUnit == "minutes"):
            self.timePerStep = self.timePerStep * 60
        self.tps = [self.timePerStep] * self.steps
        print(angle, direction, duration, durationUnit, self.timePerStep)


class Timelapse:

    tlSteps = list()
    # Pins
    #A = 7
    #B = 11
    #C = 13
    #D = 15
    # needs to be the BCM name, cause Adafruit Library set the mode
    A = 4
    B = 17
    C = 27
    D = 22


    def __init__(self, tlSteps):
        self.tlSteps = tlSteps

        # is already set in the Adafruit Library to BCM
        #GPIO.setmode(GPIO.BOARD)
        #GPIO.setwarnings(False)

        GPIO.setup(self.A, GPIO.OUT)
        GPIO.setup(self.B, GPIO.OUT)
        GPIO.setup(self.C, GPIO.OUT)
        GPIO.setup(self.D, GPIO.OUT)


    def GPIO_SETUP(self, a, b, c, d, t):
        GPIO.output(self.A, a)
        GPIO.output(self.B, b)
        GPIO.output(self.C, c)
        GPIO.output(self.D, d)
        time.sleep(t)

    def turn_left(self, timePerStep):
        self.GPIO_SETUP(0,0,0,0,0)
        for x in timePerStep:
            self.GPIO_SETUP(1,0,0,0, x)
            self.GPIO_SETUP(1,1,0,0, x)
            self.GPIO_SETUP(0,1,0,0, x)
            self.GPIO_SETUP(0,1,1,0, x)
            self.GPIO_SETUP(0,0,1,0, x)
            self.GPIO_SETUP(0,0,1,1, x)
            self.GPIO_SETUP(0,0,0,1, x)
            self.GPIO_SETUP(1,0,0,1, x)

    def turn_right(self, timePerStep):
        self.GPIO_SETUP(0,0,0,0,0)
        for x in timePerStep:
            self.GPIO_SETUP(1,0,0,1, x)
            self.GPIO_SETUP(0,0,0,1, x)
            self.GPIO_SETUP(0,0,1,1, x)
            self.GPIO_SETUP(0,0,1,0, x)
            self.GPIO_SETUP(0,1,1,0, x)
            self.GPIO_SETUP(0,1,0,0, x)
            self.GPIO_SETUP(1,1,0,0, x)
            self.GPIO_SETUP(1,0,0,0, x)

    def stop_motor(self):
        self.GPIO_SETUP(0,0,0,0,0)

    def startTL(self, menu):
        menu.turn_display_off()
        try:
            if (menu.xels[0].subEntries[4].getCurrentValue() == "yes"): #jetz wird's wild. Refactoring!
                for i in range(1, len(self.tlSteps)):
                    #for readability
                    cs = self.tlSteps[i-1]
                    ns = self.tlSteps[i]
                    if (cs.timePerStep != ns.timePerStep and cs.direction == ns.direction):
                        if (cs.timePerStep < ns.timePerStep):
                            for x in range(int(cs.steps * 0.75), cs.steps):
                                cs.tps[x] = cs.tps[x-1] + (ns.timePerStep - cs.timePerStep) / ((cs.steps * 0.25) + (ns.steps * 0.25))
                            for x in range(int(ns.steps * 0.25) + 1, 0, -1):
                                ns.tps[x] = ns.tps[x+1] - (ns.timePerStep - cs.timePerStep) / ((cs.steps * 0.25) + (ns.steps * 0.25))
                        else:
                            for x in range(int(cs.steps * 0.75), cs.steps):
                                cs.tps[x] = cs.tps[x-1] - (cs.timePerStep - ns.timePerStep) / ((cs.steps * 0.25) + (ns.steps * 0.25))
                            for x in range(int(ns.steps * 0.25) + 1, 0, -1):
                                ns.tps[x] = ns.tps[x+1] + (cs.timePerStep - ns.timePerStep) / ((cs.steps * 0.25) + (ns.steps * 0.25))
    
                    elif (self.tlSteps[i].direction != self.tlSteps[i-1].direction):
                        for x in range(int(cs.steps * 0.75), cs.steps):
                            cs.tps[x] = cs.timePerStep + (x - int(cs.steps * 0.75)) * cs.timePerStep / int(cs.steps * 0.25)
                        for x in range(int(ns.steps * 0.25)):
                            ns.tps[x] = ns.timePerStep + (x+1) * ns.timePerStep / int(ns.steps * 0.25)


            for tlStep in self.tlSteps:

                if (tlStep.direction == "left"):
                    self.turn_left(tlStep.tps)
                elif (tlStep.direction == "right"):
                    self.turn_right(tlStep.tps)
                self.stop_motor()
                
        except KeyboardInterrupt:
            print("\nAborting timelapse. Menu still running.")
            self.stop_motor()
        else:
            self.stop_motor()
        menu.button_was_pressed()


