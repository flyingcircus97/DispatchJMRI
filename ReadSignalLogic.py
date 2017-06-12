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
import logging


class Listener(java.beans.PropertyChangeListener):
  def propertyChange(self, event):
    logging.debug("Read Signal Logic change %s",event.propertyName)
    logging.debug("from %r to %r", event.oldValue, event.newValue)
    logging.debug("source systemName %s", event.source.systemName)
    logging.debug("source userName %s", event.source.userName)
    if event.source.systemName[:2]=='IB' and event.propertyName == 'state' and event.newValue==2: #Block change state
       if self.parent: self.parent.eventBlock(event)  
    elif event.source.systemName[:2]=='IS' and (event.newValue==2 or event.newValue==4): #Signal Control state change if value is active
       if self.parent: self.parent.eventSignal(event)
  def setClass(self, parent):
    self.parent = parent

class signalClass(object):

    def __init__(self, signalLogic):
         self.signalLogic = signalLogic
         self.sourceMast = self.signalLogic.getSourceMast()
         self.sourceMastName = self.sourceMast.getDisplayName()
         #Control sensor - will match held status.
         self.controlUserName = self.sourceMastName + '-HOLD' #Add underscore S to find sensor name that controls signalMast on dispatcher screen
         #print self.controlUserName
         self.control = sensors.getSensor(self.controlUserName)
         self.direction = self.calcDirection()

    #Initalize singal to held
         self.signalHold()

	 #Initialize Listener 
         self.m = Listener()
         self.m.setClass(self)
    

         #Destination Masts
         self.destmasts = {}
         for destmast in self.signalLogic.getDestinationList().toArray():
            #Get mastTurnouts
            mastTurnouts = {}
            for t in self.signalLogic.getTurnouts(destmast).toArray():
                state = self.signalLogic.getTurnoutState(t, destmast)
                #print 'C_Turnout -- ', t.getUserName(), state
                mastTurnouts[t.getUserName()] = state

            #Get Sensor List
            mastSensors = {}
            for s in self.signalLogic.getSensors(destmast).toArray():
                state = self.signalLogic.getSensorState(s, destmast)
                #print 'C_Sensor -- ', s.getUserName(), state
                mastSensors[s.getUserName()] = state

            #Get Block List
            mastBlocks = {}
            for b in self.signalLogic.getBlocks(destmast).toArray():
                state = self.signalLogic.getBlockState(b, destmast)
                #print 'C_Blocks -- ', b.getUserName(), state
                mastBlocks[b.getUserName()] = state
                #Add listener to block to un allocate when block is occupied
                b.addPropertyChangeListener(self.m)
         self.destmasts[destmast.getDisplayName()] = {'turnouts': mastTurnouts, 'sensors': mastSensors, 'blocks': mastBlocks}

         self.control.addPropertyChangeListener(self.m)
         #print self.destmasts   

    def getActiveDestination(self):
        #Determins if any of the destination masts are "active", as having tunrouts and sensors matching signal logic.
        result = None
        logging.info("Source Mast - %s", self.sourceMastName)
        for destmast in self.signalLogic.getDestinationList().toArray():
            match = True #Assume match to start
            logging.debug("Checking Dest Mast - %s", destmast.getUserName())
            #Turnout Check
            for t in self.signalLogic.getTurnouts(destmast).toArray(): 
                desired_state = self.signalLogic.getTurnoutState(t, destmast)
                current_state = t.getKnownState()
                if desired_state != current_state:
                     match = False
                     logging.debug('Turnout - %s Different State %d - %d',t.getUserName(), current_state, desired_state)
                else:
                     logging.debug('Turnout - %s Correct State %d - %d',t.getUserName(), current_state, desired_state)
            #Sensor Check
            for s in self.signalLogic.getSensors(destmast).toArray():
                desired_state = self.signalLogic.getSensorState(s, destmast)
                current_state = s.getKnownState()
                if desired_state != current_state:
                     match = False
                     logging.debug('Sensor - %s Different State %d - %d', s.getUserName(), current_state, desired_state)
                else:
                     logging.debug('Sensor - %s Correct State %d - %d', s.getUserName(), current_state, desired_state)
        # Check if match 
            if match: 
                result = destmast #Assume only one matching destination with sensor / turnout combination
                logging.info('DestMast Match - %s', result.getUserName())
        #if not result: #No path found for any destination mast
         
             

        return result   

    def checkBlocks(self, destmast):
        result = []
        logging.debug("Check Blocks - %s", destmast.getUserName())
        for b in self.signalLogic.getBlocks(destmast).toArray():
           allocated = block_dict[b.getUserName()].isAllocated()
           state = b.getState()
           logging.debug("Block - %s Allocated - %r State - %r", b.getUserName(), allocated, state)
           result.append({'block': b.getUserName(), 'allocated': allocated, 'state': state})
        return result

    def checkTurnouts(self, destmast):
        result = []
        logging.debug("Check Turnouts - %s", destmast.getUserName())
        for t in self.signalLogic.getTurnouts(destmast).toArray():
           local_sensor = sensors.provideSensor(t.getUserName()+ '_LOCAL') 
           local = local_sensor.getKnownState()
           logging.debug("Turnouts - %s Local - %r", t.getUserName(), local)
           result.append({'turnout': t.getUserName(), 'local': local})
        return result

    def eventSignal(self, event):
         #Currently event possible is . Change of Signal control.. (Toggle Held / Non Held State)
         #Signal is clicked
         logging.debug('eventSignal')
         result = self.getActiveDestination() #Determine blocks and destination
         if result:
            blocks = self.checkBlocks(result)
            turnouts = self.checkTurnouts(result)
         #Signal Held and Clicked
            if self.sourceMast.getHeld() and event.newValue==2: #If signal held and newValue unheld/clear
                #If all blocks unallocated / unoccupied, and no turnouts are set to local control
                if self.blocksFree(blocks, turnouts):
                #Allocate all Blocks
                   self.blocksAllocate(blocks)
                   #Unhold (clear signal)
                   self.signalClear()
                elif (not self.blocksUnAllocated(blocks)) and self.blocksUnOccupied(blocks): #If some allocated, but all unoccupied
                   #Unallocate all blocks allocated by the signal   
                    result = self.blocksDeAllocate(blocks)
                    self.signalHold()

                    if not result: #Means atleast one block couldn't be deallocated because it was allocated by a different sourcemast
                        showErrorMessage('Unable to Allocate', 'Unable to Allocate All Blocks for %s (Some blocks allocated by different signal mast)' %self.sourceMastName)

                else:
                    self.signalHold()
                    showErrorMessage('Unable to Allocate', 'Unable to Allocate %s (Blocks not all free or Turnout in Local Mode)' %self.sourceMastName)
                    
            elif not self.sourceMast.getHeld() and event.newValue==4: #Signal Not Held and newvalue is hold/red
            
                #If blocks allocted by signal > 1 and the all blocks are unoccupied
                if (self.blocksAllocatedBySignal(blocks)>0 and self.blocksUnOccupied(blocks)):
                   #Hold Signal (Turn Red)
                   self.signalHold()
                   #DeAllocate Blocks
                   result = self.blocksDeAllocate(blocks) 
                   if not result: #Means atleast one block couldn't be deallocated because it was allocated by a different sourcemast
                        showErrorMessage('Unable to DeAllocate', 'Unable to DeAllocate All Blocks for %s (Some blocks allocated by different signal mast)' %self.sourceMastName)
                else: #Maintain signal as cleared
                   self.signalClear()
         else: #No result found
            self.signalHold()
            if event.newValue==2: #Only show message once on switch to clear
                showInfoMessage('No Path Found', 'No Path Found for SignalMast %s' %self.sourceMastName)
                      
            
             
    
    def eventBlock(self, event):
         logging.debug('eventBlock - %s', event.source.userName)
         logging.debug('Allocated -  %r', block_dict[event.source.userName].isAllocated())
         #If block allocated by source signal then deAllocate block and hold signal
         if block_dict[event.source.userName].isAllocated() == self.sourceMastName:
                block_dict[event.source.userName].deAllocated()
                self.signalHold()


    def blocksDeAllocate(self, blocks):
        #Returns False if any of blocks to be Deallocated were allocated by different signal mast
         logging.debug('blocksDeAllocate')
         result = True #Assume DeAllocate successful
         for block in blocks:
            #If block is allocated by sourceMast then deAllocate
            if block_dict[block['block']].isAllocated() == self.sourceMastName:
                block_dict[block['block']].deAllocated()
            elif block_dict[block['block']].isAllocated():
                #If block allocated by different source signal mast
                result = False

         return result



    def blocksAllocate(self, blocks):
         logging.debug('blocksAllocate')
         for block in blocks:
             block_dict[block['block']].setAllocated(self.sourceMastName, self.direction)


    def blocksFree(self, blocks, turnout_list):
        #Checks if all blocks are unallocated
        # -- UnAllocated, UnOccupied, NotLocal Control
        #Future NotLocal
        return (self.blocksUnAllocated(blocks) and self.blocksUnOccupied(blocks) and self.turnoutsNonLocal(turnout_list))

    def blocksUnAllocated(self, blocks):
        #Checks 'if all blocks are unallocated
        # -- UnAllocated, UnOccupied, NotLocal Control
        result = True
        for block in blocks:
            if block['allocated'] != None: 
                result=False #Already Allocated
                logging.debug('Block %s is Already Allocated', block['block'])

        return result

    def blocksUnOccupied(self, blocks):
        #Checks if all blocks are occupied
        result = True
        for block in blocks:
            if block['state'] == 2:
               result=False #Occupied
               logging.debug('Block %s in Local Control', block.getUserName())
            #Future Get local controlif block['']

        return result

    def turnoutsNonLocal(self, turnout_list):
        #Checks if all turnouts are non local
        result = True
        for t in turnout_list:
            if t['local'] == 2:
                result=False #Local Control
                logging.debug('Turnout %s in Local Control', t['turnout'])

            #Future Get local controlif block['']

        return result


    def blocksAllocatedBySignal(self, blocks):
        result = 0
        for block in blocks:
            if block['allocated'] == self.sourceMastName: result+=1 

        return result

    def signalClear(self):
        self.sourceMast.setHeld(False)
        self.control.setKnownState(self.control.ACTIVE)
        logging.info('signalClear - %s', self.sourceMastName)

    def signalHold(self):
        self.sourceMast.setHeld(True)
        self.control.setKnownState(self.control.INACTIVE)
        logging.info('signalHold - %s', self.sourceMastName)
   

    def done(self): #Used to easily remove listener so code can be reloaded during testing
         logging.debug('Remove Signal Listener - %s', self.sourceMastName)
         self.control.removePropertyChangeListener(self.m)
         #Set signel back to clear
         self.signalClear()
         for destmast in self.signalLogic.getDestinationList().toArray():
            for b in self.signalLogic.getBlocks(destmast).toArray():
                b.removePropertyChangeListener(self.m)

    def calcDirection(self):
        #Determine if signal face right or left on panel
        name = self.sourceMastName
        left = False #Assume right 
        if name in signalMast_list:
            deg = signalMast_list[name].getDegrees()
            if deg == 270: left = True #Left
            if 'HEL_C' in name: #Invert if Helix C signal (Due to helix being in two spots in the panel, going opposite directions)
                left = not left 

        return left

def signalDone():
      logging.debug('Unload / Disable Signal Code')
      #print masterMastList
      for signalC in masterMastList:
          signalC.done()
          del signalC
      #masterMastList = []


mastLogic = jmri.InstanceManager.signalMastLogicManagerInstance()
#Set All Masts to Held
logging.info("Start ReadSignalLogic.py")

mastlist = masts.getSystemNameList().toArray()
mastlogiclist = mastLogic.getSignalMastLogicList().toArray()
#for x in mastlist:
#    m = masts.getBySystemName(x)
#    m.setHeld(True)
masterMastList = []
for x in mastlogiclist:
    sourcemast = x.getSourceMast().getDisplayName()
    #print sourcemast
    #if ('virtual' not in sourcemast.lower()) and (sourcemast[:3] != 'SGN'): #Don't initalize virutal mast or permissive signals
    if ('virtual' not in sourcemast.lower()): #Don't initalize virutal mast
        logging.debug('Initializing - %s', sourcemast)
        masterMastList.append(signalClass(x))
