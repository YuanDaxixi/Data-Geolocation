# -*- coding: utf-8 -*-
# landmark module
# created by YuanDa 2017-12

def challenge(*args):
    file_name, blocksize, server_sock = args
    nonce_list = [1, 5, 50, 500, 5000]
    file_name = struct.pack('128s', file_name)
    server_sock.send(file_name)
    server_sock.send(ulong2str(blocksize))

    buf_size = blocksize + 4
    total = len(nonce_list) * buf_size
    received = 0
    i = 0
    buf = ''
    t = []
    while(received < total):
        if received % buf_size == 0:       
            server_sock.send(ulong2str(nonce_list[i]))
            t.append([time.time()])
            i += 1   
        unreceived = total - received
        if unreceived >= buf_size:
            buf += server_sock.recv(buf_size)
        else:
            buf += server_sock.recv(unreceived)
        t[i-1].append(time.time())
        received = len(buf)

    server_sock.send(ulong2str(4294967295))
    for i in range(len(nonce_list)):
        i *= buf_size
        index, whisper = struct.unpack('L4096s', buf[i : i+buf_size])
        index = socket.ntohl(index)
        print index
    for lst in t:
        print 'latency:'
        for guy in lst:
            print guy