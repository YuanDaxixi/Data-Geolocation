# -*- coding: utf-8 -*-
# LC module
# created by YuanDa 2017-11

import socket, struct, threading
from client import set_client
from Crypto.Random import random
from str2num import *

FILE_NAME = '128s'

latencies = {} # record latency that each landmark gets, key is landmark's ip, value is latency
tags = [] # record tags received from user

################ Data Geolocation Service ################

def locate_data(*args):
    """ LC receive file_name, key_len, key, blocksize, tag_size,
        tag_count and tags; Then LC arrange landmarks to challenge
        the cloud and wait for latency to be sent by landmarks;
        Finally, LC uses latency to calculate the location of data(file_name)
        and tell the user the result.
        invoked by LC<->user server
    whisper -- no use so fat
    landmarks -- a list of tuple(ip, port)
    user_sock -- socket
    """
    
    landmarks, user_sock = args
    try:
        metadata = receive_metadata(user_sock)
    except socket.error, e:
        print 'Error while receiving metadata', e
    try:
        receive_tags(user_sock, 
                        get_tag_count(metadata), 
                        get_tag_size(metadata))
    except socket.error, e:
        print 'Error while receiving tags', e
    try:
        arrange_landmarks(landmarks, *metadata)
    except socket.error, e:
        print 'Error while geolocating', e
    try:
        result = calculate_location(landmarks)
    except FloatingPointError, e:
        print 'Error while calculating location', e
    try:
        reply_user(user_sock, result)
    except socket.error, e:
        print 'Error while tell user the good news', e

def receive_metadata(user_sock):
    """ LC receive metadata from user, 128 bytes for file name,
        4 bytes for key length, key_len bytes for key, 4 bytes
        for blocksize, 4 bytes for tag size, 4 bytes for tag count
    return these metadata in tuple
    user_sock -- socket
    """
    file_name = user_sock.recv(struct.calcsize(FILE_NAME))
    key_len = user_sock.recv(4)
    key = user_sock.recv(str2ulong(key_len))
    blocksize = user_sock.recv(4)
    tag_size = str2ulong(user_sock.recv(4))
    tag_count = str2ulong(user_sock.recv(4))
    return (file_name, key_len, key, blocksize, tag_size, tag_count)

def receive_tags(user_sock, tag_count, tag_size):
    """ LC receive tags from user
    user_sock -- socket
    tag_count -- total number of tags
    tag_size -- size(bytes) of each tag
    the variable 'tags' is global
    """
    global tags
    received = 0
    total = tag_count * tag_size
    while(received < total):
        unreceived = total - received
        if unreceived >= tag_size:
            tags += user_sock.recv(tag_size)
        else:
            tags += user_sock.recv(unreceived)
        received = len(tags)

def arrange_landmarks(landmarks, *metadata):
    """ LC arrange the landmarks to challenge the cloud;
        LC need generate unique random indexes for each
        landmark, the order of challenges doesn't matter
        LC creates a thread for each landmark between itself
    landmarks -- list of (ip, port) of each landmarks
    metadata -- a tuple including many data, detail seen above
    """
    total = get_tag_count(metadata)
    nonce_list = gen_nonce_list(total, len(landmarks))
    step = len(nonce_list) // len(landmarks)
    i, arg, threads = 0, [], []
    for landmark in landmarks:
        arg.append(pack_args(landmark, nonce_list[i*step : (i+1)*step], metadata))
        new_thread = threading.Thread(target = connect_landmark, args = arg[-1])
        new_thread.start()
        threads.append(new_thread)
        i += 1
    for t in threads:
        t.join()

def calculate_location(landmarks):
    """ given latencies, calculate the location of the data
    landmarks -- list of (ip, port) of each landmarks
    """
    global latencies
    ips = [x[0] for x in landmarks]
    for ip in ips:
        if latencies[ip] > 0:
            print "Xi'an"
        else:
            print 'Failure'
    return "Xi'an"

