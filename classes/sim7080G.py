#!/usr/bin/python3

import functools
import logging
import RPi.GPIO as GPIO
import time
import serial


class simcom:

    powerKey = 4
    rec_buff = ''
    startedSim = False
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
    noresponse = 0
    MAXNORESPONSE=3

    def __init__(self, data):
        self.ser = serial.Serial(self.serial_dev, self.bps)
        self.ser.flushInput()
        self.startedSim = False
        self.checkStart()
        
    def __del__(self):
        self.powerDown(self.powerKey)

    def powerOn(self, powerKey):
        logging.info('SIM7080X is powering on')
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

    def reboot (self):
        self.noresponse=0
        powerDown()
        time.sleep(5)
        powerOn()


    def sendAt(self, command, back, timeout):
        rec_buff = ''
        try:
            self.ser.write((command+'\r\n').encode())
            time.sleep(timeout)

            if self.ser.inWaiting():
                time.sleep(timeout)
                rec_buff = self.ser.read(self.ser.inWaiting())
            if rec_buff != '':
                self.cmdout = rec_buff.decode()
                if back not in rec_buff.decode():
                    logging.debug("Unexpected answer:" + command + ' back:\t' + rec_buff.decode())
                    return 0
                else:
                    logging.debug("ANSWER: "+ rec_buff.decode())
                    return 1
            else:
                logging.debug(command + ' no response')
                self.noresponse += 1
                if (self.noresponse > self.MAXNORESPONSE):
                    self.reboot()

        except Exception as e:
            logging.info('Algo paso al enviar el comando')
            pass



    def checkStart(self):
        while not self.startedSim:
            # simcom module uart may be fool, so it is better
            # to send much times when it starts.
            logging.info('SIM7080X starting')
            try:
                self.ser.write('AT\r\n'.encode())
                time.sleep(1)
                self.ser.write('AT\r\n'.encode())
                time.sleep(1)
                self.ser.write('AT\r\n'.encode())
                time.sleep(1)
                if self.ser.inWaiting():
                    time.sleep(0.01)
                    recBuff = self.ser.read(self.ser.inWaiting())
                    self.startedSim = True
                    logging.info('SIM7080X is ready')
                    logging.debug('Try to start' + recBuff.decode())
                    if 'OK' in recBuff.decode():
                        recBuff = ''
                        break

                else:
                    self.powerOn(self.powerKey)
            except UnicodeDecodeError:
                logging.info ("Unicode error")
                # Como no esta el self.startedSim, debe repetirse, ojo con bucle infinito
                # Volvemos a ejecutar quizas sería mejor un bucle
                #self.checkStart()
            except Exception as e:
                print("ERROR NO CONTROLADO")
                logging.info (format(e))
        logging.info('SIM7080X already started')
     
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
        position = False
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
                    #time.sleep(1)
                else:
                    logging.info('Posicion: ' + self.cmdout)
                    i=0
                    position = self.cmdout.splitlines()[2].split(":")[1].lstrip()
                    rec_null = False
                    print(position)
            else:
                logging.info('getGpsPosition error %s' % answer)
                logging.debug(self.cmdout)
                rec_buff = ''
                return False
            #time.sleep(1.5)
        return position

    def sim_pin(self):

        if (self.sendAt('AT+CPIN?','READY', 1)):
            logging.debug('SIM prepadada')
        else:
            logging.debug('Revisar SIM')

    def reboot(self):
        self.sendAt('AT+CREBOOT', 'OK', 1)

    def sim_signal(self):
        self.sendAt('AT+CSQ','OK',3)
#        self.sendAt('AT+CGREG?', 'OK', 3)
#        self.sendAt('AT+CGNAPN', 'OK', 3)
        self.sendAt('AT+CPSI?','CPSI',3)
