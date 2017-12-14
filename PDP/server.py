# -*- coding: utf-8 -*-
# server interface(multithread)
# created by YuanDa 2017-11

import socket, threading, struct
from sockaddr import is_valid_addr, is_valid_client
from Crypto.Random import random
from str2num import *

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
    file_name = client.recv(struct.calcsize('128s'))
    file_name = struct.unpack('128s', file_name)[0]
    file_name = file_name.strip('\00')
    key_len = str2ulong(client.recv(4))
    key = random.bytes_to_long(client.recv(key_len))
    blocksize = str2ulong(client.recv(4))
    tag_size = str2ulong(client.recv(4))
    tag_count = str2ulong(client.recv(4))
    print key_len
    print key
    print blocksize
    print tag_size
    print tag_count

    received = 0
    total = tag_count * tag_size
    while(received < total):
        unreceived = total - received
        if unreceived >= tag_size:
            whisper = client.recv(tag_size)
        else:
            whisper = client.recv(unreceived)
            #print ('I got ' + whisper)
        received += len(whisper)

    say_goodbye = client.recv(1024)
    if say_goodbye == 'Finished':
        client.send('Good News!')
    print 'Connection %s closed' % client.getsockname()[0]
    client.close()