# -*- coding: utf-8 -*-
# cloud module
# created by YuanDa 2017-11

import socket, struct 

def retrieve_block(index, blocksize, fp):
    """return the file(pointed by fp) block according to 'index'"""
    offset = index * blocksize
    fp.seek(offset)
    block = fp.read(blocksize)
    return block

def test_response_user(*args):
    """ just for test, the cloud receive blocksize, blockcount
    then begin to receive the file needing stored, once user sending
    'Done', cloud reply 'All Received', and connection completed
    """
    whisper, client = args
    temp = client.recv(4)
    blocksize = socket.ntohl(struct.unpack('L', temp)[0])
    temp = client.recv(4)
    blockcount = socket.ntohl(struct.unpack('L', temp)[0])

    received = 0
    while(received < blockcount):
        try:
            whisper = client.recv(blocksize)
            print ('I got ' + whisper)
            received += 1
        except socket.error, e:
            print 'Nothing received or nothing sent', e

    say_goodbye = client.recv(1024)
    if say_goodbye == 'Done':
        client.send('All Received!')
    print 'Connection %s closed' % client.getsockname()[0]
    client.close()