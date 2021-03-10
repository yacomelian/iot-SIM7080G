
import time

try:
    import numpy as np
    import serial.tools.list_ports
except:
    pass

class Lidar2d:
    
    ser = None
    port = '/dev/ttyS0'
    bps= 115200 
    
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.flushInput()
    def is_open():
        return self.ser.is_open()
    
    def open (self):
        self.ser.open(self)

    def close (self):
        self.ser.close()

    def getTFminiData(self):
        while True:
            count = self.ser.in_waiting
            if count > 8:
                recv = self.ser.read(9)
                self.ser.reset_input_buffer()
                if recv[0] == 0x59 and recv[1] == 0x59:  # python3
                    distance = np.int16(recv[2] + np.int16(recv[3] << 8))
                    strength = recv[4] + recv[5] * 256
                    meters = distance / 100
        #            print('distance = %5d  strengh = %5d' % (distance, strength))
                    print('meters = %5d  distance = %5d  strengh = %5d' % (meters, distance, strength))
                    self.ser.reset_input_buffer()

                if recv[0] == 'Y' and recv[1] == 'Y':  # python2
                    lowD = int(recv[2].encode('hex'), 16)
                    highD = int(recv[3].encode('hex'), 16)
                    lowS = int(recv[4].encode('hex'), 16)
                    highS = int(recv[5].encode('hex'), 16)
                    distance = np.int16(lowD + np.int16(highD << 8))
                    strength = lowS + highS * 256
                    print('distance = %5d  strengh = %5d' % (distance, strength))
            else:
                time.sleep(0.005) #50ms

                
if __name__ == '__main__':
    ser = Lidar2d()
    try:
        if ser.is_open == False:
            try:
                ser.open()
            except:
                print('Open COM failed!')
        ser.getTFminiData()
    except KeyboardInterrupt:  # Ctrl+C
        if ser != None:
            ser.close()
