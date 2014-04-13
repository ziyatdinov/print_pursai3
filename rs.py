import serial
import threading
from Queue import Queue, Empty as QueueEmpty

class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting\n"
        prin = printer()
        prin.reader()
        print "Exiting\n"

class printer:
    def __init__(self):
        self.port  = "/dev/ttyACM0"
        self.baudrate = 115200
        self.echo = 1
        self.rtscts = 0
        self.xonxoff = 0
        self.repr_mode = 0
        self.priqueue = Queue(0)
        
        try:
            self.s = serial.Serial(self.port, self.baudrate, rtscts=self.rtscts, xonxoff=self.xonxoff)
            print("Could open port\n")
        except:
            print("Could not open port\n")

    def reader(self):
        print('reader')
        while 1:
            data = self.s.readline()
            print(data)

    def writer(self,data):
        self.s.write(data)
        print(data)