#        self.sendAt('AT+CNACT?','OK',3)
#        self.sendAt('AT+CGACT?','OK',3)
#        self.sendAt('AT+CGNAPN=?','OK',3)
#        self.sendAt('AT+CBANDCFG=?','OK',3)
#        self.sendAt('AT+CBANDCFG?','OK',3)
#        self.sendAt('AT+COPS?','OK',3)
#        self.sendAt('AT+CSQ','OK',3)
#        self.sendAt('AT+COPS=?','OK',900)

        time.sleep(5)

    def network_connect(self):
            logging.info('wait for signal')
            time.sleep(10)
            self.sendAt('AT+CSQ', 'OK', 1)
            self.sendAt('AT+CPSI?', 'OK', 1)
            self.sendAt('AT+CGREG?', '+CGREG: 0, 1', 0.5)
            self.sendAt('AT+CNACT=0, 1', 'OK', 1)


    def factoryTestMode(self):
        self.sendAt('AT+CFUN=5','OK', 1)
    
    def fullMode(self):
        self.sendAt('AT+CFUN=1','OK', 1)
    
    def resetModule(self):
        self.sendAt('AT+CFUN=1,1','OK', 10)
    
    def checkSIM(self):
        self.sendAt('AT+CPIN?','OK', 1)
 
    def view_basicConfigOptions(self):
        self.sendAt('AT+CNMP=?','OK',3)
        self.sendAt('AT+CNMP?','OK',3)
        self.sendAt('AT+CMNB=?','OK',3)
        self.sendAt('AT+CMNB?','OK',3)
        self.sendAt('AT+CBANDCFG=?','OK',1)
        self.sendAt('AT+CBANDCFG?','OK',1)
        self.sendAt('AT+CGNAPN', 'OK', 1)

    def view_phoneSettings(self):
        # Configure CAT-M or NB-IOT
        self.sendAt('AT+CBANDCFG?','OK',1)
        # Configure mobile operation band
        self.sendAt('AT+CBAND?','OK',1)
        # Preferred mode selection
        self.sendAt('AT+CNMP?','OK',1)
        # Select between CAT-M and NB-IOT
        self.sendAt('AT+CMNB?','OK',1)

    def view_simSettings(self):
        self.sendAt('AT+CPIN?','OK',1)

    def view_operatorSettings(self):
        self.sendAt('AT+COPS?','OK',1)
        pass

    def view_simcomdata(self):
        # Network system mode
        self.sendAt('AT+CNSMOD?','OK',1)
        # Power Saving
        self.sendAt('AT+CPSMS?','OK',1)
        # Service Domain Preference
        self.sendAt('AT+CSDP?','OK',1)
        # NB-IOT Scrambling Feature
        self.sendAt('AT+NBSC?','OK',1)
        # NB-IOT Band Scan Optimization
        self.sendAt('AT+CNBS?','OK',1)
        # NB-IOT Service Domain Preference
        self.sendAt('AT+CNDS?','OK',1)
        # Manage Mobile Operator Configuration
        self.sendAt('AT+CMCFG?','OK',1)
        # Show remote IP Addr and Port when receive data
        self.sendAt('AT+CASRIP?','OK',1)
        # Read PSM Dynamic Parameters
        self.sendAt('AT+CPSMRDP','OK',1)
        # Configure PSM version and minimum threshold
        self.sendAt('AT+CPSMCFG?','OK',1)
        # Enable deep Sleep Wakeup Indication
        self.sendAt('AT+CPSMSTATUS?','OK',1)
        # NB-IOT Configure Release Assistance Indication
        self.sendAt('AT+CRAI?','OK',1)
        # Configure Antenna Tuner
        self.sendAt('AT+ANTENALLCFG?','ANTENA',2)

    def view_nbSettings(self):
        # NB-IOT Scrambling Feature
        self.sendAt('AT+NBSC?','OK',1)
        # NB-IOT Band Scan Optimization
        self.sendAt('AT+CNBS?','OK',1)
        # NB-IOT Service Domain Preference
        self.sendAt('AT+CNDS?','OK',1)
        # NB-IOT Configure Release Assistance Indication
        self.sendAt('AT+CRAI?','OK',1)

        self.sendAt('AT+CGNAPN', 'OK', 1)
    
    
    def view_signal(self):
        self.sendAt('AT+CSQ','OK',1)

    def view_ipSettings(self):
         # APP Network Active
        self.sendAt('AT+CNACT?','OK',1)
   
    def viewSettings(self):
        self.view_basicConfigOptions()
        self.view_phoneSettings()
        self.view_simSettings()
        self.view_operatorSettings()
        self.view_simcomdata()


    def defineBands(self):
        self.sendAt('AT+CBANDCFG="NB-IOT",1,2,3,4,5,8,12,13,18,19,20,25,26,28,66,71,85','OK',2)
        self.sendAt('AT+CBANDCFG="CAT-M",1,2,3,4,5,8,12,13,14,18,19,20,25,26,27,28,66,85','OK',1)


    def network_parametersetup(self):
        #
        NBIOT=2
        CATM=1
        CATMNBIOT=3
