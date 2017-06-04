# Sample script showing how to initialize
# turnouts based on the state of their input
# sensors (e.g. feedback)
#
# This is particularly useful for a C/MRI system, where
# the turnouts need to be set to a particular state quickly
#
#
# Part of the JMRI distribution

import jmri, java
import time

#Listner class gives ability to change turnouts when not in dispatch mode.
class Listener(java.beans.PropertyChangeListener):
  def propertyChange(self, event):
    #logging.debug("Turnout Control Listener change %s",event.propertyName)
    #logging.debug("from %r to %r", event.oldValue, event.newValue)
    #logging.debug("source systemName %s", event.source.systemName)
    #logging.debug("source userName %s", event.source.userName)
    
    if sensors.provideSensor("ISDISPATCH").getKnownState() == INACTIVE: #Make sure not in dispatch mode
      
      if event.propertyName == 'KnownState':
        if event.newValue == 2: #Active
          #Calculate turnout name as source sensor name minus last 2 characters
          turnout_name = event.source.userName[:-2]
          turnout = turnouts.provideTurnout(turnout_name)
          self.changeTurnout(turnout)

          sensors.provideSensor(event.source.systemName).setKnownState(INACTIVE) #reset control sensor to inactive

  def changeTurnout(self, turnout):
         #Toggle turnout position
         turnoutPos = turnout.getKnownState()
        
         if turnoutPos == CLOSED: 
          turnout.setCommandedState(THROWN)
         else:
          turnout.setCommandedState(CLOSED)

        
  def setClass(self, parent):
    self.parent = parent

def initTurnout(turnout):
    to = turnouts.provideTurnout(turnout)
    #to.setState(to.getKnownState())
    to.setState(2) #Mainline
    #return

def initSensor(sensor):
    s = sensors.provideSensor(sensor)
    s.setKnownState(INACTIVE) #4 = inactive
    #Add listener if sensors ends with _S (Turnout switch)
    if sensor[-2:]=='_S':
      s.addPropertyChangeListener(nonDispatchListener)


time.sleep(10)
nonDispatchListener = Listener()
# invoke for all defined turnouts
for x in turnouts.getSystemNameList().toArray() :
  if ((len(x)<= 4) and (x[:2] == 'LT')):
     #print "InitTurnout" , x
     initTurnout(x)
     #time.sleep(0.02)
     

for x in sensors.getSystemNameList().toArray() :
  #print "InitSensor" , x
  if x not in ['IS001']:
     initSensor(x)
     #time.sleep(0.02)
  
