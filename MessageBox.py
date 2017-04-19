import jmri

import java
import javax.swing
import logging


# create a frame to hold the button, put button in it, and display
#f = javax.swing.JFrame("custom button")
#f.contentPane.add(b)
#f.pack()
#f.show()
def showErrorMessage(title, message):
	f = javax.swing.JOptionPane.showMessageDialog(None, message, title, javax.swing.JOptionPane.ERROR_MESSAGE)
	logging.warning('MessageBox Error %s - %s', title, message)

def showInfoMessage(title, message):
	f = javax.swing.JOptionPane.showMessageDialog(None, message, title, javax.swing.JOptionPane.INFORMATION_MESSAGE)
	logging.info('MessageBox Info %s - %s', title, message)