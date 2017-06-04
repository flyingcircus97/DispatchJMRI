#Code to start dispatch control for BMRC


import jmri, java
import logging, sys

#Setup Logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
logFilename = FileUtil.getExternalFilename("scripts:jython/dispatch.log")
logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
#logging.basicConfig(filename=logFilename, filemode='w', level=logging.DEBUG, format=logFormat)
#logging.basicConfig(level=logging.DEBUG, format=logFormat)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(logFormat)
fh = logging.FileHandler(logFilename)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logFormat)
#root.addHandler(ch)
root.addHandler(fh)

logging.info('Start Dispatch code')

#Load MessageBox code
execfile(FileUtil.getExternalFilename("scripts:jython/MessageBox.py"))
#Read ITrack objects in ControlPanel
execfile(FileUtil.getExternalFilename("scripts:jython/ITrackControl.py"))
#Create Turnouts
execfile(FileUtil.getExternalFilename("scripts:jython/TurnoutControl.py"))
#Initalize Signal Logic for Dispatcher
execfile(FileUtil.getExternalFilename("scripts:jython/ReadSignalLogic.py"))
#print "Log Test"