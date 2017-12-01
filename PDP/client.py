# -*- coding: utf-8 -*-
# client interface(multithread)
# created by YuanDa 2017-11

import socket
from check_sockaddr import is_valid_addr

# the argument func is the function binding to the new thread
# the argument arg is passed to func in tuple type whose last
# element is client's socket
# the argument server_ip and server_port are valid ipv4 address
# and port of the server which the client gonna connect
def set_client(server_ip, server_port, func, *arg):
    server_addr = (server_ip, server_port)
    if not is_valid_addr(server_addr):
        print 'Please try again with a legal address'
        return False

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_addr)
    print 'Connecting to', server_ip, ':', server_port
    func_arg = arg + (s,)
    func(*func_arg)
    s.close()
    print 'Connection closed.'
    return True

# just for simply testing set_cliet()
def test_func(*args):
    hello, s = args
    while(hello != ''):
        s.send(hello)
        data = s.recv(1024)
        print 'server told me', data
        hello = raw_input('What do you wanna tell the server?')
