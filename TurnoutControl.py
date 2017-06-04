# BMRC Custom Dispatch
# 
# Turnout Control -- Used to provide turnout control with local control option
#

import jmri, java
import time
import logging

class Listener(java.beans.PropertyChangeListener):
  def propertyChange(self, event):
    logging.debug("Turnout Control Listener change %s",event.propertyName)
    logging.debug("from %r to %r", event.oldValue, event.newValue)
    logging.debug("source systemName %s", event.source.systemName)
    logging.debug("source userName %s", event.source.userName)
    if self.parent: self.parent.change(event)
  def setClass(self, parent):
    self.parent = parent

class turnoutClass(object):

    def __init__(self, turnoutUserName, blockList):
	 #turnoutUserName - UserName of Turnout
	 #controlUserName - UserName of Sensor that controls turnouts. (Sits on top of turnout)
	 #localUserName - Username of Sensor that controls weather turnout is in local mode or dispatch mode (Sits on top of turnout)
         logging.debug('Initalize Turnout %s with Blocks %r', turnoutUserName, blockList)
         self.turnoutUserName = turnoutUserName
         self.controlUserName = turnoutUserName + '_S'
         self.localUserName = turnoutUserName + '_LOCAL'
         self.turnout = turnouts.provideTurnout(turnoutUserName)
         self.control = sensors.provideSensor(self.controlUserName)
         self.local = sensors.provideSensor(self.localUserName)
         self.m = Listener()
         self.m.setClass(self)
         self.turnout.addPropertyChangeListener(self.m)
         self.control.addPropertyChangeListener(self.m)
         self.turnoutPos = self.turnout.getKnownState() #Initalize TurnoutPos
         
         #Block List
         self.block_list = []
         for b in blockList:
            self.block_list.append(block_dict[b])
            


    def getLocal(self):
         #Retrives state of local mode (True) or Dispatch Mode (False)
         if self.local.getKnownState()==self.local.ACTIVE: return True
         else: return False

    def getOccupiedAllocated(self):
        result = False
        for b in self.block_list:
            if b.isAllocated(): result=True
            if b.isOccupied(): result=True

        return result

    def changeTurnout(self):
         #Toggle turnout position
         if self.turnoutPos == self.turnout.CLOSED: self.turnoutPos = self.turnout.THROWN
         else: self.turnoutPos = self.turnout.CLOSED
         self.turnout.setCommandedState(self.turnoutPos)
         logging.info('Change Turnout Pos %s - %r', self.turnoutUserName, self.turnoutPos)

    def change(self, event):
         #Check to see if turnout change sensor activated to switch turnout
         if event.source.userName == self.controlUserName:
               if event.propertyName == 'KnownState':
                   if event.newValue == 2: #Active
                        self.control.setKnownState(self.control.INACTIVE)
                        if not self.getLocal() and not self.getOccupiedAllocated():
                            self.changeTurnout() #Disable switch if turnout in local control or allocated/occupied
                        else:
                            showErrorMessage('Unable to Change Turnout', 'Unable to Change Turnout %s (Turnout either occupied or in local control)' %self.turnoutUserName)
                        
         #Check to see if turnout moved
         elif event.source.userName == self.turnoutUserName:
            if event.propertyName == 'CommandedState':
                if self.getLocal(): #If local control don't worry about it, set turnoutPos variable to new value
                    self.turnoutPos = event.newValue
                    logging.info('Change Turnout by Local %s - %r', self.turnoutUserName, self.turnoutPos)
                else: #If not in local mode and new value doesn't match position of turnout then reset turnout
                    if event.newValue != self.turnoutPos:  
                        self.turnout.setCommandedState(self.turnoutPos)
                        logging.info('Change Turnout by Local OVERRIDEN %s - %r', self.turnoutUserName, self.turnoutPos)
           
    def done(self): #Used to easily remove listener so code can be reloaded during testing
         logging.debug('Remove Turnout Listener %s', self.turnoutUserName)
         self.turnout.removePropertyChangeListener(self.m)
         self.control.removePropertyChangeListener(self.m)


def turnoutsDone():
      logging.info('Unload / Disable Turnout Code')
      for t in turnoutControl:
          t.done()
          del t

#Use list from ITrackControl scan
logging.info("Start TurnoutControl.py")
#Initalize turnouts
turnoutControl = []
for turnoutName in turnout_list:
    turnoutBlocks = turnout_list[turnoutName]
    turnoutControl.append(turnoutClass(turnoutName, turnoutBlocks))
