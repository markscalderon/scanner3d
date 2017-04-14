import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from .gui.mainwindow_ui import Ui_MainWindow

import plotter

import socket
import threading
import fcntl
import struct
import time


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.processingButton.clicked.connect(self.Calculate)
        self.socket_init()
        self.cycle = True #cycle of thread recv_message
        self.ip = self.get_ip_address('wlan0')
        self.ip_line.setText(self.ip)

    def __del__(self):
        print "close all"
        self.s.close()
        self.cycle = False
        self.th.stop()

    def gestalt_init(self):
        ##gestaltInterface init function
        self.stages = virtualMachine(persistenceFile = "test.vmp")
        self.stages.xAxisNode.setVelocityRequest(1)
        self.stages.yAxisNode.setVelocityRequest(8)
        print "geslts have just initialized"

    #function to define the movements of gestalts
    def gestalt_define_mov(self):

        # Disk
        self.dangle=360.0/self.nshots
        self.movi=  range(0,361,dangle)
        self.movesx = []
        for i in self.movi:
            self.movesx.append([i])
        # Phone
        self.arcpoints=[[10],[20],[30],[40],[50],[60],[70],[80],[90],[100]]  # Empirical points selected on the arc
        self.dangle=360/self.nlevels
        self.movi=  range(0,361,self.dangle)
        self.movesy = []
        for i in self.movi:
            self.movesy.append([i])

    ##function to start the movements of robot
    def gestalt_mov_start(self):
        for my in self.movesy: # Phone
            self.stages.move(my,0)
            status = self.stages.xAxisNode.spinStatusRequest()
            # This checks to see if the move is done.
            while status['stepsRemaining'] > 0:
                time.sleep(0.001)
                status = self.stages.xAxisNode.spinStatusRequest()
            for mx in self.movesx: # Disk
                self.stages.move(mx,0)
                status = self.stages.yAxisNode.spinStatusRequest()
                # This checks to see if the move is done.
                while status['stepsRemaining'] > 0:
                    time.sleep(0.001)
                    status = self.stages.yAxisNode.spinStatusRequest()
                #here the scoket moments


    def socket_init(self):
        self.port = 44450
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ("<broadcast>", self.port)
        print >>sys.stderr, 'starting up on %s port %s' % self.server_address
        self.s.bind(('',self.port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

    def get_ip_address(self, ifname):

        return socket.inet_ntoa(fcntl.ioctl( self.s.fileno(),0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])

    def send_message(self, text):
        self.s.sendto(text, self.server_address)

    def recv_message(self):

        print >>sys.stderr, 'listen up on %s port %s' % self.server_address
        self.sock = self.s

        self.th = threading.Thread(target = self.recv_message_thread, args=(self.sock,self.server_address))
        self.th.start()

    def recv_message_thread(self, client, address):
        size = 1024
        print "RECV MSG FROM THREAD"
        try:
            while self.cycle:
                data = client.recv(size)
                if data:
                    print "recv from android: " + data
                else:
                    raise error('Client error')

                time.sleep(1)
        except KeyboardInterrupt:
            client.close()
            return False
        client.close()

    def Calculate(self):
        self.sessionT = self.sesion_line.text()
        self.nshots = self.shots.value()
        self.nlevels = self.levels.value()
        self.ntime = self.time.value()
        print self.sessionT
        print self.nshots
        print self.nlevels
        print self.ntime

        self.read_items()
        self.send_message(self.sessionT+","+self.ip)
        self.recv_message()



    def read_items(self):
        self.sesion_line.setReadOnly(True)
        self.shots.setReadOnly(True)
        self.levels.setReadOnly(True)
        self.time.setReadOnly(True)

    def write_items(self):
        self.sesion_line.setReadOnly(False)
        self.shots.setReadOnly(False)
        self.levels.setReadOnly(False)
        self.time.setReadOnly(False)



def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
