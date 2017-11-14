# -*- coding: utf-8 -*-
# a client interface
# created by YuanDa 2017-11

import socket

def set_client(server_ip, server_port, func, *arg):
    server_addr = (server_ip, server_port)
    if not is_valid_addr(server_addr):
        print 'Please try again with a legal address'
        return False

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_addr)
    print 'Connecting to', server_ip, ':', server_port
    func((arg, s))
    s.close()
    print 'Connection closed.'
    return True

def is_valid_addr(server_addr):
    ip, port = server_addr
    try:
        socket.inet_aton(ip)
        if port >= 0 and port < 65536:
            return True
        else:
            return False
    except:
        return False

def test_func(*args):
    hello, s = args
    while(hello != '\n'):
        s.send(hello)
        data = s.recv(1024)
        print 'server told me', data
        hello = raw_input('What do you wanna tell the server?')
