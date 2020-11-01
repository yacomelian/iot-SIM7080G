#!/usr/bin/python3

# import RPi.GPIO as GPIO
import time
import serial


class simcom:

    powerKey = 4
    rec_buff = ''
    Message = 'www.waveshare.com'
    mqtt_url = 'broker.emqx.io'
    mqtt_port = 1883
    serial_dev = '/dev/ttyS0'
    bps = 9600
    ser = ''

    def __init__(self, data):
        self.ser = serial.Serial(self.serial_dev, self.bps)
        self.ser.flushInput()

    def powerOn(self, powerKey):
        print('SIM7080X is starting:')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(powerKey, GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(powerKey, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(powerKey, GPIO.LOW)
        time.sleep(5)
        self.ser.flushInput()

    def powerDown(self, powerKey):
        print('SIM7080X is loging off:')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(powerKey, GPIO.OUT)
        GPIO.output(powerKey, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(powerKey, GPIO.LOW)
        time.sleep(5)
        print('Good bye')

    def sendAt(self, command, back, timeout):
        rec_buff = ''
        self.ser.write((command+'\r\n').encode())
        time.sleep(timeout)
        if self.ser.inWaiting():
            time.sleep(0.1)
            rec_buff = self.ser.read(self.ser.inWaiting())
        if rec_buff != '':
            if back not in rec_buff.decode():
                print(command + ' back:\t' + rec_buff.decode())
                return 0
            else:
                print(rec_buff.decode())
                return 1
        else:
            print(command + ' no responce')

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
                print('SOM7080X is ready\r\n')
                print('try to start\r\n' + recBuff.decode())
                if 'OK' in recBuff.decode():
                    recBuff = ''
                    break
            else:
                self.powerOn(self.powerKey)

    def getGpsPosition(self):
        rec_null = True
        answer = 0
        print('Start GPS session...')
        rec_buff = ''
        time.sleep(5)
        self.sendAt('AT+CGNSPWR=1', 'OK', 0.1)
        while rec_null:
            answer = self.sendAt('AT+CGNSINF', '+CGNSINF: ', 1)
            if 1 == answer:
                answer = 0
                if ',,,,,,' in rec_buff:
                    print('GPS is not ready')
                    rec_null = False
                    time.sleep(1)
            else:
                print('error %d' % answer)
                rec_buff = ''
                self.sendAt('AT+CGNSPWR=0', 'OK', 1)
                return False
            time.sleep(1.5)

    def test_mqtt(self):
        try:
            self.checkStart()
            print('wait for signal')
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
            print('send message successfully!')
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