#        service = 1  # CAT-M
        service = NBIOT
 #       service = 3  # Both
        AUTO= 2
        GSM = 13
        LTE = 38
        GSMyLTE = 51
        network = AUTO
        # 1 CAT-M  2 NB-IOT  3 CAT-M and NB-IOT
        self.sendAt('AT+CMNB='+str(service), 'OK', 3)
        self.sendAt('AT+CNMP='+str(network), 'OK', 3)
    
    def network_select (self):
        self.sendAt('AT+COPS=?','COPS', 600)

    def network_register(self):
        DISABLE=0
        ENABLE=1
        ENABLEGPRS=2

        self.sendAt('AT+CREG='+str(ENABLE), 'OK', 1)
        time.sleep(1)


    def network_nbsetup(self):
        pass


    def phone_setstatus(self, value):
        self.sendAt('AT+CFUN='+str(value), 'OK', 1)

    def phone_disable(self):
        self.phone_setstatus(0)

    def phone_enable(self):
        self.phone_setstatus(1)



    def test_nb(self):
        self.viewSettings()
        self.phone_disable()
        self.defineBands()
        self.phone_enable()
        self.network_parametersetup()
        self.sendAt('AT+CMCFG=1', 'OK', 3)
        self.network_nbsetup()
        self.network_register()
#        self.network_connect()
 

    def test_sim3(self):
        self.sendAt('ATZ', 'OK', 1)
        self.sendAt('AT+CFUN=0', 'OK', 1)
        self.sendAt('AT+CFUN=1', 'OK', 1)

        self.preferredtechselection()
#        self.sendAt('AT+CGDCONT=0,"IP","nb.inetd.gdsp"', 'OK', 1)
        self.network_register()
        #self.factoryTestMode()
#        self.resetModule()
        #self.checkStart()
#        self.sim_pin()
        #self.sendAt('AT+CMNB=3', 'OK', 1)
#        self.preferredtechselection()
#        self.preferredmodeselection()
#        self.sendAt('AT+CREG=2', 'OK', 1)
#        self.sim_signal()
#        self.fullMode(),
#        self.sendAt('AT+CBANDCFG="CAT-M",85','OK',1)
#        self.viewOptions()
        self.viewSettings()
        self.sim_connect()


    def test_sim2(self):
        self.sendAt('ATZ', 'OK', 1)
        self.sendAt('AT+CFUN=0', 'OK', 1)
        self.sendAt('AT+CBANDCFG=?','OK',1)
        self.sendAt('AT+CBANDCFG?','OK',1)
        self.sendAt('AT+CREG=1', 'OK', 1)
        #self.sendAt('AT*MCGDEFCONT="IP","spe.inetd.vodafone.nbiot"','AT',1)
#        self.sendAt('AT+CGDCONT=0,"IP","nb.inetd.gdsp"','AT',3)
        self.sendAt('AT+CGDCONT=1,"IP","nb.inetd.gdsp"','OK',3)
#       self.sendAt('AT+CBANDCFG="CAT-M",1','OK',1)
 #       self.sendAt('AT+CBANDCFG="NB-IOT",20','OK',1)
        self.sendAt('AT+CBANDCFG="NB-IOT",1,2,3,4,5,8,12,13,14,18,19,25,26,27,28,66,71,85','OK',1)

 #       self.sendAt('AT+CNBS=3', 'OK', 1)
 #       self.sendAt('AT+CNMP=51', 'OK', 1)
        self.sendAt('AT+CMNB=3', 'OK', 1)
 
        self.sendAt('AT+CFUN=1', 'OK', 1)
#        self.sendAt('AT+CGATT=1','AT',3)
#        self.sendAt('AT+CGACT=1,1','OK',3)
 
 #       self.sendAt('AT+CBAND=?','OK',1)
 #       self.sendAt('AT+CBAND="ALL_MODE"','OK',1)
