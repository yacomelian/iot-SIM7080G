#!/usr/bin/env python3
#import sys
#sys.path.append('../classes')

from classes import simcomgpsdata
#from classes import simcom


#from classes import simcomgpsdata


strexamples=["1,1,20201129145559.000,28.416744,-16.305781,119.562,0.00,,0,,2.0,2.2,1.0,,7,,15.0,24.0",
    ",,,,,,,,,,,,,,,,,",
    "1,1,20201129175723.000,28.416947,-16.305671,161.116,0.00,,0,,2.0,2.2,1.0,,6,,10.8,12.0",
    "1,1,20201129175735.000,28.416947,-16.305671,161.131,0.00,,0,,1.4,1.7,1.0,,7,,10.7,12.0",
    "1,1,20201129175747.000,28.416947,-16.305670,161.153,0.00,,0,,1.6,1.8,0.9,,7,,13.7,16.0"]


for item in strexamples:
    gps = simcomgpsdata(item)