# -*- coding: utf-8 -*-
# landmark module
# created by YuanDa 2017-12

import socket, struct, time, os
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from Crypto.Random import random
from client import set_client
from str2num import *
from sockaddr import get_host_ip, receive
from LC import get_tag_count, get_tag_size, get_cloud_ip
from netools import traceroute
from core_route import RouteTable

index_tag = '' # record indexes and tags received from LC
proof = '' # record proofs returned from cloud
t = [] # record latency between each challenge and response

################ Transmission between LC and Landmarks ################
def follow_lc(*args):
    """ landmark receives meta data, indexes and tags for challenging
        cloud, gets many latencies after all challenge-response, and pick
        a suitable latency which should be transferred to lc.
        invoked by LC<->landmark server
    cloud_port -- port of cloud
    lc_sock -- socket
    """
    cloud_port, lc_sock = args
    try:
        meta = receive_metadata(lc_sock)
    except socket.error, e:
        print 'Error while receiving metadata from LC', e
    try:
        receive_index_tag(get_tag_size(meta) + INT_SIZE, get_tag_count(meta), lc_sock)
    except socket.error, e:
        print 'Error while receiving indexes-tags from LC', e
    try:
        pack_index_tag(get_tag_size(meta) + INT_SIZE, get_tag_count(meta))
    except:
        print 'Error while packing'
    try:
        cloud_ip = net2ip(get_cloud_ip(meta))
        latency = challenge(cloud_ip, cloud_port, *meta)
        trace = geotrace(cloud_ip)
        geoinfo = [latency] + trace
        reply_lc(geoinfo, lc_sock)
    except socket.error, e:
        print 'Error while challenging cloud', e

def receive_metadata(lc_sock):
    """ landmark receive metadata from LC, 128 bytes for file name,
        4 bytes for key length, key_len bytes for key, 4 bytes for
        blocksize, 4 bytes for tag size, 4 bytes for tag count
    return these metadata in tuple
    lc_sock -- socket
    """
    file_name = receive(lc_sock, struct.calcsize(FILE_NAME))
    file_name = struct.unpack(FILE_NAME, file_name)[0]
    file_name = file_name.strip('\00')
    key_len = str2uint(receive(lc_sock, INT_SIZE))
    key = random.bytes_to_long(receive(lc_sock, key_len))
    blocksize = str2uint(receive(lc_sock, INT_SIZE))
    tag_size = str2uint(receive(lc_sock, INT_SIZE))
    cloud_ip = receive(lc_sock, INT_SIZE)
    tag_count = str2uint(receive(lc_sock, INT_SIZE))
    return (file_name, key_len, key, blocksize, tag_size, cloud_ip, tag_count)

def receive_index_tag(size, count, lc_sock):
    """ landmark receive the random indexes and corresponding tags from
        LC, each transfer is 36bytes(4bytes for index, 32bytes for tag),
        save these data in index_tag(a global variable)
    size -- size(bytes) of a index + tag
    count -- total number of tags(or indexes)
    lc_sock -- socket
    """
    global index_tag
    index_tag = receive(lc_sock, count * size, size)


def pack_index_tag(size, count, index_size = 4):
    """ in global variable index_tag, the data format is a string,
        this function tranformed it into a (integer, string) list, index is
        integer, tag is string.
    size -- size(bytes) of a index + tag
    count -- total number of tags(or indexes)
    index_size -- bytes of a index
    """
    global index_tag
    index_tag_list = []
    for i in xrange(count):
        start = i * size
        temp = index_tag[start:start + size]
        index = str2uint(temp[:index_size])
        tag = temp[index_size:]
        index_tag_list.append((index, tag))
    index_tag = index_tag_list

def reply_lc(geoinfo, lc_sock):
    """ landmark transfers the latency, frequency, hop, city to LC """
    latency, frequency, hop, city = geoinfo[:]
    frequency = socket.htonl(frequency)
    hop = socket.htonl(hop)
    lc_sock.send(struct.pack(GEOINFO, latency, frequency, hop, city.encode('utf-8')))
################ Transmission between LC and Landmarks END ################