def reply_user(user_sock, result):
    """ send the result to user """
    say_goodbye = user_sock.recv(1024)
    if say_goodbye == 'So, where is it?':
        user_sock.send(result)
    else:
        user_sock.send('Faker!')
    print 'Connection %s closed' % user_sock.getsockname()[0]

def pack_args(landmark, nonce_list, metadata):
    """ construct the arguments for landmarks generating challenges,
        return them in tuple.
    landmark -- (ip, port) of the landmark
    nonce_list -- random indexes for the landmark
    metadata -- a tuple including many data, detail seen above
    """
    file_name, key_len, key, blocksize, tag_size = metadata[0:-1]
    ip = landmark[0]
    port = landmark[1]
    file_name = get_file_name(metadata)
    key_len = get_key_len(metadata)
    key = get_key(metadata)
    blocksize = get_blocksize(metadata)
    tag_size = get_tag_size(metadata)
    nonce_count = len(nonce_list)
    
    return (ip, port, file_name, key_len, key, blocksize, tag_size, nonce_count, nonce_list[:])

def gen_nonce_list(total, landmark_num):
    """ generate random indexes for all landmarks in a big list,
        and return it. Other code should slice the big list for
        each landmark in the following steps.
    total -- total number of tags
    landmark_num -- total number of landmarks
    """
    if total > 10000:
        n = total / 2000
    elif total > 1000:
        n = total / 200
    elif total > 100:
        n = max(landmark_num, total / 20)
    else:
        n = landmark_num
    return random.sample(range(total), n)

def get_tag_count(metadata):
    return metadata[5]

def get_tag_size(metadata):
    return metadata[4]

def get_blocksize(metadata):
    return metadata[3]

def get_key(metadata):
    return metadata[2]

def get_key_len(metadata):
    return metadata[1]

def get_file_name(metadata):
    return metadata[0]

################ Data Geolocation Service END ################

################ Transmission between LC and Landmarks ################

def connect_landmark(ip, port, *args):
    """ LC send all useful data to the landmark and wait for latency
    ip -- ip address of the landmark server
    port -- port of the landmark server
    args -- file_name, key_len, key, blocksize, tag_size, nonce_count, nonce_list
            detail seen below """
    #latencies[ip] = 1.0
    landmark_addr = (ip, port)
    landmark_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    landmark_sock.connect(landmark_addr)
    print 'Connecting to', ip, ':', port

    transfer_data(landmark_sock, *args)
    wait_latency(ip, landmark_sock)

    landmark_sock.close()
    print 'Connection closed.'

def transfer_data(landmark_sock, *args):
    """ LC transfer data to landmark, data including:
    file_name -- name of the file to be located
    key_len -- length of the cipher key
    key -- the key used to generate tags
    blocksize -- size(bytes) of file block
    tag_size -- size(bytes) of tag 
    nonce_count -- total number of nonce(index)
    nonce_list -- list of the nonce(index)
    tags -- global, list of character
    """
    global tags
    file_name, key_len, key, blocksize, tag_size, nonce_count, nonce_list = args
    landmark_sock.send(file_name)
    landmark_sock.send(key_len)
    landmark_sock.send(key)
    landmark_sock.send(blocksize)
    # 4 variables above are string, 2 below are usigned long
    landmark_sock.send(ulong2str(tag_size))
    landmark_sock.send(ulong2str(nonce_count))
    for index in nonce_list:
        landmark_sock.send(ulong2str(index))
        tag = tags[index*tag_size : (index+1)*tag_size]
        landmark_sock.send(''.join(tag))

def wait_latency(ip, landmark_sock):
    """ LC waits for landmark replying latency then save it
    ip -- ip address of the landmark
    landmark_sock -- socket
    """
    global latencies
    temp = landmark_sock.recv(8)
    latency = str2double(temp)
    latencies[ip] = latency
    print latency

################ Transmission between LC and Landmarks END ################