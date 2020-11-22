#!/usr/bin/python3

import functools
import logging
import RPi.GPIO as GPIO
import time
import serial


class simcom:

    powerKey = 4
    rec_buff = ''
    Message = 'www.waveshare.com'
    mqtt_url = 'broker.emqx.io'
    mqtt_port = 1883
    serial_dev = '/dev/ttyS0'
    bps = 115200
    ser = ''
    cmdout = ''
    gps_status = 0
    ON = 1
    OFF = 0

    def __init__(self, data):
        self.ser = serial.Serial(self.serial_dev, self.bps)
        self.ser.flushInput()
        self.checkStart()
        
    def __del__(self):
        self.powerDown(self.powerKey)

    def powerOn(self, powerKey):
        logging.info('SIM7080X is starting')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(powerKey, GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(powerKey, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(powerKey, GPIO.LOW)
        time.sleep(5)
        self.ser.flushInput()

    def powerDown(self, powerKey = 4):
        logging.info('SIM7080X is stopping')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(powerKey, GPIO.OUT)
        GPIO.output(powerKey, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(powerKey, GPIO.LOW)
        time.sleep(5)
        logging.info('Good bye')

    def sendAt(self, command, back, timeout):
        rec_buff = ''
        self.ser.write((command+'\r\n').encode())
        time.sleep(timeout)
        if self.ser.inWaiting():
            time.sleep(timeout)
            rec_buff = self.ser.read(self.ser.inWaiting())
        if rec_buff != '':
            self.cmdout = rec_buff.decode()
            if back not in rec_buff.decode():
                logging.debug(command + ' back:\t' + rec_buff.decode())
                return 0
            else:
                logging.debug(rec_buff.decode())
                return 1
        else:
            logging.debug(command + ' no response')

    def checkStart(self):
        while True:
            # simcom module uart may be fool, so it is better
            # to send much times when it starts.
            self.ser.write('AT\r\n'.encode())
            time.sleep(1)
            self.ser.write('AT\r\n'.encode())
            time.sleep(1)
            self.ser.write('AT\r\n'.encode())
            time.sleep(1)
            if self.ser.inWaiting():
                time.sleep(0.01)
                recBuff = self.ser.read(self.ser.inWaiting())
                logging.info('SIM7080X is ready')
                logging.debug('try to start' + recBuff.decode())
                if 'OK' in recBuff.decode():
                    recBuff = ''
                    break
            else:
                self.powerOn(self.powerKey)
     
    def gpsGetStatus(self):
        return self.sendAt('AT+CGNSINF', '+CGNSINF: ', 1)

    """ 
    Set the status of gps Power. The function if defined between if 
    to avoid wrong parameters pases (invalid value of param status)
    param status can be 1 or 0 ( private consts defined ON or OFF)
    """
     
    def gpsPower(self, status):
        if status == self.ON:
            logging.debug('Start GPS session')
            self.gps_status = self.ON
        if status == self.OFF:
            logging.debug('Stop GPS session.')
            self.gps_status = self.OFF
        if (self.gps_status >= 0):
            self.sendAt('AT+CGNSPWR='+str(self.gps_status), 'OK', 0.1)
        
    def gpsPowerOn(self):
        self.gpsPower(self.ON)
        
    def gpsPowerOff(self):
        self.gpsPower(self.OFF)


    """ 
    OUTPUT>
    <GNSS run status>,<Fix status>,<UTC date & Time>,<Latitude>,
    <Longitude>,<MSL Altitude>,<Speed Over Ground>,<Course Over Ground>,
    <Fix Mode>,<Reserved1>,<HDOP>,<PDOP>,<VDOP>,<Reserved2>
    ,<GNSS Satellites in View>,<Reserved3>,<HPA>,<VPA>
    
    """
    def getGpsPosition(self):
        rec_null = True
        answer = 0
        rec_buff = ''
        if (self.gps_status == self.OFF):  # Si GPS no activo
            self.gpsPowerOn();
        while rec_null:
            answer = self.sendAt('AT+CGNSINF', '+CGNSINF: ', 1)
            if 1 == answer:
                logging.debug('Answer ok' + str(answer))
                answer = 0
                if ',,,,,,' in self.cmdout:
                    logging.debug('GPS is not ready')
                    rec_null = False
                    time.sleep(1)
                else:
                    logging.info('Posicion: ' + self.cmdout)
                    i=0
                    out = self.cmdout.splitlines()[2]
                    #for s in self.cmdout.splitlines():
                    #    i+=1
                    #    print(str(i) +": "+ s)
                    #print("[" + self.cmdout + "]")
                    #hex_val = self.toHex(self.cmdout)
                    #print(hex_val)
                    print(out)
            else:
                logging.info('error %s' % answer)
                rec_buff = ''
                return False
            time.sleep(1.5)

    def test_mqtt(self):
        try:
            self.checkStart()
            logging.info('wait for signal')
            time.sleep(10)
            self.sendAt('AT+CSQ', 'OK', 1)
            self.sendAt('AT+CPSI?', 'OK', 1)
            self.sendAt('AT+CGREG?', '+CGREG: 0, 1', 0.5)
            self.sendAt('AT+CNACT=0, 1', 'OK', 1)
            self.sendAt('AT+CACID=0',  'OK', 1)
            self.sendAt('AT+SMCONF=\"URL\", broker.emqx.io, 1883', 'OK', 1)
            self.sendAt(
                'AT+SMCONF=\"URL\", ' + self.mqtt_url + ', ' + self.mqtt_port,
                'OK', 1)
            self.sendAt('AT+SMCONF=\"KEEPTIME\", 60', 'OK', 1)
            self.sendAt('AT+SMCONN', 'OK', 5)
            self.sendAt('AT+SMSUB=\"waveshare_pub\", 1', 'OK', 1)
            self.sendAt('AT+SMPUB=\"waveshare_sub\", 17, 1, 0', 'OK', 1)
            self.ser.write(self.Message.encode())
            time.sleep(10)
            logging.info('send message successfully!')
            self.sendAt('AT+SMDISC', 'OK', 1)
            self.sendAt('AT+CNACT=0, 0',  'OK',  1)
            self.powerDown(self.powerKey)
        except Exception:
            if self.ser is not None:
                self.ser.close()
            self.powerDown(self.powerKey)
            GPIO.cleanup()

    def test_gps(self):
        try:
            self.checkStart()
            self.getGpsPosition()
            self.powerDown(self.powerKey)
        except Exception:
            if ser is not None:
                ser.close()
            self.powerDown(self.powerKey)
            GPIO.cleanup()

    #convert string to hex
    def toHex(self,s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', ' ')
            if len(hv) == 1:
                hv = '0'+hv
            lst.append(hv)
        
        return functools.reduce(lambda x,y:x+y, lst)

    #convert hex repr to string
    def toStr(self,s):
        return s and chr(atoi(s[:2], base=16)) + toStr(s[2:]) or ''
