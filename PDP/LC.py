# -*- coding: utf-8 -*-
# LC module
# created by YuanDa 2017-11

import socket,struct
from Crypto.Random import random

FILE_NAME = '128s'

def LC(*args):
    """ just for test, LC receive file_name, key_len, key, blocksize,
    tag_len, tag_count; then begin to receive tags for verification,
    once user sending 'Finished', LC reply 'Good News', geolocation completed
    """
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
