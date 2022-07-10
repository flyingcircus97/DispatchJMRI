# Every ReporterIcon will have its font size and colour set as  
# specified at the top of the script
#
# In addition to being a useful tool in itself, this is a good example
# of stepping through the object structure of a panel.
#
# Author: Dennis Miller
# Parts of this script are based on the ControlPanel.py 
# script written by Bob Jacobsen
#
# Part of the JMRI distribution

import jmri, java, javax.swing

import logging

class AllocateBlock(java.beans.PropertyChangeListener):

     def __init__(self, block, widget):
         self.trackWidget = [] #Initialize trackWidget list
         self.turnoutWidget = [] #Iniitialize turnoutWidget list
         self.addWidget(widget)
             
         self.block = block
         self.name = block.getUserName()
         self.allocated = None
         #self.listen = AllocateBlockListener()
         self.blockSensor = self.block.getSensor()
         if self.blockSensor: self.block.getSensor().addPropertyChangeListener(self)
         
     def addWidget(self, widget):
         #Used to add multiple track segments to the same "block"
         if (isinstance(widget, jmri.jmrit.display.IndicatorTrackIcon)):
            self.trackWidget.append(widget)
         else: #IndicatorTurnoutIcon
            self.turnoutWidget.append(widget)


     def setAllocated(self, signalName, direction):
         self.allocated = signalName
         logging.info("Allocated Block %s by signal - %s", self.name, signalName)
         #Allocate all Track Segments (turn green)
         #Invert Direction for special case - Needed for Helix to show correct on panel for direction arrow
         if (self.name in ['Block 79', 'Block 146']) and ('HEL' in signalName):
            direction = not direction
            
         for widget in self.trackWidget:
             if direction:
                widget.displayState("PositionTrack")
             else:
                widget.displayState("AllocatedTrack")
         #Allocate all Turnouts (turn green)
         for widget in self.turnoutWidget:
             #print widget.getDegrees() 
             if direction == (widget.getDegrees()==0):
                widget.setIcon(widget.getIcon("PositionTrack",widget.getTurnout().getKnownState()))
             else:
                widget.setIcon(widget.getIcon("AllocatedTrack",widget.getTurnout().getKnownState()))

         

     def deAllocated(self):
         self.allocated = None
         for widget in self.trackWidget:
             widget.displayState(widget.getStatus())
         for widget in self.turnoutWidget:
             widget.displayState(widget.getTurnout().getKnownState())
         logging.info("DeAllocated Block %s ", self.name)

     def isAllocated(self):
         return self.allocated

     def isOccupied(self):
         return self.blockSensor.getKnownState() == 2 #Occupied  

     def propertyChange(self, event):
        if event.propertyName == "KnownState":
            if event.newValue == 2: #Occuiped
                   # self.allocated = None
                   # print "DeAllocated", self.block.getUserName()
                   pass
   
     def done(self):
         if self.block:
            self.deAllocated()
            if self.block.getSensor():
                self.block.getSensor().removePropertyChangeListener(self)
        


def loadWidgets():
    widget_list = []
    signal_list = {}
    turnout_list = {}
    l = jmri.jmrit.display.PanelMenu.instance().getEditorPanelList()
    #print l
    for i in l:
       if (isinstance(i, jmri.jmrit.display.controlPanelEditor.ControlPanelEditor)):
           #pane = i.getComponents()[0]
           #jpanel = pane.getComponents()[0]
           #next = jpanel.getComponents()[0]
           panel = i.getFrame()
           root = panel.getComponents()[0]
           pane = root.getComponents()[1]
           jpanel = pane.getComponents()[0]
           jpanel2 = jpanel.getComponents()[0]
           scrollpane = jpanel2.getComponents()[0]
           viewport = scrollpane.getComponents()[0]
           widgets = viewport.getComponents()
           #print widgets
           for widget in widgets:
                if (isinstance(widget, jmri.jmrit.display.IndicatorTrackIcon)):
                
                        widget_list.append(widget) 
                 #widget.displayState("AllocatedTrack")
                 #print widget.getOccSensor()
                elif (isinstance(widget, jmri.jmrit.display.IndicatorTurnoutIcon)):
                        widget_list.append(widget) 
                        #Add to turnout list
                        turnout_name = widget.getTurnout().getUserName()
                        #print 'Turnout List Add', turnout_name
                        sensor_name = widget.getOccSensor().getUserName()
                        #print 'Sensor', sensor_name
                        if turnout_name not in ['MDT-2']: #Disable MDT-2 Only
                            if turnout_name in turnout_list:
                                turnout_list[turnout_name].append(sensor_name)
                            else: turnout_list[turnout_name] = [sensor_name]

                         #widget.setIcon(widget.getIcon("AllocatedTrack",widget.getTurnout().getKnownState()))

                elif (isinstance(widget, jmri.jmrit.display.SignalMastIcon)):
                        
                        name = widget.getSignalMast().getUserName()
                        #if name not in ['SGN-4N','MDT-2_A']: #Remove signals down mountain from Elkhorn leave ABS always even in dispatch mode.
                        signal_list[name] = widget
                        

    return widget_list, turnout_list, signal_list

def createBlocks(widgets):
    
    blocklist= blocks.getSystemNameArray()
    for name in blocklist:
        block = blocks.getBySystemName(name)
        sens = block.getSensor() 
        for widget in widgets:
            if widget.getOccSensor() == sens:
               #print "MATCH", block.getUserName(), sens
               #Create Block
               if block.getUserName() not in block_dict.keys():
                    block_dict[block.getUserName()] = AllocateBlock(block, widget)
               else:
                    block_dict[block.getUserName()].addWidget(widget)

def blocksDone():
    for block in block_dict:
       block_dict[block].done()
       logging.debug('Remove Listener to Block: %r', block)
logging.info("Start ITrackControl.py")
block_dict = {}
widgets, turnout_list, signalMast_list = loadWidgets()
createBlocks(widgets)
#print block_dict


