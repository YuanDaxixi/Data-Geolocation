# -*- coding: utf-8 -*-
# server interface(multithread)
# created by YuanDa 2017-11

import socket, threading, struct
from check_sockaddr import is_valid_addr
from Crypto.Random import random

def set_server(ip, port, max_client, func, *arg):
    """ a server interface providing multithreading capability
    func -- the function binding to the new thread
    arg -- passed to func in tuple whose last element is client's socket
    ip, port, max_client -- self ipv4 address, port and max client numbers 
    """
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

# just for simply testing
def test_func(*args):
    whisper, client = args
    key_len = socket.ntohl(struct.unpack('L', client.recv(4))[0])
    key = random.bytes_to_long(client.recv(key_len))
    blocksize = socket.ntohl(struct.unpack('L', client.recv(4))[0])
    tag_len = socket.ntohl(struct.unpack('L', client.recv(4))[0])
    tag_count = socket.ntohl(struct.unpack('L', client.recv(4))[0])
    print key_len
    print key
    print blocksize
    print tag_len
    print tag_count

    received = 0
    while(received < tag_count):
        try:
            whisper = client.recv(tag_len)
            #print ('I got ' + whisper)
            received += 1
        except socket.error, e:
            print 'Nothing received or nothing sent', e

    say_goodbye = client.recv(1024)
    if say_goodbye == 'Finished':
        client.send('Good News!')
    print 'Connection %s closed' % client.getsockname()[0]
    client.close()

def is_valid_client(ip):
    """customize the function if needed,
    it should check if the client connected is
    a legal one, if so, return True, else False"""
    return True