# -*- coding: utf-8 -*-
# created by YuanDa 2017-11

import socket

def is_valid_addr(server_addr):
    """check if the socket address is legal,
       legal for True otherwise False
    server_addr -- a tuple(ipv4 address, port)
    """
    ip, port = server_addr
    try:
        socket.inet_aton(ip)
        if port >= 0 and port < 65536:
            return True
        else:
            return False
    except:
        return False 

def is_valid_client(ip):
    """customize the function if needed,
    it should check if the client connected is
    a legal one, if so, return True, else False"""
    return True

def get_host_ip():
    """get self's ip address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close() 
    return ip

def query_port(service_name):
    """get service port by service name
       bad name results in -1"""
    ports = {'krs': 7777, # keep rings service provided by Baggins
             'drs': 7778, # destroy rings service provided by Baggins
             'frs': 8888, # find rings service provided by Witch-King
             'grs': 9999} # geolocate rings service provided by Nazgul
    if service_name in ports.keys():
        return ports[service_name]
    else:
        return -1

def query_ip(host_name):
    """get a host ip by given host name
       bad name results in self's ip"""
    ips = {'Baggins': ['115.28.188.42', '101.132.155.247'],
           'Nazgul': ['127.0.0.1'], # modify when deploying
           'Witch_King': '127.0.0.1',
           'Sauron': '127.0.0.1'
          }
    if host_name in ips.keys():
        return ips[host_name]
    else:
        return get_host_ip()