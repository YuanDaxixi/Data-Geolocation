# -*- coding: utf-8 -*-
# created by YuanDa 2017-11

import socket

# server_addr is a tuple(ipv4 address, port)
# this function check if the socket address
# is legal, legal for True otherwise False
def is_valid_addr(server_addr):
    ip, port = server_addr
    try:
        socket.inet_aton(ip)
        if port >= 0 and port < 65536:
            return True
        else:
            return False
    except:
        return False