################ Challenge-Response ################
def challenge(cloud_ip, cloud_port, *metadata):
    """ landmark challenges cloud with the random indexes for many times,
        which leads to many latencies, in this implementation, I just pick
        the minimal latency among them, but it's not secure.
    return the minimal latency
    file_name -- name of the file to be located
    key_len -- length of key
    key -- key for generating tags
    blocksize -- size(bytes) of block
    tag_size -- size(bytes) of tag
    count -- total number of challenges(of tags, of indexes)
    """
    file_name, key_len, key, blocksize, tag_size, no_use, count = metadata
    cloud_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cloud_sock.connect((cloud_ip, cloud_port))
    print 'Connecting to', cloud_ip, ':', cloud_port
    cloud_sock.send(struct.pack(FILE_NAME, file_name)) # cloud need know the file name
    cloud_sock.send(uint2str(blocksize)) # cloud need know the size of each block
    measure_latency(blocksize, count, cloud_sock)
    cloud_sock.send(uint2str(FINISH)) # -1 tells cloud finish
    passed = verify_proof(blocksize, key)
    latency = handle_latency(passed, cloud_ip)
    cloud_sock.close()
    print 'Connection closed.'
    return latency

def geotrace(cloud_ip, path = u'./resources/route/'):
    with open('.config', 'r') as fp:
        my_city = fp.readline().split()[-1].decode('utf-8')
        path += my_city + u'.route'
    t = traceroute.Tracert()
    trace_info = t.traceroute(cloud_ip)
    trace_info.reverse()
    if trace_info:
        route_table = RouteTable(path, my_city)
        route_table.load(path)
        for hop, trace in enumerate(trace_info):
            ip = trace[1]
            weights = route_table.weight(ip)
            if weights:
                result = list(max(weights, key = lambda x: x[1]))
                result.insert(1, hop)
                result.reverse()
                return result
    return [0, 0, NONE]

def measure_latency(blocksize, times, cloud_sock):
    """ landmark challenges cloud for many times, a challenge includes
        a index and corresponding tag; landmark maintains a timer to record
        latencies between challenges and responses
    blocksize -- size of block
    times -- times of challenges
    cloud_sock -- socket
    """
    # t used to record time, but here it is tricky. socket may not receive the
    # whole block plus the index after one transfer, so it may record several time
    # which constructs a list for a single challenge-response process, this list
    # is a element of t, that means t is list of list
    global proof, t
    proof, t = '', [] # clear them after working at last time
    buf_size = blocksize + INT_SIZE # the 4bytes is for index which cloud should reply
    total = times * buf_size
    received, i = 0, 0 
    if os.name == 'nt': # time.clock() on win32, time.time() on linux
        getime = time.clock
    else:
        getime = time.time
    getime()
    while(received < total):
        # once a whole block received, it restart the timer
        if received % buf_size == 0:       
            cloud_sock.send(uint2str(index_tag[i][0]))
            t.append([getime()])
            i += 1   
        unreceived = total - received
        if unreceived >= buf_size:
            proof += cloud_sock.recv(buf_size)
        else:
            proof += cloud_sock.recv(unreceived)
        t[i-1].append(getime())
        received = len(proof)

def verify_proof(blocksize, key, hash_func = SHA256):
    """landmark verifies whether the proof from cloud is True
    return True or False
    blocksize -- size of block
    key -- key used to generating proof(MAC)
    hash_func -- hash function
    """
    i, size = 0, blocksize + 4
    key = random.long_to_bytes(key)
    for pair in index_tag:
        temp = proof[i*size : (i+1)*size]
        index = str2uint(temp[:4])
        block = temp[4:]
        if pair[0] != index: # verify index first
            print 'Index not match!'
            return False
        else:
            Mac = HMAC.new(key, block, hash_func)
            tag = Mac.digest()
            if tag != pair[1]: # verify tag second
                print 'Bad block!'
                return False
        i += 1
    return True

def handle_latency(passed, cloud_ip):
    """ pick only one latency using some strategy, if proof
        doesn't pass verification before, return -1.0
    passed -- True for passed, False for not passed
    cloud_ip -- cloud ip address
    """
    global t
    if not passed:
        return -1.0
    report_name = get_host_ip() + '.txt'
    with open(report_name, 'a') as fp:
        fp.write('target:' + cloud_ip + '\n')
        for time_stamp in t:
            start = time_stamp[0]
            for end in time_stamp[1:]:
                latency = (end - start) * 1000
                fp.write(str(latency) + 'ms ')
                print latency, 'ms'
            fp.write('\n')
            print '--------'
    latency = min([time_stamp[1] - time_stamp[0] for time_stamp in t])
    return latency * 1000
################ Challenge-Response END ################