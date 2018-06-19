# -*- coding: utf-8 -*-

# requires ROOT

""" some code is Derived from ping.c distributed in Linux's netkit.
    That code is copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the US Army 
    Ballistic Research Laboratory in December, 1983 and placed in the public domain.
"""
import os, time, socket, struct, select, random

if os.name == 'nt':
    get_time = time.clock
else:
    get_time = time.time

class Ping():
    """a ping implementation"""

    ICMP_ECHO_REQUEST = 8
    PING = socket.IPPROTO_ICMP

    def __init__(self):
        try:
            self.ping_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.PING)
        except socket.error, e:
            print 'socket error:', e
        get_time()

    def ping(self, host, interval = 30, counts = 0, w = 1, timeout = 5):
        """ping the host(domin name or ipv4 address)
           <interval> is time interval between each ping,
           <counts> is the total numbers of ping
           <w> 1 means writing the result in hard disk
           <timeout> set timeout
           return a list of delays(-1 means timeout)
        """
        if w == 1:
            try:
                fp = open(host+'.txt', 'a')
            except IOError, e:
                print "Can't open", ip + '.txt\n', e 
        delays, i = [], counts
        if counts <= 0:
            i = -1
        while i != 0:
            try:
                delay = self.send_one(host, timeout)
            except socket.gaierror, e:
                print 'socket error', e

            if delay > 0:
                delays.append(delay*1000)
            else:
                delays.append(-1)
            print 'rtt:', str(delays[-1]), 'ms\n'
            if w == 1:
                fp.write(str(delays[-1]) + '\n')
            i -= 1
            time.sleep(interval)
        if w == 1:
            fp.close()
        return delays

    def send_one(self, host, timeout = 5):
        """one-time echo-reply, return something <1 if timeout"""

        #id = os.getpid() & 0xFFFF
        id = random.randint(9999,23333) # a solid id makes the os think I'm malicous

        stime = self._icmp_echo(self.ping_sock, host, id)
        etime = self._icmp_reply(self.ping_sock, id, timeout)
        return etime - stime

    def _icmp_echo(self, sock, host, id, psize = 64):
        """ pack the icmp header for ping """

        ip = socket.gethostbyname(host)
        # Remove header size from packet size
        psize = psize - 8
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        checksum = 0
        # Make a dummy header with a 0 checksum.
        header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, checksum, id, 1)
        bytes = struct.calcsize("d")
        data = (psize - bytes) * "Q"
        data = struct.pack("d", time.time()) + data

        # Calculate the checksum on the data and the dummy header.
        checksum = self._checksum(header + data)

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, socket.htons(checksum), id, 1)
        packet = header + data
        sock.sendto(packet, (ip, 1))
        return get_time()

    def _icmp_reply(self, sock, id, timeout = 5):
        """ Receive the ping from the socket."""
        time_left = timeout
        while True:
            started_select = time.time()
            what_ready = select.select([sock], [], [], time_left)
            how_long_in_select = (time.time() - started_select)
            if what_ready[0] == []: # Timeout
                self.peer_addr = None
                return -1

            time_received = get_time()
            received_packet, self.peer_addr = sock.recvfrom(1024)
            icmpHeader = received_packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmpHeader)
            if packet_id == id:
                #bytes = struct.calcsize("d")
                #time_sent = struct.unpack("d", received_packet[28:28 + bytes])[0]
                return time_received

            time_left = time_left - how_long_in_select
            if time_left <= 0:
                return -1

    def _checksum(self, source_string):
        """
        I'm not too confident that this is right but testing seems
        to suggest that it gives the same answers as in_cksum in ping.c
        """
        sum = 0
        count_to = (len(source_string) / 2) * 2
        for count in xrange(0, count_to, 2):
            this = ord(source_string[count + 1]) * 256 + ord(source_string[count])
            sum = sum + this
            sum = sum & 0xffffffff # Necessary?

        if count_to < len(source_string):
            sum = sum + ord(source_string[len(source_string) - 1])
            sum = sum & 0xffffffff # Necessary?

        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff

        # Swap bytes. Bugger me if I know why.
        answer = answer >> 8 | (answer << 8 & 0xff00)

        return answer

if __name__ == '__main__':
    p = Ping()
    rtt = p.ping('61.131.38.240', 1, 1, 0, 1)