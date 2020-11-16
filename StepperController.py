import threading #For parallel tasks.
import time #Timers inside of threads.

import digitalio

#RaspberryPi pin definitions:
#Enable_pin = digitalio.DigitalInOut(board.D18)
#Coil_A_1_pin = digitalio.DigitalInOut(board.D4)
#Coil_A_2_pin = digitalio.DigitalInOut(board.D17)
#Coil_B_1_pin = digitalio.DigitalInOut(board.D23)
#Coil_B_2_pin = digitalio.DigitalInOut(board.D24)

class StepperMotor():
    #Stepper Delay (s):
    step_delay = 0.01

    #Stepper Step count:
    step_count = 0

    step_target = 0

    #Target tracking thread:
    MoveThread = threading.Thread

    def __init__(self, enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin, stepsPerTurn=512):
        self.enable_pin = digitalio.DigitalInOut(enable_pin)
        self.coil_A_1_pin = digitalio.DigitalInOut(coil_A_1_pin)
        self.coil_A_2_pin = digitalio.DigitalInOut(coil_A_2_pin)
        self.coil_B_1_pin = digitalio.DigitalInOut(coil_B_1_pin)
        self.coil_B_2_pin = digitalio.DigitalInOut(coil_B_2_pin)

        #Pin directions:
        self.enable_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_A_2_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_1_pin.direction = digitalio.Direction.OUTPUT
        self.coil_B_2_pin.direction = digitalio.Direction.OUTPUT

        #Stepper Revolution:
        self.step_revolution = stepsPerTurn

        self.MoveThread = threading.Thread(target=self.moveAsync)
        self.MoveThread.start()

    def setStep(self, w1, w2, w3, w4):
        self.coil_A_1_pin.value = w1
        self.coil_A_2_pin.value = w2
        self.coil_B_1_pin.value = w3
        self.coil_B_2_pin.value = w4

    def forward(self, steps):
        i = 0
        while i in range(0, steps):
            self.setStep(1, 1, 0, 0)
            time.sleep(self.step_delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(self.step_delay)
            self.setStep(0, 0, 1, 1)
            time.sleep(self.step_delay)
            self.setStep(1, 0, 0, 1)
            time.sleep(self.step_delay)
            self.step_count += 1
            i += 1

    def backwards(self, steps):
        i = 0
        while i in range(0, steps):
            self.setStep(0, 0, 1, 1)
            time.sleep(self.step_delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(self.step_delay)
            self.setStep(1, 1, 0, 0)
            time.sleep(self.step_delay)
            self.setStep(1, 0, 0, 1)
            time.sleep(self.step_delay)
            self.step_count -= 1
            i += 1

    def moveAsync(self):
        while True:
            if self.step_target > self.step_count:
                self.forward(self.step_target - self.step_count)
            elif self.step_target < self.step_count:
                self.backwards(self.step_count - self.step_target)

    def setAngle(self, angle):
        self.step_target = int(angle / 360 * self.step_revolution)

    def enable(self):
        self.enable_pin.value = True
        self.MoveThread.start()

    def disable(self):
        self.enable_pin.value = False
        self.MoveThread.stop()