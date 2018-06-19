# -*- coding: utf-8 -*-

# requires ROOT

import socket, sys, time, os, struct, random
from ip_database import query_location

class Tracert():
    """invoke the besttrace/tracert to implement traceroute
    usage: user could provide other traceroute command,
    if not provided, it uses default tool on certain os"""

    def __init__(self, cmd = ''):
        if os.name == 'nt':
            self.cmd = 'tracert -w 100 -d '
        else:
            self.cmd = "./besttrace -q 1 -w 1 -an "
        if cmd:
            self.cmd = cmd
    
    def _resolve_nt(self, line):
        """resolve the tracert output on windows"""

        idx, ip = line[0], line[-1]
        rtt = []
        for field in line[1:-1]:
            if field.isdigit():
                rtt.append(int(field))
            elif field == '<1':
                rtt.append(1)
        if rtt == []:
            ip, rtt, location = '0.0.0.0', -1, '*'
        else:
            rtt = min(rtt)
            location = query_location(ip)
        return [int(idx), ip, rtt] + location.split()

    def _resolve_xnix(self, line):
        """"resolve the traceroute output on unix like"""

        idx = line[0]
        if line[1] == '*':
            return (int(idx), '0.0.0.0', -1, '*')
        ip, rtt, location = line[1], float(line[2]), line[4:] #line[3] is 'ms'
        return [int(idx), ip, rtt] + location

    def _resolve(self, info):
        """resolve traceroute output, its format is:
        [[index, ip, rtt, location1, location2,...], ...]"""

        lines = [line.strip() for line in info]
        if os.name == 'nt':
            output = [self._resolve_nt(line.split()) for line in lines if line and line[0].isdigit()]
        else:
            output = [self._resolve_xnix(line.split()) for line in lines if line and line[0].isdigit()]
        return output
        #output = []
        #for line in info:
        #    line = line.strip()
        #    if line and line[0].isdigit():
        #        temp = line.split()
        #        if os.name == 'nt':
        #            idx, rtt, ip, location = self._resolve_nt(temp)
        #        else:
        #            idx, rtt, ip, location = self._resolve_xnix(temp)
        #        output.append([idx, ip, rtt] + location.split())

    def traceroute(self, ip, para = ''):
        """traceroute the ip, para is the parameter for traceroute
        return as <_resovle> does"""
        cmd = self.cmd + para + ' ' + ip
        fp = os.popen(cmd, 'r')
        output = fp.readlines()
        fp.close()
        output = self._resolve(output)
        return output


if __name__ == '__main__':
    t = Tracert()
    info = t.traceroute("115.28.188.42")
    for line in info:
        print line[0], line[1], line[2], ' '.join(line[3:]) #hop, ip, rtt, locations...
    

#from ping import Ping, get_time
# Still can't implement properly
#class Tracert(Ping):
#    """a traceroute implementation"""
    #ttl = 1
    #TRACE_ROUTE = socket.IPPROTO_ICMP
    #ETH_P_IP = 0x800
    #ETH_P_ALL = 3

    #def __init__(self):
    #    self.ping_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.TRACE_ROUTE)
    #    self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.TRACE_ROUTE)
    #    #self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.htons(self.ETH_P_IP))
    #    #For IPv4 (address family of AF_INET), an application receives the IP header 
    #    #at the front of each received datagram regardless of the IP_HDRINCL socket option.
    #    #self.recv_sock.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
    #    #self.recv_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

    #def tracert(self, host, max_hops):
    #    ip = socket.gethostbyname(host)
    #    id = random.randint(9999, 23333)
    #    packet = self._pack_icmp_header(id)
    #    while self.ttl <= max_hops:
    #        try:
    #            self.ping_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, self.ttl)
    #            stime = self._icmp_echo(self.ping_sock, ip, id)
    #            etime = self._icmp_reply(self.recv_sock, id)
    #        except socket.error, e:
    #            print 'socket error:', e
    #        else:
    #            state = etime - stime
    #            if self.peer_addr == None:
    #                print self.ttl, ' *    *    *\n'
    #            else:
    #                print self.ttl, state, self.peer_addr[0], '\n'
    #            self.ttl += 1


    #def _pack_icmp_header(self, id, psize = 64):
    #     # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    #    checksum = 0
    #    # Make a dummy header with a 0 checksum.
    #    header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, checksum, id, 1)
    #    bytes = struct.calcsize("d")
    #    data = (psize - bytes) * "W"
    #    data = struct.pack("d", time.time()) + data

    #    # Calculate the checksum on the data and the dummy header.
    #    checksum = self._checksum(header + data)

    #    # Now that we have the right checksum, we put that in. It's just easier
    #    # to make up a new header than to stuff it into the dummy.
    #    header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, socket.htons(checksum), id, 1)
    #    packet = header + data
    #    return packet

