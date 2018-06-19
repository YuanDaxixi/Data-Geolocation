# -*- coding: utf-8 -*-
# LC module
# created by YuanDa 2017-11

import socket, struct, threading
from client import set_client
from Crypto.Random import random
from str2num import *
from sockaddr import receive

geo_info = {} # record latency that each landmark gets, key is landmark's ip, value is latency
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
        and 4 bytes for cloud ip address
    return these metadata in tuple
    user_sock -- socket
    """
    file_name = receive(user_sock, struct.calcsize(FILE_NAME))
    key_len = receive(user_sock, INT_SIZE)
    key = receive(user_sock, str2uint(key_len))
    blocksize = receive(user_sock, INT_SIZE)
    cloud_ip = receive(user_sock, INT_SIZE)
    tag_size = str2uint(receive(user_sock, INT_SIZE))
    tag_count = str2uint(receive(user_sock, INT_SIZE))
    return (file_name, key_len, key, blocksize, tag_size, cloud_ip, tag_count)

def receive_tags(user_sock, tag_count, tag_size):
    """ LC receive tags from user
    user_sock -- socket
    tag_count -- total number of tags
    tag_size -- size(bytes) of each tag
    the variable 'tags' is global
    """
    global tags
    tags = []
    for i in range(tag_count):
        tags.append(receive(user_sock, tag_size))


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
    """ given geo_info, calculate the location of the data
    landmarks -- list of (ip, port) of each landmarks
    """
    global geo_info
    ips = [x[0] for x in landmarks]
    for ip in ips:
        if geo_info[ip][0] > 0:
            pass # geolocation process
        else:
            print 'Failure'
    return "Xi'an"

def reply_user(user_sock, result):
    """ send the result to user """
    say_goodbye = user_sock.recv(128)
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
    ip = landmark[0]
    port = landmark[1]
    file_name = get_file_name(metadata)
    key_len = get_key_len(metadata)
    key = get_key(metadata)
    blocksize = get_blocksize(metadata)
    tag_size = get_tag_size(metadata)
    cloud_ip = get_cloud_ip(metadata)
    nonce_count = len(nonce_list)
    
    return (ip, port, file_name, key_len, key, blocksize, tag_size, cloud_ip, nonce_count, nonce_list[:])

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
    return metadata[-1]

def get_cloud_ip(metadata):
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
    landmark_addr = (ip, port)
    landmark_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    landmark_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
    file_name, key_len, key, blocksize, tag_size, cloud_ip, nonce_count, nonce_list = args
    landmark_sock.send(file_name)
    landmark_sock.send(key_len)
    landmark_sock.send(key)
    landmark_sock.send(blocksize)
    landmark_sock.send(uint2str(tag_size))
    landmark_sock.send(cloud_ip)
    landmark_sock.send(uint2str(nonce_count))
    for index in nonce_list:
        landmark_sock.send(uint2str(index))
        tag = tags[index]
        landmark_sock.send(tag)

def wait_latency(ip, landmark_sock):
    """ LC waits for landmark replying latency, frequency, hop, city,
    then save it.
    ip -- ip address of the landmark
    landmark_sock -- socket
    """
    global geo_info
    geo_info = {}
    format = GEOINFO
    temp = receive(landmark_sock, struct.calcsize(format))
    latency, frequency, hop, city = struct.unpack(format, temp)
    geo_info[ip] = (latency, socket.ntohl(frequency), socket.ntohl(hop), city.strip('\00'))
    print latency, frequency, hop, city

################ Transmission between LC and Landmarks END ################