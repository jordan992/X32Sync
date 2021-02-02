#!/usr/bin/python

#Run command
#

import threading
import time
import argparse
import OSC
import BehringerX32




usage = "Sync Channel name, color"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('--m_address', default="192.168.1.52",                      
                        help='name/ip-address of Main Mixer')
    parser.add_argument('--b_address', default="192.168.1.53",                      
                        help='name/ip-address of Broadcast Mixer')
    parser.add_argument("-v", "--verbose", default = False, 
                        action = "store_true",
                        help="Make program output some state messages")
    parser.add_argument('--port', default = 10300,                        
                        help='UDP-port to open on this machine.')

    args = parser.parse_args()

    mixer = BehringerX32(m_address=args.m_address, b_address=args.b_address, server_port=args.port, verbose=args.verbose)
    mixer.ping()
    
    # Need to check that reciever m & b address

    # Sync Names ch 1-32
    print (mixer.get_value("/ch/01/config/name"))
    print (mixer.get_value("/ch/01/config/color"))

    # Sync Colors ch 1-32

    # Sync Gain ch 1-16


