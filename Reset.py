import logging

logging.info("Resetting / Disabling Dispatch Code")
try:
	signalDone()
	turnoutsDone()
	blocksDone()
except: 
	logging.info("Unable to Reset Code")

logging.info("Resetting Code Complete")
