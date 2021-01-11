import threading #For parallel tasks.
import time #Timers inside of threads.
import gpsd #Gps driver utility.
import math #Math package
import socket
import struct
from datetime import datetime
#import board
#from StepperController import StepperMotor
from GpsConnectionHandler import GpsConnectionHandler

class AntennaGps():
    def __init__(self, host = "127.0.0.1", port = "2947"):
        self.host = host
        self.port = port

    def connect(self):
        gpsd.connect() #Find the gps device.

    def getPosition(self):
        return gpsd.get_current().position()

class RoverGps():
    def __init__(self, host = "10.42.0.30", port = "65432"):
        self.host = host
        self.port = port

    def connect(self):
        self.bufSize = 1024
        self.sock = socket.socket(socket.AF_INET, # Internet
                                    socket.SOCK_DGRAM) # UDP
        self.sock.bind((self.host, self.port))
        print("Rover GPS connected")

    def getPosition(self):
        data, addr = self.sock.recvfrom(self.bufSize)
        msg = struct.unpack("2f", data)
        if msg[0] == 999 or msg[1] == 999:
            raise gpsd.NoFixError("Needs at least 2D fix")
        return msg

class AntennaStation():
    def __init__(self):
        self.antennaGps = AntennaGps()
        self.roverGps = RoverGps()
        #self.motor = StepperMotor(board.D18, board.D4, board.D17, board.D23, board.D24, 512)
        #self.motor.enable

    def loop(self):
        print("[Task] Connecting antenna GPS...")
        self.connect(self.antennaGps)

        print("[Task] Connecting rover GPS...")
        self.connect(self.roverGps)

        while True:
            try:
                antennaPosition = self.antennaGps.getPosition()
            except (socket.error, UserWarning):
                print("[Error] Antenna GPS: Connection lost")
                print("[Task] Reconnecting...")
                self.connect(self.antennaGps)
                print("[Success] Connected antenna GPS")
                continue
            except gpsd.NoFixError:
                print("[Error] Antenna GPS: NoFixError", end="\r")
                continue
            
            try:
                roverPosition = self.roverGps.getPosition()
            except socket.error:
                print("[Error] Rover GPS: Connection lost")
                print("[Task] Reconnecting...")
                self.connect(self.roverGps)
                print("[Success] Connected rover GPS")
                continue
            except gpsd.NoFixError:
                print("[Error] Rover GPS: NoFixError", end="\r")
                continue

            bearing = getBearing(antennaPosition, roverPosition)
            #self.motor.setAngle(bearing)
            time.sleep(1)
            print("[Status] Ok", end="\r")
    
    def connect(self, gps):
        i = 0
        while True:              
            try:
                gps.connect()
                break
            except:
                i += 1
                time.sleep(1)
                print("[Error] Connection failed, retrying... %d" % i, end="\r")
                continue

#source https://gist.github.com/jeromer/2005586
def getBearing(pointA, pointB):
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

def savePosition(pos):
    logging = open("logs","a")
    (x, y) = pos
    logging.write(datetime.now().strftime("%H-%M-%S")+":" + str(x)+":"+str(y)+"\n")
    logging.close()

if __name__ == "__main__":
    antennaStation = AntennaStation()
    antennaStation.loop()