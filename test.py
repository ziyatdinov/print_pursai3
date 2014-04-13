#!/usr/bin/env python

#(C)2002-2003 Chris Liechti <cliechti@gmx.net>
#redirect data from a TCP/IP connection to a serial port and vice versa
#requires Python 2.2 'cause socket.sendall is used

import sys, os, serial, threading, getopt, socket

try:
    True
except NameError:
    True = 1
    False = 0

class Redirector:
    def __init__(self, serial, socket):
        self.serial = serial
        self.socket = socket

    def shortcut(self):
        """connect the serial port to the tcp port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(1)
        self.thread_read.start()
        self.writer()
    
    def reader(self):
        """loop forever and copy serial->socket"""
        while self.alive:
            try:
                data = self.serial.read(1)              #read one, blocking
                n = self.serial.inWaiting()             #look if there is more
                if n:
                    data = data + self.serial.read(n)   #and get as much as possible
                if data:
                    self.socket.sendall(data)           #send it over TCP
            except socket.error, msg:
                print msg
                #probably got disconnected
                break
        self.alive = False
    
    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.serial.write(data)                 #get a bunch of bytes and send them
            except socket.error, msg:
                print msg
                #probably got disconnected
                break
        self.alive = False
        self.thread_read.join()

    def stop(self):
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()

if __name__ == '__main__':
    ser = serial.Serial()
    
    #parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                "hp:b:rxP",
                ["help", "port=", "baud=", "rtscts", "xonxoff", "localport="])
    except getopt.GetoptError:
        # print help information and exit:
        print >>sys.stderr, __doc__
        sys.exit(2)
    
    ser.port    = '/dev/ttyACM0'
    ser.baudrate = 115200
    ser.rtscts  = False
    ser.xonxoff = False
    ser.timeout = 1     #required so that the reader thread can exit
    
    localport = 9090
    for o, a in opts:
        if o in ("-h", "--help"):   #help text
            usage()
            sys.exit()
        elif o in ("-p", "--port"):   #specified port
            try:
                ser.port = int(a)
            except ValueError:
                ser.port = a
        elif o in ("-b", "--baud"):   #specified baudrate
            try:
                ser.baudrate = int(a)
            except ValueError:
                raise ValueError, "Baudrate must be a integer number"
        elif o in ("-r", "--rtscts"):
            ser.rtscts = True
        elif o in ("-x", "--xonxoff"):
            ser.xonxoff = True
        elif o in ("-P", "--localport"):
            try:
                localport = int(a)
            except ValueError:
                raise ValueError, "Local port must be an integer number"

    print "--- TCP/IP to Serial redirector --- type Ctrl-C / BREAK to quit"

    try:
        ser.open()
        ser
    except serial.SerialException, e:
        print "Could not open serial port %s: %s" % (ser.portstr, e)
        sys.exit(1)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind( ('', localport) )
    srv.listen(1)
    while 1:
        try:
            print "Waiting for connection..."
            connection, addr = srv.accept()
            print 'Connected by', addr
            #enter console->serial loop
            r = Redirector(ser, connection)
            r.shortcut()
            print 'Disconnected'
            connection.close()
        except socket.error, msg:
            print msg

    print "\n--- exit ---"