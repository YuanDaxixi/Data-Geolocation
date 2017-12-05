# -*- coding: utf-8 -*-
# created by YuanDa 2017-11

import socket, struct

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