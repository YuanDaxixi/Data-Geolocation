# -*- coding: utf-8 -*-
# created by YuanDa 2017-12
# functions only used before transfer data on network(socket)
import socket, struct

NONE = 'none'
GEOINFO = 'dII128s'
FILE_NAME = '128s'
DOUBLE = 'd'
INT = 'I'
INT_SIZE = struct.calcsize(INT)
DOUBLE_SIZE = struct.calcsize(DOUBLE)
FINISH = 4294967295

def str2uint(str):
    return socket.ntohl(struct.unpack('I', str)[0])

def str2double(str):
    return struct.unpack('d', str)[0]

def uint2str(num):
    return struct.pack('I', socket.htonl(num))

def double2str(num):
    return struct.pack('d', num)

def ip2net(str_ip):
    return socket.inet_aton(str_ip)

def net2ip(int_ip):
    return socket.inet_ntoa(int_ip)