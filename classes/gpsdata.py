
class simcomgpsdata:

    nameslist = ['runstatus', 'fixstatus', 'utcdatetime', 'latitude',
        'longitude','altitude', 'speedoverground', 'courseoverground',
        'fixmode', 'reserved1', 'hdop','pdop','vdop', 'reserved2',
        'numsatellites', 'reserved3', 'hpa', 'vpa']
    """ GNSS run status>,<Fix status>,<UTC date & Time>,<Latitude>,
    <Longitude>,<MSL Altitude>,<Speed Over Ground>,<Course Over Ground>,
    <Fix Mode>,<Reserved1>,<HDOP>,<PDOP>,<VDOP>,<Reserved2>
    ,<GNSS Satellites in View>,<Reserved3>,<HPA>,<VPA> """
    datastr=''
    datalist = []
    SEPARATOR=","

    def __init__(self, stringdata):
        """
        docstring
        """
        self.inputstr=stringdata
        self.datalist = self.inputstr.split(self.SEPARATOR)
        pass

    def mapall(self):
        i=0
        for value in self.datalist:
            try:
                key = self.nameslist[i]             
            except IndexError:
                key = "Extra" + str(i)
            finally:
                print ("{:s} = {:s}".format(key, value))
                i+=1
            