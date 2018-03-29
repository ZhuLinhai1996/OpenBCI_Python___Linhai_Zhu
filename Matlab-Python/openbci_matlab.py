#######################################################
# openbci_matlab.py
# 
# An interface to allow live streaming from the OpenBCI board
# into Matlab using Python. Python establishes an instance of 
# lab streaming layer, which is then received by a Matlab script.
# 
# For more information or troubleshooting, see README.md or 
# https://github.com/OpenBCI/OpenBCI_MATLAB
# 

import sys; sys.path.append('lib')
from pylsl import StreamInfo, StreamOutlet
import argparse
import os
import time
import string
import atexit
import threading
import sys
import open_bci_v3 as bci


class StreamerLSL():

    def __init__(self,daisy=False):
        parser = argparse.ArgumentParser(description="OpenBCI 'user'")
        parser.add_argument('-p', '--port',
                        help="Port to connect to OpenBCI Dongle " +
                        "( ex /dev/ttyUSB0 or /dev/tty.usbserial-* )")
        parser.add_argument('-d', action="store_true",
                        help="Enable Daisy Module " +
                        "-d")
        args = parser.parse_args()
        port = args.port
        print ("\n-------INSTANTIATING BOARD-------")
        self.board = bci.OpenBCIBoard(port, daisy=args.d)
        self.eeg_channels = self.board.getNbEEGChannels()
        self.aux_channels = self.board.getNbAUXChannels()
        self.sample_rate = self.board.getSampleRate()

        print('{} EEG channels and {} AUX channels at {} Hz'.format(self.eeg_channels, self.aux_channels,self.sample_rate))

    def send(self,sample):
        print(sample.channel_data)

        ##写入数据的文件名filename，限制行数count_boss
        filename = 'test.txt'
        count_boss = 10000;

        ##获取文件行数，达到 count_boss 行时，将test.txt文件清空,否则向里面写入数据
        count = -1
        for count, line in enumerate(open(r"test.txt", 'rU')):
            pass
        count += 1

        if(count >= count_boss):
            with open(filename, 'r+') as f:
                f.truncate()  # 清空文件内容

        else:
            with open(filename, 'a') as f:  # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
                f.write( str(sample.channel_data) )
                f.write("\n")

            self.outlet_eeg.push_sample(sample.channel_data)
            self.outlet_aux.push_sample(sample.aux_data)

    def create_lsl(self):
        info_eeg = StreamInfo("OpenBCI_EEG", 'EEG', self.eeg_channels, self.sample_rate,'float32',"openbci_eeg_id1");
        info_aux = StreamInfo("OpenBCI_AUX", 'AUX', self.aux_channels,self.sample_rate,'float32',"openbci_aux_id1")
        self.outlet_eeg = StreamOutlet(info_eeg)
        self.outlet_aux = StreamOutlet(info_aux)

    def cleanUp():
        board.disconnect()
        print ("Disconnecting...")
        atexit.register(cleanUp)

    def begin(self):

        print ("--------------INFO---------------")
        print ("User serial interface enabled...\n" + \
            "View command map at http://docs.openbci.com.\n" + \
            "Type /start to run -- and /stop before issuing new commands afterwards.\n" + \
            "Type /exit to exit. \n" + \
            "Board outputs are automatically printed as: \n" +  \
            "%  <tab>  message\n" + \
            "$$$ signals end of message")

        print("\n-------------BEGIN---------------")
        # Init board state
        # s: stop board streaming; v: soft reset of the 32-bit board (no effect with 8bit board)
        s = 'sv'
        # Tell the board to enable or not daisy module
        print(self.board.daisy)
        if self.board.daisy:
            s = s + 'C'
        else:
            s = s + 'c'
        # d: Channels settings back to default
        s = s + 'd'

        while(s != "/exit"):
            # Send char and wait for registers to set
            if (not s):
                pass
            elif("help" in s):
                print ("View command map at:" + \
                    "http://docs.openbci.com/software/01-OpenBCI_SDK.\n" +\
                    "For user interface: read README or view" + \
                    "https://github.com/OpenBCI/OpenBCI_Python")

            elif self.board.streaming and s != "/stop":
                print ("Error: the board is currently streaming data, please type '/stop' before issuing new commands.")
            else:
                # read silently incoming packet if set (used when stream is stopped)
                flush = False

                if('/' == s[0]):
                    s = s[1:]
                    rec = False  # current command is recognized or fot

                    if("T:" in s):
                        lapse = int(s[string.find(s, "T:")+2:])
                        rec = True
                    elif("t:" in s):
                        lapse = int(s[string.find(s, "t:")+2:])
                        rec = True
                    else:
                        lapse = -1

                    if("start" in s):
                        # start streaming in a separate thread so we could always send commands in here

                        f = open('test.txt', 'w')  # 打开文件，如果没有该文件则新建文件
                        f.truncate()  # 清空文件内容
                        f.close()  # 关闭文件

                        boardThread = threading.Thread(target=self.board.start_streaming,args=(self.send,-1))
                        boardThread.daemon = True # will stop on exit
                        try:
                            boardThread.start()
                            print("Streaming data...")
                        except:
                                raise
                        rec = True
                    elif('test' in s):
                        test = int(s[s.find("test")+4:])
                        self.board.test_signal(test)
                        rec = True
                    elif('stop' in s):
                        self.board.stop()
                        rec = True
                        flush = True
                    if rec == False:
                        print("Command not recognized...")

                elif s:
                    for c in s:
                        if sys.hexversion > 0x03000000:
                            self.board.ser.write(bytes(c, 'utf-8'))
                        else:
                            self.board.ser.write(bytes(c))
                        time.sleep(0.100)

                line = ''
                time.sleep(0.1) #Wait to see if the board has anything to report
                while self.board.ser.inWaiting():
                    c = self.board.ser.read().decode('utf-8', errors='replace')
                    line += c
                    time.sleep(0.001)
                    if (c == '\n') and not flush:
                        # print('%\t'+line[:-1])
                        line = ''

                if not flush:
                    print(line)

            # Take user input
            #s = input('--> ')
            if sys.hexversion > 0x03000000:
                s = input('--> ')
            else:
                s = raw_input('--> ')

def main():
    lsl = StreamerLSL()
    lsl.create_lsl()
    lsl.begin()

if __name__ == '__main__':
    main()