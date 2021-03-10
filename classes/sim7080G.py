#!/usr/bin/python3

import functools
import logging
#import re
import time

try:
    import RPi.GPIO as GPIO
    import serial
except:
    pass

class simcom:
    powerKey = 4
    serial_dev = '/dev/ttyS0'
    bps = 115200
    nbchannels = '20,21'
    catmchannels = '19,20'
    uuid = None
    sim_pin = "3522"
    sim_apn = "m2m.movistar.es"
    network_up = False
    mqtt_url = 'broker.emqx.io'
    mqtt_port = 1883
    mqtt_topic_sub = ""
    mqtt_topic_pub = ""
    mqtt_message = 'M2M MOVISTAR'
    rec_buff = ''
    startedSim = False
    ser = ''
    cmdout = ''
    gps_status = 0
    ON = 1
    OFF = 0
    noresponse = 0
    MAXNORESPONSE = 5
    WAITONESECOND = 1
    WAITTWOSECONDS = 2
    WAITTTHREESECONDS = 3
    MAXCONNECTIONSTART = 1300

    def __init__(self, data):
        start_time = time.time()
        self.initialize(data)
        self.ser = serial.Serial(self.serial_dev, self.bps)
        self.ser.flushInput()
        self.startedSim = False
        self.checkStart()
        self.sim_checkpin()
        while True:
            time_difference = time.time() - start_time
            print ("Uptime: " + str(time_difference) + " A: [" + self.cmdout + "]") 
            if (time_difference > self.MAXCONNECTIONSTART):
                start_time = time.time()
                self.reboot()
            self.sim_signal()
            self.sim_connect()
        
    def __del__(self):
        self.powerDown(self.powerKey)

    def initialize(self, data):
        print(data['sim'])
        print(data['mqtt'])
        #serial_dev = '/dev/ttyS0'
        #bps = 115200
        #nbchannels = '20,21'
        #catmchannels = '19,20'
        """
        topic_pub:
        topic_sub:
         - command = "root/IECI/client/<device_id>/command"
         - other = "root/IECI/client/<device_id>/other"
        """
        if 'pin' in data['sim'].keys():
            self.sim_pin = data['sim']['pin']
        if  'powerkey' in data.keys():
            self.powerKey = data['powerkey']
        
        self.uuid = data['uuid']
        self.mqtt_topic_pub = data['mqtt']['topic'].replace("<device_id>", str(self.uuid))

        print(self.mqtt_topic_pub)
            
        print("Powerkey: " + str(self.powerKey))
        #self.sim_pin = "1111" if data['sim']['pin'] is None else data['sim']['pin']
        print ("PIN: " + str(self.sim_pin))
        #sim_apn = "m2m.movistar.es"
        #mqtt_url = 'broker.emqx.io'
        #mqtt_port = 1883
        #mqtt_topic_sub = ""
        #mqtt_topic_pub = ""
        
    """ 
    SIMCOM
    """
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
        self.noresponse=0

    def powerDown(self, powerKey = 4):
        logging.info('SIM7080X is powering off')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(powerKey, GPIO.OUT)
        GPIO.output(powerKey, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(powerKey, GPIO.LOW)
        time.sleep(5)
        logging.info('Good bye')



    def reboot (self):
        logging.info('SIM7080X reboot')
        self.powerDown()
        self.startedSim = False
        time.sleep(15)
        self.checkStart()

    def checkIfReboot (self):
        logging.info('SIM7080X check if reboot')
        self.noresponse += 1
        logging.debug('SIM7080X no response count is: {} of maximum of {}'.format(self.noresponse, self.MAXNORESPONSE ))
        if (self.noresponse > self.MAXNORESPONSE):
            self.reboot()

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
                return self.analize_output(self.cmdout, back)
                """if back not in rec_buff.decode():
                    logging.debug("Unexpected answer:" + command + ' back:\t' + rec_buff.decode())
                    return 0
                else:
                    logging.debug("ANSWER: "+ rec_buff.decode())
                    return 1 """
            else:
                logging.debug(command + ' no response')
                self.checkIfReboot()
        except Exception as e:
            logging.info('Algo paso al enviar el comando: ' + str(e))
            self.checkIfReboot()

    def checkStart(self):
        while not self.startedSim:
            # simcom module uart may be fool, so it is better
            # to send much times when it starts.
            logging.info('SIM7080X starting')
            try:
                for i in range(3):
                    self.ser.write('AT\r\n'.encode())
                    time.sleep(self.WAITONESECOND)
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
                self.checkIfReboot()
        logging.info('SIM7080X already started')
     
    
    """ 
    GPS
    """
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

    def gpsGetStatus(self):
        return self.sendAt('AT+CGNSINF', '+CGNSINF: ', 1)

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

    """
    Here we check output of the SIMCOM module, to define actions
    output - Salida del comando
    back - Salida esperada del comando
    """
    def simcom_analizeoutput (self, output, back):
        
        # Check if back is expected
        if back not in output:
            logging.debug("Unexpected answer:" + command + ' back:\t' + output)
            ret  = 0
        else:
            logging.debug("ANSWER: "+ output)
            ret = 1
        
        # Check answer to understand future behaviour
        #pattern = re.compile("CPSI.*online")
        if ("CPSI" in output):
            if ("NO SERVICE" in output):
                self.network_up = False
            else:
                self.network_up = True
                print("OEOEOEOEO =================00000000 CONECTADO!!!")
        
        
        return ret
        


    """
    SIM - CELL
    """
    def sim_checkpin(self):
        if (self.sendAt('AT+CPIN?','READY', 1)):
            logging.debug('SIM prepadada')
        else:
            self.sendAt('AT+CPIN=' + self.sim_pin, 'OK', 1)
            logging.debug('Revisar SIM')

    def sim_reboot(self):
        #self.sendAt('AT+CREBOOT', 'OK', 1)
        self.sendAt('AT+CFUN=1,1', 'OK', 1)

    def sim_signal(self):
        self.sendAt('AT+CSQ','OK',3)
        val = self.sendAt('AT+CPSI?','CPSI',3)
        print ('Valor: {}'.format(val))
        time.sleep(3)
        #        self.sendAt('AT+CGREG?', 'OK', 3)
        #        self.sendAt('AT+CGNAPN', 'OK', 3)
        #        self.sendAt('AT+CNACT?','OK',3)
        #        self.sendAt('AT+CGACT?','OK',3)
        #        self.sendAt('AT+CGNAPN=?','OK',3)
        #        self.sendAt('AT+CBANDCFG=?','OK',3)
        #        self.sendAt('AT+CBANDCFG?','OK',3)
        #        self.sendAt('AT+COPS?','OK',3)
        #        self.sendAt('AT+CSQ','OK',3)
        #        self.sendAt('AT+COPS=?','OK',900)

    def sim_checkconnection(self):
        if ( self.sendAt('AT+CPSI?','NO SERVICE',3) == 1 ):
            return 0
        else:
            return 1

    def sim_connect(self):
        logging.info('wait for signal')
        time.sleep(3)
        self.sendAt('AT+CSQ', 'OK', 1)
        self.sendAt('AT+CPSI?', 'OK', 1)
        self.sendAt('AT+CGREG?', '+CGREG: 0, 1', 0.5)
        #self.sendAt('AT+CNCFG=0,1,"m2m.movistar.es"', 'OK', 1)
        self.sendAt('AT+CNCFG=0,1,"' + self.sim_apn + '"', 'OK', 1)
        self.sendAt('AT+CNACT=0, 1', 'OK', 1)
        self.sim_getnbSettings()

    def sim_factoryTestMode(self):
        self.sendAt('AT+CFUN=5','OK', 1)
    
    def sim_fullMode(self):
        self.sendAt('AT+CFUN=1','OK', 1)
    
    def sim_resetModule(self):
        self.sendAt('AT+CFUN=1,1','OK', 10)
    
    def sim_checkpin(self):
        self.sendAt('AT+CPIN?','OK', 1)
 
    def sim_getConfig(self):
        self.sendAt('AT+CNMP=?','OK',3)
        self.sendAt('AT+CNMP?','OK',3)
        self.sendAt('AT+CMNB=?','OK',3)
        self.sendAt('AT+CMNB?','OK',3)
        self.sendAt('AT+CBANDCFG=?','OK',1)
        self.sendAt('AT+CBANDCFG?','OK',1)
        self.sendAt('AT+CGNAPN', 'OK', 1)

    def sim_getOperatorSettings(self):
        self.sendAt('AT+COPS?','OK',1)
        pass

    def sim_getSimcomdata(self):
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
        #self.sendAt('AT+ANTENALLCFG=?','OK',2)
        #self.sendAt('AT+ANTENALLCFG?','OK',2)
        # Lock the special NB-IOT cell
#        self.sendAt('AT+NCELLLOCK=?','OK',2)
#        self.sendAt('AT+NCELLLOCK?','OK',2)

    def sim_getnbSettings(self):
        # NB-IOT Scrambling Feature
        self.sendAt('AT+NBSC?','OK',1)
        # NB-IOT Band Scan Optimization
        self.sendAt('AT+CNBS?','OK',1)
        # NB-IOT Service Domain Preference
        self.sendAt('AT+CNDS?','OK',1)
        # NB-IOT Configure Release Assistance Indication
        self.sendAt('AT+CRAI?','OK',1)
        self.sendAt('AT+CGNAPN', 'OK', 1)
    
    def sim_getsignal(self):
        self.sendAt('AT+CSQ','OK',1)

    def sim_getipSettings(self):
        # APP Network Active:
        self.sendAt('AT+CNACT?','OK',1)
        self.sendAt('AT+CDNSCFG?','OK',1)

    def getSettings(self):
        self.sim_getConfig()
        self.sim_getOperatorSettings()
        self.sim_getSimcomdata()
        self.sim_getnbSettings()
        self.sim_getsignal()
        self.sim_getipSettings()

    def sim_set_band(self):
        #self.sendAt('AT+CBANDCFG="NB-IOT",1,2,3,4,5,8,12,13,18,19,20,25,26,28,66,71,85','OK',2)
        # self.sendAt('AT+CBANDCFG="CAT-M",1,2,3,4,5,8,12,13,14,18,19,20,25,26,27,28,66,85','OK',1)
        # Segun https://halberdbastion.com/intelligence/mobile-networks/vodafone-spain, limitamos las bandas
        # Segun https://halberdbastion.com/intelligence/countries-nations/spain       
        #Vodafone Spain
        #Country: Spain
        #Technology: NB-IoT (LTE Cat-NB1)
        #Band: B20 (800 MHz)
        #Status: Active
        self.sendAt('AT+CBANDCFG="NB-IOT",20','OK',2)
        self.sendAt('AT+CBANDCFG="NB-IOT",' + self.nbchannels + "\'",'OK',2)
        #self.sendAt('AT+CBANDCFG="CAT-M",20','OK',1)
        self.sendAt('AT+CBANDCFG="CAT-M",' + self.catmchannels + "\'",'OK',1)


    def sim_set_network_parameters(self):
        #
        NBIOT=2
        CATM=1
        CATMNBIOT=3
#        service = 1  # CAT-M
        service = CATMNBIOT
 #       service = 3  # Both
        self.sendAt('AT+CMNB='+str(service), 'OK', 3)
        AUTO= 2
        GSM = 13
        LTE = 38
        GSMyLTE = 51
        network = AUTO
        self.sendAt('AT+CNMP='+str(network), 'OK', 3)
        # 1 CAT-M  2 NB-IOT  3 CAT-M and NB-IOT
        SNRL1 = 1 # UE tries SNR level 0
        SNRL2 = 2 # UE tries SNR level 0 and level 1
        SNRL3 = 3 # UE tries SNR level 0, level 1 and level 2 band scan
        SNRL4 = 4 # Reserved
        SNRL5 = 5 # UE tries SNR level 2 band scan only
        bandopt = SNRL3
        self.sendAt('AT+CNBS='+str(bandopt), 'OK', 3)
        PS = 1 # PS (Packed Switched Domain) ONLY
        CS = 2 # CS(Circuit Switched Domain) + PS (Packet Switched Domain)
        dompref = PS
        self.sendAt('AT+CNDS='+str(dompref), 'OK', 3)
        SCRDIS = 0 # Disable scambilng feature in NB-IOT network 
        SCRENA = 1 # Enable scambilng feature in NB-IOT network 
        scrambling = SCRENA
        
        self.sendAt('AT+NBSC='+str(scrambling), 'OK', 3)
    
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
        self.sim_set_band()
        self.phone_enable()
        self.sim_set_network_parameters()
        self.sendAt('AT+CMCFG=1', 'OK', 3)
        self.network_nbsetup()
        self.network_register()
#        self.network_connect()
 
    def mqtt_init (self):
        #self.sendAt('AT+SMCONF=\"URL\", \"broker.mqttdashboard.com\", \"1883\"', 'OK', 1)
        self.sendAt('AT+SMCONF=\"URL\", \"' + self.mqtt_url + '\", \"' + self.mqtt_port + '\"','OK', 1)
        self.sendAt('AT+SMCONF=\"KEEPTIME\", 60', 'OK', 1)
        self.sendAt('AT+SMCONN', 'OK', 5)
    
    def mqtt_pub(self, message, suffix = ""):
        self.mqtt_init()
        cmd = 'AT+SMPUB="' + self.mqtt_topic_pub + suffix + '", 17, 1, 0'
        self.sendAt(cmd, 'OK', 1)
        self.ser.write(message.encode())
    
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
            self.sendAt('AT+SMCONF=\"URL\", \"broker.mqttdashboard.com\", \"1883\"', 'OK', 1)
#            self.sendAt('AT+SMCONF="URL", ' + self.mqtt_url + ', ' + self.mqtt_port,'OK', 1)
            self.sendAt('AT+SMCONF=\"KEEPTIME\", 60', 'OK', 1)
            self.sendAt('AT+SMCONN', 'OK', 5)
            self.sendAt('AT+SMPUB="waveshare1_sub", 17, 1, 0', 'OK', 1)
            #self.sendAt('AT+SMSUB="waveshare1_pub", 1', 'AMS-OK', 1)
            self.ser.write(self.mqtt_message.encode())
            time.sleep(10)
            logging.info('send message successfully!')
            self.sendAt('AT+SMDISC', 'OK', 1)
            self.sendAt('AT+CNACT=0, 0',  'OK',  1)
#            self.powerDown(self.powerKey)
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


"""
# State machine in python
# We have diferent states of the SIMCOM
- Encendido
- Sim Unlock
- Network Search
- Network Registry
- IP Stack
- Protocols   (Diferent states depending on protocol)
    - PING
    - MQTT
    - ....

- Idle
- Apagado
"""
#State Machine
class StateMachine:
    def __init__(self, initialState):
            self.currentState= initialState
            self.currentState.run()

    def runAll(self, inputs):
            for i in inputs:
                print(i)
                self.currentState = self.currentState.next(i)
                self.currentState.run()

class State_poweron:
    def run(self):
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
        self.noresponse=0


    def next(self, input):
        assert 0, "run not implemented"

class State_simUnlock:
    pass


class State_2:
    pass
