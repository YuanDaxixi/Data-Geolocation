# -*- coding: utf-8 -*-
# server interface
# created by YuanDa 2017-11

import socket, threading
from client import is_valid_addr

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
        # is_valid_client should be defined by the caller
        if is_valid_client(client_ip):
            new_thread = threading.thread(func, (arg, client_sock))
            new_thread.start()
        else:
            print 'A badguy %s connected' %(client_ip)
            client_sock.close()
            continue
    s.close()
    return True

def test_func(*args):
    whisper, client = args
    while(whisper != '\n'):
        whisper = client.recv(1024)
        client.send('I got ' + whisper)
    client.close()

def is_valid_client(ip):
    return True