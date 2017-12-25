# -*- coding: utf-8 -*-
# client interface
# created by YuanDa 2017-11

import socket, struct, time
from sockaddr import is_valid_addr
from str2num import *

def set_client(server_ip, server_port, func, *args):
    """ a client interface providing function by func
    func -- function the client should provide
    args -- passed to func in tuple type whose last
            element is socket
    server_ip -- ipv4 address of the server
    server_port -- port of the server
    """
    server_addr = (server_ip, server_port)
    if not is_valid_addr(server_addr):
        print 'Please try again with a legal address'
        return False

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_addr)
    print 'Connecting to', server_ip, ':', server_port
    func_arg = args + (s,)
    func(*func_arg)
    s.close()
    print 'Connection closed.'
    return True

# just for simply testing set_cliet()
def test_func(*args):
    file_name, blocksize, server_sock = args
    nonce_list = [1, 5, 50, 500, 5000]
    file_name = struct.pack('128s', file_name)
    server_sock.send(file_name)
    server_sock.send(uint2str(blocksize))

    buf_size = blocksize + 4
    total = len(nonce_list) * buf_size
    received = 0
    i = 0
    buf = ''
    t = []
    while(received < total):
        if received % buf_size == 0:       
            server_sock.send(uint2str(nonce_list[i]))
            t.append([time.time()])
            i += 1   
        unreceived = total - received
        if unreceived >= buf_size:
            buf += server_sock.recv(buf_size)
        else:
            buf += server_sock.recv(unreceived)
        t[i-1].append(time.time())
        received = len(buf)

    server_sock.send(uint2str(4294967295))
    for i in range(len(nonce_list)):
        i *= buf_size
        index, whisper = struct.unpack('L4096s', buf[i : i+buf_size])
        index = socket.ntohl(index)
        print index
    for lst in t:
        print 'latency:'
        for guy in lst:
            print guy
    