#        self.sendAt('AT+COPS=1,2,"21401"','COPS', 1)
        self.sendAt('AT+COPS=0','OK', 1)


    def test_sim(self):
        logging.info('Test SIM CARD')
        #self.sendAt('AT+CFUN=1','OK',3)
        self.sim_pin()
        self.sendAt('ATI', 'OK', 1)
        self.sendAt('AT+CGMI', 'OK', 1)
        self.sendAt('AT+CGMM', 'OK', 1)
        self.sendAt('AT+CCID', 'OK', 1)
        self.sendAt('AT+CFUN?', 'OK', 1)
        self.sendAt('AT+COPS=1,2,"21401"','COPS', 6)
        time.sleep(5)
        self.sendAt('AT+CSQ','OK',3)
        time.sleep(5)
        self.sendAt('AT+CSQ','OK',3)
        self.sendAt('AT+CGDCONT=1,"IP","spe.inetd.vodafone.nbiot"','OK',3)
        time.sleep(5)
        self.sendAt('AT+CSQ','OK',3)
        #self.sendAt('AT+CMNB=2', 'OK', 1)
#        self.sendAt('AT+CBANDCFG="NB-IOT",2,3,4,8,9,12,13','OK',3)
        #self.sendAt('AT+CGDCONT=1,"IP","ac.vodafone.es","0.0.0.0",0,0','OK',3)
        #self.sendAt('AT+CGDCONT=1,"IP","spe.inetd.vodafone.nbiot","0.0.0.0",0,0','OK',3)

        self.sendAt('AT+CNBS=3', 'OK', 1)
        self.sendAt('AT+CNMP=2', 'OK', 1)
        self.sendAt('AT+CMNB=2', 'OK', 1)
        #self.sendAt('AT+COPS=1,2,"21409",9','COPS', 6)
        #self.sendAt('AT+COPS=0','COPS', 6)
        self.sendAt('AT+CGREG=1', 'OK', 3)
        self.sendAt('AT+CGDCONT=1,"IP","spe.inetd.vodafone.nbiot"','OK',3)
        self.sendAt('AT+CGDCONT=1,"IP","spe.inetd.vodafone.nbiot"','OK',3)
        self.sendAt('AT+CGACT=1','OK',30)
        #self.sendAt('AT+COPS=1,2,"21409",9','COPS', 6)
        #self.sendAt('AT+QCFG="iotopmode",1','OK', 6)
        #self.sendAt('AT+QCFG="iotopmode",1','OK', 6)
        #self.sendAt('AT+COPS=1,2,"21409"','COPS', 6)
        #self.sendAt('AT+CSQ','OK',3)

        #self.sendAt('AT+CBANDCFG=?', 'OK', 1)
        #self.sendAt('AT+CNMP=?', 'OK', 1)
#        self.sendAt('AT+CNMP=38', 'OK', 1)
        #self.sendAt('AT+CGDCONT=1,"IP","ac.vodafone.es","0.0.0.0",0,0','OK',3)
        #self.sendAt('AT+CGNAPN','OK',3)
#        self.sendAt('AT+CPSI?','OK',3)
#        self.sendAt('AT+CBANDCFG="NB-IOT",8','OK',3)
        time.sleep(10)
#        self.sendAt('AT+CPSI','OK',3)
#        self.sendAt('AT+CGPADDR=?','OK', 3)
#        self.sendAt('AT+COPS?','OK', 6)
        #     

        #self.sendAt('AT+COPS=1,1,1','OK', 600)
#        self.sendAt('AT+CPSI','OK',3)
#        self.sendAt('AT+CSQ','OK',3)
#        self.sendAt('AT+CNMP=38')
#        self.sendAt('AT+CMNB=2')
#        self.sendAt('AT+CSQ')
#        self.sendAt('AT+CGREG')
#        self.sendAt('AT+CGNAPN')
#        self.sendAt('AT+CPSI?')
#        for i in range (1,5):
#            self.sendAt('AT+CGATT?','OK',3)
#            time.sleep(1)
#        self.sendAt('AT+CSQ','OK',3)
#        self.sendAt('AT+CGDCONT=1,"IP","nb.inetd.gdsp","0.0.0.0",0,0','OK',3)
#

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

class gnss_object:
    def __init__(self, data):
        data.split(",")
