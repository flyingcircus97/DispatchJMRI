#Elkhorn North Thru
#ElkNorthThru.py
#Script to set Thru Thurnout variable.

import jmri, java
import time

a = showYesNoDialog('ELK North Thru Train','Is Train coming into North Elkhorn a Thru Train?')
#print (a)
thru = turnouts.provideTurnout('LT805') #ELK_ENTER_THRU_N
req = turnouts.provideTurnout('LT803') #ELK_ENTER_REQ_N
#print (thru)
if a:
    thru.setCommandedState(THROWN)
else:
    thru.setCommandedState(CLOSED)
#Set Req Thrunout in Script, so it waits for end of dialog box
time.sleep(0.2)
req.setCommandedState(THROWN)