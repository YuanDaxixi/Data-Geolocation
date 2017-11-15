# -*- coding: utf-8 -*-
# server interface(multithread)
# created by YuanDa 2017-11

import socket, threading
from check_sockaddr import is_valid_addr

# the argument func is the function binding to the new thread
# the argument arg is passed to func in tuple type whose last
# element is client's socket
# the argument ip, port, max_client are ipv4 address, port and
# max client numbers allowed to connect to this server
def set_server(ip, port, max_client, func, *arg):
    self_addr = (ip, port)
    if not is_valid_addr(self_addr):
        print 'Please try again with a legal self_addr'
        return False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(self_addr)
        s.listen(max_client)
        print 'Waiting Connection...'
    except socket.error, e:
        print 'Socket Error', e
    while(True):
        client_sock, client_ip = s.accept()
        print 'Connected by', client_ip
        if is_valid_client(client_ip):
            func_arg = arg + (client_sock,)
            new_thread = threading.Thread(target = func, args = func_arg)
            new_thread.start()
        else:
            print 'A badguy %s connected' %(client_ip)
            client_sock.close()
            continue
    s.close()
    return True

# just for simply testing set_server()
def test_func(*args):
    whisper, client = args
    while(whisper != ''):
        try:
            whisper = client.recv(1024)
            client.send('I got ' + whisper)
        except socket.error, e:
            print 'Nothing received or nothing sent', e
    print 'Connection %s closed' % client.getsockname()[0]
    client.close()

# customize the function if needed
# this function should check if the client connected
# is a legal one, if so, return True, else False
def is_valid_client(ip):
    return True