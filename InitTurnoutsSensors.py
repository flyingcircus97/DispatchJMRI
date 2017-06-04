# Sample script showing how to initialize
# turnouts based on the state of their input
# sensors (e.g. feedback)
#
# This is particularly useful for a C/MRI system, where
# the turnouts need to be set to a particular state quickly
#
#
# Part of the JMRI distribution

import jmri
import time

def initTurnout(turnout):
    to = turnouts.provideTurnout(turnout)
    #to.setState(to.getKnownState())
    to.setState(2) #Mainline
    #return

def initSensor(sensor):
    s = sensors.provideSensor(sensor)
    s.setKnownState(4) #4 = inactive


time.sleep(10)
# invoke for all defined turnouts
for x in turnouts.getSystemNameList().toArray() :
  if ((len(x)<= 4) and (x[:2] == 'LT')):
     #print "InitTurnout" , x
     initTurnout(x)
     time.sleep(0.02)
     

for x in sensors.getSystemNameList().toArray() :
  #print "InitSensor" , x
  if x not in ['IS001']:
     initSensor(x)
     time.sleep(0.02)
  
