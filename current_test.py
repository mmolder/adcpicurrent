#!/usr/bin/python

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
import time
import os
import math

i2c_helper = ABEHelpers()
bus = i2c_helper.get_smbus()
adc = ADCPi(bus, 0x68, 0x69, 12)	# 12 = 240 max samples per second 

ICAL = 30.3	# was 60.6 but halved since output doubled

# initial values
offsetI   = 760 	# new value, close to idle value
sampleI   = 760
sumI 	  = 0		# start with 0
filteredI = 0

# calcIrms
# reads the raw analog input and converts it to Irms, basically amps
def calcIrms(number_of_samples):
	global offsetI, sumI, sampleI, filteredI	# in order to modify
	supplyVoltage = 5000	# 5V supply voltage, change to 3300 for 3.3V

	for x in range(1, number_of_samples):
		lastSample = sampleI
		sampleI = adc.read_raw(1)	# read raw analog value
		lastFiltered = filteredI
		# filtering calculation, borrowed from https://openenergymonitor.org/forum-archive/node/3434.html
		filteredI = 0.996 * (lastFiltered + sampleI - lastSample)

		# root-mean-sqare method
		# 1) square current values
		sqI = filteredI * filteredI
		# 2) sum
		sumI += sqI

	I_RATIO = ICAL * ((supplyVoltage / 1000.0) / 1023.0)
	Irms = I_RATIO * math.sqrt(sumI / number_of_samples)
	sumI = 0
	return Irms

# main loop, do forever
while(True):
	ir = calcIrms(200)		# 200 samples to base result
	print("%0.3f A" % ir)		# amps
	watts = ir * 230.0
	print("%0.3f W" % watts)	# watts 
