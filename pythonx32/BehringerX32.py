#!/usr/bin/python
"""
Behringer communication 

"""

import OSC
import time
import threading
import Queue
from collections import namedtuple, OrderedDict
from x32parameters import get_settings
import json
import sys
import math

setting_paths = get_settings()

class BehringerX32(object):
    def __init__(self, m_address, b_address, server_port, verbose, timeout=1):
        self._verbose = verbose
        self._timeout = timeout
        self._server = OSC.OSCServer(("", server_port))

        self._m_client = OSC.OSCClient(server=self._server) #This makes sure that client and server uses same socket. This has to be this way, as the X32 sends notifications back to same port as the /xremote message came from
        self._b_client = OSC.OSCClient(server=self._server) #This makes sure that client and server uses same socket. This has to be this way, as the X32 sends notifications back to same port as the /xremote message came from
        
        self._m_client.connect((m_address, 10023))
        self._b_client.connect((b_address, 10023))

        self._input_queue = Queue.Queue()

    def ping(self):
        self.get_value(path="/info")
    
    def get_value(self, path):
        while True:
            try:
                self._input_queue.get_nowait()
            except Queue.Empty:
                break            
        try:
            self._m_client.send(OSC.OSCMessage(path))
            return self._input_queue.get(timeout=self._timeout).data
        except:
            while True:
                try:
                    self._input_queue.get_nowait()
                except Queue.Empty:
                    break            
            self._m_client.send(OSC.OSCMessage(path))
            return self._input_queue.get(timeout=self._timeout).data            


    def set_value(self, path, value, readback=True):
        self._b_client.send(OSC.OSCMessage(path, value))
        if readback:
            start_time = time.time()
            while True:
                read_back_value = self.get_value(path)
                #Special case for nans
                if len(value) == 1 and len(read_back_value)==1:
                    if type(value[0]) is float and math.isnan(value[0]) and math.isnan(read_back_value[0]):
                        break
                if read_back_value == value:
                    break
                if time.time() - start_time > self._timeout:
                    print("Timeout while readback of path %s, value=%s, read_back_value=%s" % (path, value, read_back_value)) 
                    break
                time.sleep(0.0001)
                
    def get_state(self):        
        state = OrderedDict()
        for index, path in enumerate(setting_paths):
            if self._verbose:
                print "Reading parameter %d of %d (%s) from x32" % (index, len(setting_paths), path)
            try:
                value = self.get_value(path)
                if self._verbose:
                    print "value returned: %s" % value
                if value:            
                    assert len(value) == 1
                    state[path] = value[0]
                    if self._verbose:
                        print "adding state: %s : %s" % (path, value[0])
            except:
                print "caught error trying to retrieve key: %s" % path

        return state
    
    def set_state(self, state):
        """Set state will first set all faders to 0, then load all values except for faders and at the end will it restore the faders.
        
        This is to avoid feedbacks/high volume during restore, if some in between setting would cause problems.
        """
        fader_keys = sorted(key for key in state if key.endswith("fader"))
        parameters = [(key, 0.0) for key in fader_keys]
        parameters.extend((key, state[key]) for key in sorted(state.iterkeys()) if key not in fader_keys)
        parameters.extend((key, state[key]) for key in fader_keys)
        
        for index, my_tuple in enumerate(parameters):
            key, value = my_tuple
            if self._verbose and index % 100 == 0:
                print "Writing parameter %d of %d to x32" % (index, len(state))
            self.set_value(path=key, value=[value], readback=True)
        return
            
    def save_state_to_file(self, outputfile, state):
        my_dict = {"x32_state": state,
                   }
        json.dump(my_dict, outputfile, indent=4)

    def read_state_from_file(self, inputfile):
        my_dict = OrderedDict(json.load(inputfile))
        return my_dict["x32_state"]
