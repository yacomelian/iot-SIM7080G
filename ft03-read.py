#!/usr/bin/env python3

import serial.tools.list_ports
import time
import numpy as np

ser = serial.Serial()
ser.port = '/dev/ttyS0'
ser.baudrate = 115200

def getTFminiData():
   while True:
      count = ser.in_waiting
      if count > 8:
         recv = ser.read(9)
         ser.reset_input_buffer()
         if recv[0] == 0x59 and recv[1] == 0x59:  # python3 
            distance = np.int16(recv[2] + np.int16(recv[3] << 8))
            strength = recv[4] + recv[5] * 256
            meter = distance / 100
            print(' meter = %5d distance = %5d  strengh = %5d' % (meter, distance, strength))
            ser.reset_input_buffer()

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
   try:
      if ser.is_open == False:
         try:
            ser.open()
         except:
            print('Open COM failed!')
      getTFminiData()
   except KeyboardInterrupt:  # Ctrl+C
      if ser != None:
         ser.close()