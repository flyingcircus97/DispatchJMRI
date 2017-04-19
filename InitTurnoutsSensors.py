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

def initTurnout(turnout):
    to = turnouts.provideTurnout(turnout)
    #to.setState(to.getKnownState())
    to.setState(2) #Mainline
    return

def initSensor(sensor):
    s = sensors.provideSensor(sensor)
    s.setKnownState(4) #4 = inactive

# invoke for all defined turnouts
for x in turnouts.getSystemNameList().toArray() :
  initTurnout(x)

for x in sensors.getSystemNameList().toArray() :
  initSensor(x)
  
