#Elkhorn South Thru
#ELKSouthThru.py
#Script to set Thru Thurnout variable.

import jmri, java
import time

a = showYesNoDialog('ELK South Thru Train','Is Train coming into South Elkhorn a Thru Train?')
#print (a)
thru = turnouts.provideTurnout('LT802')
req = turnouts.provideTurnout('LT800')
#print (thru)
if a:
    thru.setCommandedState(THROWN)
else:
    thru.setCommandedState(CLOSED)
#Set Req Thrunout in Script, so it waits for end of dialog box
time.sleep(0.2)
req.setCommandedState(THROWN)