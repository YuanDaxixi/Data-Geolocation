# -*- coding: utf-8 -*-
# LC module
# created by YuanDa 2017-11

def LC(*args):
    """ just for test, LC receive key_len, key, blocksize, tag_len,
    tag_count; then begin to receive tags for verification, 
    once user sending 'Finished', LC reply 'Good News', geolocation completed
    """
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
