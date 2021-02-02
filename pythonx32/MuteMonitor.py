#!/usr/bin/python

import threading
import time
import OSC

def request_x32_to_send_change_notifications(client):
    """request_x32_to_send_change_notifications sends /xremote repeatedly to
    mixing desk to make sure changes are transmitted to our server.
    """
    while True:
        client.send(OSC.OSCMessage("/xremote"))
        time.sleep(7)

def copy_name(main_x32_address, broadcast_x32_address):
    print ("copy names from ", main_x32_address)
    print ("copy name to ", broadcast_x32_address)
    
def scan_for_mute(main_x32_address, broadcast_x32_address, filename):
    if filename is not None:
        outputfile = open(filename, "wt")
    else:
        outputfile = None

    def msgPrinter_handler(addr, tags, data, client_address):
        txt = 'OSCMessage("%s", %s)' % (addr, data)
        # print (txt)
        if "/mix/on" in addr:
            print("Mute ", "Address: ",addr, "Data: ", data)
            if "/ch" in addr:
                print ("Channel Mute activity")
                # self._client.send(OSC.OSCMessage(path, value))
                broadcast_client.send(OSC.OSCMessage(addr, data))
        elif "/config/name" in addr:
            print("Rename ", "Address: ",addr, "Data: ", data)
            if "/ch" in addr:
                print ("Channel Rename activity")
                broadcast_client.send(OSC.OSCMessage(addr, data))
        elif "/config/color" in addr:
            print("Color ", "Address: ",addr, "Data: ", data)
            if "/ch" in addr:
                print ("Channel Color activity")
                broadcast_client.send(OSC.OSCMessage(addr, data))
        else:
            print("Not a mute ", "Address: ",addr, "Data: ", data)
        if outputfile is not None:
            outputfile.write(txt + "\n")

    m_server = OSC.OSCServer(("", 10300))
    m_server.addMsgHandler("default", msgPrinter_handler)
    main_client = OSC.OSCClient(
        server=m_server)  
        
    b_server = OSC.OSCServer(("", 10301))
    # b_server.addMsgHandler("default", msgPrinter_handler)
    broadcast_client = OSC.OSCClient(
        server=b_server)  

    main_client.connect((main_x32_address, 10023))
    broadcast_client.connect((broadcast_x32_address, 10023))
    """
    OSCMessage("/ch/01/mix/on", [1]) Mute OFF
    OSCMessage("/ch/01/mix/on", [0]) Mute ON
    """

    main_thread = threading.Thread(
        target=request_x32_to_send_change_notifications, kwargs={"client": main_client})
    main_thread.start()


    m_server.serve_forever()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Dump all change/state messages from Behringer X32 mixing desk. This tool can be used to find undocumented messages.")
    parser.add_argument('--m_address', required=True,
                        help='name/ip-address of Behringer X32 mixing desk')
    parser.add_argument('--b_address', required=True,
                        help='name/ip-address of Behringer X32 mixing desk')
    parser.add_argument('--sync_names', default=False,
                        action = "store_true",
                        help='copies names from main to broadcast for channels 1-32')
    parser.add_argument('--filename', default=None,
                        help='File to write all messages to.')  

    args = parser.parse_args()

    print("App running", "Main: ", args.m_address)
    if args.sync_names == True :
        copy_name(main_x32_address=args.m_address,
                  broadcast_x32_address=args.b_address)
    
    scan_for_mute(main_x32_address=args.m_address,
                  broadcast_x32_address=args.b_address, filename=args.filename)
