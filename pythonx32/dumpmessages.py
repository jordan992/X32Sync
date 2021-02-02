#!/usr/bin/python
import OSC
import time
import threading

def request_x32_to_send_change_notifications(client):
    """request_x32_to_send_change_notifications sends /xremote repeatedly to
    mixing desk to make sure changes are transmitted to our server.
    """
    while True:
        client.send(OSC.OSCMessage("/xremote"))
        time.sleep(7)

def print_all_x32_change_messages(x32_address, server_udp_port, filename):
    if filename is not None:
        outputfile = open(filename, "wt")
    else:
        outputfile = None

    def msgPrinter_handler(addr, tags, data, client_address):
        txt = 'OSCMessage("%s", %s)' % (addr, data)
        print txt
        if outputfile is not None:
            outputfile.write(txt+"\n")

    server = OSC.OSCServer(("", server_udp_port))
    server.addMsgHandler("default", msgPrinter_handler)
    client = OSC.OSCClient(server=server) #This makes sure that client and server uses same socket. This has to be this way, as the X32 sends notifications back to same port as the /xremote message came from
    
    client.connect((x32_address, 10023))
    
    thread = threading.Thread(target=request_x32_to_send_change_notifications, kwargs = {"client": client})
    thread.start()
    server.serve_forever()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Dump all change/state messages from Behringer X32 mixing desk. This tool can be used to find undocumented messages.")
    parser.add_argument('--address', required = True,                        
                        help='name/ip-address of Behringer X32 mixing desk')
    parser.add_argument('--filename', default = None,                         
                        help='File to write all messages to.')
    parser.add_argument('--port', default = 10300,                        
                        help='UDP-port to open on this machine.')

    args = parser.parse_args()
    print_all_x32_change_messages(x32_address = args.address, server_udp_port = args.port, filename = args.filename)
    