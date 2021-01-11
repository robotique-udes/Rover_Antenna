import time

class IGps():
    def __init__(self, host = "127.0.0.1", port = "2947", label = ""):
        self.host = host
        self.port = port
        self.label = label

    def connect(self):
        pass

    def getPosition(self):
        pass

class IGpsState():
    def __init__(self, IGps : IGps, context, verbose=True):
        self.gps = IGps
        self.verbose = verbose
        self.context = context

    def setVerbose(self, verbose):
        self.verbose = verbose

    def run(self):
        pass
        
class DownState(IGpsState):
    def run(self):
        if self.verbose:
            print("[Status] GPS: %s Disconnected" % self.gps.label)
        self.context.setState(AttemptingState(self.gps, self.context, self.verbose))

class ConnectedState(IGpsState):
    def run(self):
        try:
            return self.gps.getPosition()
        except:
            self.context.setState(DownState(self.gps, self.context, self.verbose))

class AttemptingState(IGpsState):
    def __init__(self, IGps : IGps, context, verbose=True):
        IGpsState.__init__(self, IGps, context, verbose)
        self.counter = 0

    def run(self):
        try:
            self.gps.connect()
            self.context.setState(ConnectedState(self.gps, self.context, self.verbose))
            print("[Status] GPS: %s Connected" % self.gps.label)
        except:
            self.counter += 1
            time.sleep(1)
            print("[Status] GPS: %s Connection attempt [%d]" % (self.gps.label, self.counter), end="\r")

class InitState(IGpsState):
    def run(self):
        try:
            self.gps.connect()
            self.context.setState(ConnectedState(self.gps, self.context, self.verbose))
        except:
            self.context.setState(AttemptingState(self.gps, self.context, self.verbose))

class GpsConnectionHandler():
    def __init__(self, IGps, verbose=True):
        self.gps = IGps
        self.state = InitState(IGps, self, verbose)
        self.state.run()

    def setState(self, newState):
        self.state = newState

    def getPosition(self):
        return self.state.run()