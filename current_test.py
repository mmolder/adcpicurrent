#!/usr/bin/python

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
import time
import os
import math

i2c_helper = ABEHelpers()
bus = i2c_helper.get_smbus()
adc = ADCPi(bus, 0x68, 0x69, 12)	# 12 = 240 max samples per second 
ICAL = 60.6
ADC_BITS = 12
ADC_COUNTS = 1<<ADC_BITS
offsetI = ADC_COUNTS>>1
sampleI = 0
sqI = 0
sumI = 0

def calcIrms(number_of_samples):
	supplyVoltage = 5000
	global offsetI
	global sampleI
	global sqI
	global sumI
	for x in range(1, number_of_samples):
		sampleI = adc.read_raw(1)
		offsetI = offsetI + ((sampleI - offsetI) / 1024)
		filteredI = sampleI - offsetI
		sqI = filteredI * filteredI
		sumI += sqI

	I_RATIO = ICAL * ((supplyVoltage / 1000.0) / (ADC_COUNTS))
	Irms = I_RATIO * math.sqrt(sumI / number_of_samples)
	sumI = 0
	return Irms

# main loop

while(True):
	ir = calcIrms(1480)
	print("%0.3f A" % ir)
	watts = ir*230.0
	print("%0.3f W" % watts)
	#raw = adc.read_raw(1)
	#voltage = raw*(5.0/1023.0)
	#print("Voltage: %0.3f" % voltage) 
