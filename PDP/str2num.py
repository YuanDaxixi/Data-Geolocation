# -*- coding: utf-8 -*-
# created by YuanDa 2017-12
# functions only used before transfer data on network(socket)
import socket, struct

def str2ulong(str):
    return socket.ntohl(struct.unpack('L', str)[0])

def ulong2str(num):
    return struct.pack('L', socket.htonl(num))