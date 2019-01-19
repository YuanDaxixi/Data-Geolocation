# -*- coding: utf-8 -*-

# some operation requires ROOT
""" some code is Derived from ping.c distributed in Linux's netkit.
    That code is copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the US Army 
    Ballistic Research Laboratory in December, 1983 and placed in the public domain.
"""

import os, sys, time, random, socket, struct
from get_host_ip import *
from ping import Ping
from traceroute import Tracert
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r

def ip2int(ip):
    return struct.unpack('!I',socket.inet_aton(ip))[0]

def int2ip(ip):
    return socket.inet_ntoa(struct.pack('!I',ip))

class_a = (ip2int('10.0.0.0'), ip2int('10.255.255.255'))
class_b = (ip2int('172.16.0.0'), ip2int('172.31.255.255'))
class_c = (ip2int('192.168.0.0'), ip2int('192.168.255.255'))

class Inet_Detect(Ping, Tracert):
    """ This class implement some universal tools for network detection,
        including ping, traceroute, syn-scan.
    """

    SYN_SCAN = socket.IPPROTO_TCP

    def __init__(self):
        Ping.__init__(self)
        Tracert.__init__(self)
        try:
            self.syn_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.SYN_SCAN)
        except socket.error, e:
            print 'socket error:', e