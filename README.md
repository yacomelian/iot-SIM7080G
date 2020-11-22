# SIM7080G Module python test


## Install

	pip3 install -r requirements.txt
	apt install python3-yaml

## GPS

###	Resume table:
   
    
| Index | Parameter                  | Unit               | Range                                                                                | Length |
|-------|----------------------------|--------------------|--------------------------------------------------------------------------------------|--------|
| 1     | GNSS run status            | --                 | 0-1                                                                                  | 1      |
| 2     |                            | --                 | 0-1                                                                                  | 1      |
| 3     | UTC date & Time            | yyyyMMddhhmmss.sss | yyyy: [1980,2039] <br>MM : [1,12] <br>dd: [1,31] <br>hh: [0,23] <br>mm: [0,59] <br>ss.sss:[0.000,60.999] | 18     |
| 4     | Latitude                   | ±dd.dddddd         | [-90.000000,90.000000]                                                               | 10     |
| 5     | Longitude                  | ±ddd.dddddd        | [-180.000000,180.000000]                                                             | 11     |
| 6     | MSL Altitude               | meters             |                                                                                      | 8      |
| 7     | Speed Over Ground          | Km/hour            | [0,999.99]                                                                           | 6      |
| 8     | Course Over Ground         | degrees            | [0,360.00]                                                                           | 6      |
| 9     | Fix Mode                   |                    | 0,1,2                                                                                | 1      |
| 10    | Reserved1                  |                    |                                                                                      | 0      |
| 11    | HDOP                       |                    | [0,99.9]                                                                             | 4      |
| 12    | PDOP                       | --                 | [0,99.9]                                                                             | 4      |
| 13    | VDOP                       | --                 | [0,99.9]                                                                             | 4      |
| 14    | Reserved2                  |                    |                                                                                      | 0      |
| 15    | GPS Satellites in View     | #                  | [0,99]                                                                               | 2      |
| 16    | GNSS Satellites Used       | #                  | [0,99]                                                                               | 2      |
| 17    | GLONASS Satellites in View | #                  | [0,99]                                                                               | 2      |
| 18    | Reserved3                  |                    |                                                                                      |        |
| 19    | C/N0 max                   | dBHz               | [0,55]                                                                               | 2      |
| 20    | HPA                        | meters             | [0,9999.9]                                                                           | 6      |
| 21    | VPA                        | meters             | [0,9999.9]                                                                           | 6      |


### Parameters
#### GNSS run status
	0 GNSS off
	1 GNSS on
#### Fix status
	0 Not fixed position
	1 Fixed position
#### UTC date & Time
	Example 20201122211554.000
	Year: yyyy
	Month: mm
	Day: dd
	Hour: hh
	Minutes: MM
	Seconds: ss
	MS: Always .000
	
#### Latitude

#### Longitude
#### MSL Altitude
#### Speed Over Ground
#### Course Over Ground
#### Fix Mode
#### Reserved1
#### HDOP - Horizontal dilution of precision
#### DOP - Dilution of precision
Wikipedia: Dilution of precision (DOP), or geometric dilution of 
precision (GDOP), is a term used in satellite navigation and 
geomatics engineering to specify the Error propagation as a 
mathematical effect of navigation satellite geometry on positional 
measurement precision. 
    
|Value 	|Rating 	|Description
|-------|-----------|-----------------------------------------------------------------------|
|1 		|Ideal 		|Highest possible confidence level to be used for applications demanding the highest possible precision at all times.|
|1-2 	|Excellent 	|At this confidence level, positional measurements are considered accurate enough to meet all but the most sensitive applications.|
|2-5 	|Good 		|Represents a level that marks the minimum appropriate for making accurate decisions. Positional measurements could be used to make reliable in-route navigation suggestions to the user.|
|5-10 	|Moderate 	|Positional measurements could be used for calculations, but the fix quality could still be improved. A more open view of the sky is recommended.|
|10-20 	|Fair 		|Represents a low confidence level. Positional measurements should be discarded or used only to indicate a very rough estimate of the current location. |
|>20 	|Poor 		|At this level, measurements are inaccurate by as much as 300 meters with a 6-meter accurate device (50 DOP × 6 meters) and should be discarded. |

##### PDOP - Position (3D) of precision
##### VDOP - Vertical Dilution of precision
##### Reserved2
##### GNSS Satellites in View
 Global Navigation Satellite System
##### Reserved3
a
##### HPA - Horizontal position accuracy
	Margen de error en la distancia horizontal
##### VPA - Vertical position accuracy
	Margen de error en distancia vertical

### Example
Example output: 1,1,20201122211554.000,28.416938,-16.305379,185.985,
0.00,,0,,1.3,1.5,0.9,,10,,7.0,6.0
    
# References
[Wikipedia](https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)) \
[SIMCOM](https://simcom.ee/documents/SIM7060G/SIM7060%20Series_GNSS_Application%20Note_V1.03.pdf)
