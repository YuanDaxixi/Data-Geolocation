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
    """get service port by service name bad name results in -1"""
    ports = {'krs': 7777, # keep rings service provided by Baggins
             'drs': 7778, # destroy rings service provided by Baggins
             'frs': 8888, # find rings service provided by Witch-King
             'grs': 9999} # geolocate rings service provided by Nazgul
    if service_name in ports.keys():
        return ports[service_name]
    else:
        return -1

def load_landmarks(fn = './resources/servers.txt'):
    """read the servers(landmarks) configuration files, return servers alive"""
    with open(fn, 'r') as fp:
        lines = fp.readlines()
    # line[0] is ip, line[1] is city name, line[-1] is status
    lines = [line.split() for line in lines]
    dic =  {line[0]: line[1].decode('utf-8') for line in lines if line[-1] == '1'}
    if '127.0.0.1' in dic.keys():
        self_ip = get_host_ip()
        dic[self_ip] = dic['127.0.0.1']
    return dic

def online_landmarks(fn = './resources/servers.txt'):
    """connect each landmark, if succeed, mark it 1, else 0 in <fn>"""
    with open(fn, 'r+') as fp:
        # line[0] is ip, line[1] is city name, line[-1] is status
        lines = [line.split() for line in fp.readlines()]
        dic = {line[0]: line[1] for line in lines}
        #s.settimeout(1)
        fp.seek(0)
        landmarks = []
        for ip in dic.keys():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                if ip == '127.0.0.1':
                    landmark = get_host_ip()
                else:
                    landmark = ip
                s.connect((landmark, query_port('grs')))
                status = '1'
                landmarks.append(landmark)
            except socket.error:
                status = '0'
            finally:
                s.close()
                fp.write(ip + ' ' + dic[ip] + ' ' + status + '\n')
        return landmarks

def query_ip(host_name):
    """get a host ip by given host name
       bad name results in self's ip"""
    if host_name == 'Baggins':
        return ['115.28.188.42'] # modify according to need
    elif host_name == 'Nazgul':
        return online_landmarks()
    else: # Witch_King, Sauron
        return get_host_ip()

def receive(sock, total, size = 1024):
    if size > total:
        size = total
    received, data = 0, ""
    while(received < total):
        unreceived = total - received
        if unreceived >= size:
            data += sock.recv(size)
        else:
            data += sock.recv(unreceived)
        received = len(data)
    return data

if __name__ == '__main__':
    print query_ip('Nazgul')