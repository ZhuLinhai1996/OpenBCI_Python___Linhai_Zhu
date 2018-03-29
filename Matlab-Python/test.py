import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_v3 as bci
import os
import logging
import time

def printData(whole_sample):
	#os.system('clear')
	print ("----------------")
	print("%f" %(whole_sample.id))
	print ("%.5f "%(whole_sample.channel_data[0]))
	print (whole_sample.aux_data)
	print ("----------------")



if __name__ == '__main__':
	port = '/dev/tty.usbserial-DN0096XA'
	baud = 115200
	logging.basicConfig(filename="test.log",format='%(message)s',level=logging.DEBUG)
	logging.info('---------LOG START-------------')
	#board = bci.OpenBCIBoard(port=port, scaled_output=False, log=True)
	board = bci.OpenBCIBoard(port="COM3", scaled_output=False, log=True)
	
	
	#32 bit reset
	#board.ser.write(b'v')
	#time.sleep(0.100)
	
	#connect pins to vcc
	board.ser.write(b'p')
	time.sleep(0.100)

	board.start_streaming(printData)
	#board.print_packets_in()