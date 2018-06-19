#-*- coding:utf-8 -*-

# 要root权限
import os, sys, socket, select, time, random, struct
from struct import *

def checksum(msg):
	s = 0
	# 每次取2个字节
	for i in range(0,len(msg),2):
		w = (ord(msg[i]) << 8) + (ord(msg[i+1]))
		s = s+w

	s = (s>>16) + (s & 0xffff)
	s = ~s & 0xffff

	return s

def CreateSocket(source_ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error, msg:
        print 'Socket create error: ',str(msg[0]),'message: ',msg[1]
        sys.exit()

    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    return s

def CreateSocket2(source_ip):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
		r = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
	except socket.error, msg:
		print 'Socket create error: ',str(msg[0]),'message: ',msg[1]
		sys.exit()

	# 设置手工提供IP头部
	s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
	r.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
	timeout = struct.pack("ll", 1, 0)
	r.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
	return s, r

# 创建IP头部
def CreateIpHeader(source_ip, dest_ip):
	packet = ''

	# ip 头部选项
	headerlen = 5
	version = 4
	tos = 0
	tot_len = 20 + 20
	id = random.randrange(18000,65535,1)
	frag_off = 0
	ttl = 255
	protocol = socket.IPPROTO_TCP
	check = 10
	saddr = socket.inet_aton ( source_ip )
	daddr = socket.inet_aton ( dest_ip )
	hl_version = (version << 4) + headerlen
	ip_header = pack('!BBHHHBBH4s4s', hl_version, tos, tot_len, id, frag_off, ttl, protocol, check, saddr, daddr)

	return ip_header

def create_tcp_syn_header(source_ip, source, dest_ip, dest_port):
	# tcp 头部选项
	seq = 0
	ack_seq = 0
	doff = 5
	# tcp flags
	fin = 0
	syn = 1
	rst = 0
	psh = 0
	ack = 0
	urg = 0
	window = socket.htons (8192)    # 最大窗口大小
	check = 0
	urg_ptr = 0
	offset_res = (doff << 4) + 0
	tcp_flags = fin + (syn<<1) + (rst<<2) + (psh<<3) + (ack<<4) + (urg<<5)
	tcp_header = pack('!HHLLBBHHH', source, dest_port, seq, ack_seq, offset_res, tcp_flags, window, check, urg_ptr)
	# 伪头部选项
	source_address = socket.inet_aton( source_ip )
	dest_address = socket.inet_aton( dest_ip )
	placeholder = 0
	protocol = socket.IPPROTO_TCP
	tcp_length = len(tcp_header)
	psh = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length);
	psh = psh + tcp_header;
	tcp_checksum = checksum(psh)

	# 重新打包TCP头部，并填充正确地校验和
	tcp_header = pack('!HHLLBBHHH', source, dest_port, seq, ack_seq, offset_res, tcp_flags, window, tcp_checksum, urg_ptr)
	return tcp_header
	
def ip_resolve(ip_header):
    if len(ip_header) < 20:
        return '0.0.0.0'
    iph = unpack('!BBHHHBBH4s4s', ip_header)
    version = iph[0] >> 4 #Versio
    ihl = iph[0] * 0xF    #IHL
    iph_length = ihl * 4  #Total Length
    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8])
    d_addr = socket.inet_ntoa(iph[9])
    return s_addr

def syn_scan2(source_ip,dest_ip,port):
	source_port = random.randrange(32000,62000,1)    # 随机化一个源端口
	s, r = CreateSocket2(source_ip)
	ip_header = CreateIpHeader(source_ip, dest_ip)
	tcp_header = create_tcp_syn_header(source_ip, source_port, dest_ip, port)
	r.bind(("", source_port))
	packet = ip_header + tcp_header
	s.sendto(packet, (dest_ip, port))
	time1 = time.time()
	try:
		data, saddr = r.recvfrom(1024)
		time2 = time.time()
	except socket.error, e:
		print e
		return -1
	ip_header_len = (ord(data[0]) & 0x0f) * 4
	tcp_header_len = (ord(data[32]) & 0xf0) >> 2
	tcp_header_ret = data[ip_header_len : ip_header_len+tcp_header_len - 1]
	if ord(tcp_header_ret[13]) == 0x12: # SYN/ACK flags
		print "SYN ACK!"
		print saddr[0], (time2 - time1) * 1000, " ms"
		return (time2 - time1) * 1000
	else:
		print saddr[0]
		return -1
		
def syn_scan(source_ip, dest_ip, port):
    source_port = random.randrange(32000,62000,1)
    my_socket = CreateSocket(source_ip)
    ip_header = CreateIpHeader(source_ip, dest_ip)
    tcp_header = create_tcp_syn_header(source_ip, source_port, dest_ip, port)
    packet = ip_header + tcp_header
    connected_ip = '0.0.0.0'
    my_socket.settimeout(1)
    my_socket.sendto(packet, (dest_ip, port))
    time1 = time.time()
    while (connected_ip != dest_ip):
        try:
            data, saddr = my_socket.recvfrom(1024)
            time2 = time.time()
            connected_ip = ip_resolve(data[0:20])
        except socket.error, e:
            print e
            return -1
    ip_header_len = (ord(data[0]) & 0x0f) * 4
    tcp_header_len = (ord(data[32]) & 0xf0) >> 2
    tcp_header_ret = data[ip_header_len : ip_header_len+tcp_header_len - 1]
    if ord(tcp_header_ret[13]) == 0x12: # SYN/ACK flags
        print "SYN ACK!"
        print saddr[0], (time2 - time1) * 1000, " ms"
        return (time2 - time1) * 1000
    else:
        print "Bad ACK!"
        return -1

if __name__ == '__main__':
    dst_addr = raw_input('ip:')
    port = raw_input('port:')
    port = int(port)
    my_ip = socket.gethostbyname(socket.gethostname())
    print 'my ip:', my_ip
    syn_scan(my_ip, dst_addr, port) 
