import threading #For parallel tasks.
import time #Timers inside of threads.
import gpsd #Gps driver utility. gps-device acronym.
import math #Math package
from datetime import datetime
import board
from StepperController import StepperMotor

#(latitude, longitude)
roverPosition = (45.386922, -71.993060)

#Configure a stepper motor.
Motor = StepperMotor(board.D18, board.D4, board.D17, board.D23, board.D24, 512)
Motor.enable

#It Just Works!
#sauce https://gist.github.com/jeromer/2005586
def getAngle(pointA, pointB):
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def readgps(): #Defines a method to pool the gpsd driver.
    while True: #Loop forever. (4)
        #The gpsd driver throws an exception if it cannot acquire gps data
        #We enclose it in a "try: except:" statement to catch the exception.
        try:
            packet = gpsd.get_current()
            angle = getAngle(packet.position(), roverPosition)
            Motor.setAngle(angle)
            
            print(str(angle))
        #The exception thrown by gpsd is a gpsd.NotFixError
        except gpsd.NoFixError:
            print("Cannot aquire gps data... retrying")
            time.sleep(5) #Wait longer to give the gps time to find data
        
        time.sleep(5) #Loop timer (seconds)

def writeToLogs(pos):
    logging = open("logs","a")
    (x, y) = pos
    logging.write(datetime.now().strftime("%H-%M-%S")+":" + str(x)+":"+str(y)+"\n")
    logging.close()

#Execution starts here. (1)
gpsd.connect() #Find the gps device. (2)

#Puts the gps pooling method in a thread so it runs in parallel. (3)
readgpsThread = threading.Thread(target=readgps)
readgpsThread.start()