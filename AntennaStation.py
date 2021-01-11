import threading #For parallel tasks.
import time #Timers inside of threads.
import math #Math package
import gpsd #Gps driver utility.
import socket
import json
import struct
from datetime import datetime
#import board
#from StepperController import StepperMotor
from GpsConnectionHandler import GpsConnectionHandler
from GpsConnectionHandler import IGps

class AntennaGps(IGps):
    def __init__(self, host = "127.0.0.1", port = "2947", label = "AntennaStation"):
        IGps.__init__(self, host, port, label)
        self.state = {}

    def _parse_state_packet(self, json_data):
        if json_data['class'] == 'DEVICES':
            if not json_data['devices']:
                raise Exception("No gps devices found")
            self.state['devices'] = json_data
        elif json_data['class'] == 'WATCH':
            self.state['watch'] = json_data
        else:
            raise Exception(
                "Unexpected message received from gps: {}".format(json_data['class']))

    def connect(self):
        self.gpsd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gpsd_socket.connect((self.host, self.port))
        self.gpsd_stream = self.gpsd_socket.makefile(mode="rw")
        welcome_raw = self.gpsd_stream.readline()
        welcome = json.loads(welcome_raw)
        if welcome['class'] != "VERSION":
            raise Exception(
                "Unexpected data received as welcome. Is the server a gpsd 3 server?")
        self.gpsd_stream.write('?WATCH={"enable":true}\n')
        self.gpsd_stream.flush()

        for i in range(0, 2):
            raw = self.gpsd_stream.readline()
            parsed = json.loads(raw)
            self._parse_state_packet(parsed)

    def getPosition(self):
        self.gpsd_stream.write("?POLL;\n")
        self.gpsd_stream.flush()
        raw = self.gpsd_stream.readline()
        response = json.loads(raw)
        if response['class'] != 'POLL':
            raise Exception(
                "Unexpected message received from gps: {}".format(response['class']))
        return gpsd.GpsResponse.from_json(response).position()

class RoverGps(IGps):
    def __init__(self, host = "10.42.0.30", port = "65432", label = "Rover"):
        IGps.__init__(self, host, port, label)

    def connect(self):
        self.bufSize = 1024
        self.sock = socket.socket(socket.AF_INET, # Internet
                                    socket.SOCK_DGRAM) # UDP
        self.sock.bind((self.host, self.port))

    def getPosition(self):
        data, addr = self.sock.recvfrom(self.bufSize)
        msg = struct.unpack("2f", data)
        if msg[0] == 999 or msg[1] == 999:
            raise gpsd.NoFixError("Needs at least 2D fix")
        return msg

class AntennaStation():
    def __init__(self):
        self.antennaGps = GpsConnectionHandler(AntennaGps())
        self.roverGps = GpsConnectionHandler(RoverGps())
        #self.motor = StepperMotor(board.D18, board.D4, board.D17, board.D23, board.D24, 512)
        #self.motor.enable()

    def loop(self):
        while True:
            antennaPosition = self.antennaGps.getPosition()
            roverPosition = self.roverGps.getPosition()
            if antennaPosition and roverPosition:
                bearing = getBearing(antennaPosition, roverPosition)
                #self.motor.setAngle(bearing)
                time.sleep(1)

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