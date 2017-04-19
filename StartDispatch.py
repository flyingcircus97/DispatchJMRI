#Code to start dispatch control for BMRC


import jmri, java
import logging

#Setup Logging
logFilename = FileUtil.getExternalFilename("scripts:jython/dispatch.log")
logFormat = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
logging.basicConfig(filename=logFilename, filemode='w', level=logging.DEBUG, format=logFormat)
logging.info('Start Dispatch code')

#Load MessageBox code
execfile(FileUtil.getExternalFilename("scripts:jython/MessageBox.py"))
#Read ITrack objects in ControlPanel
execfile(FileUtil.getExternalFilename("scripts:jython/ITrackControl.py"))
#Create Turnouts
execfile(FileUtil.getExternalFilename("scripts:jython/TurnoutControl.py"))
#Initalize Signal Logic for Dispatcher
execfile(FileUtil.getExternalFilename("scripts:jython/ReadSignalLogic.py"))
