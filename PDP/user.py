# -*- coding: utf-8 -*-
# user module
# created by YuanDa 2017-11

import Crypto, socket, struct, time, os
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from Crypto.Random import random
from key import gen_key, get_tag_key, store_key, retrieve_key
from str2num import *

BLOCKSIZE = 4096
TAG_LEN = SHA256.digest_size * 8
KEY_LEN = 256
BUFF_SIZE = 1024
FILE_NAME = '128s'
KEY_FILE = 'key'

################ PDP Setup Phase ################

# the number of blocks of the file expected handled
block_count = 0

def pdp_setup(*args):
    """input file F, generate metadata, save it, and send new file to cloud.
       invoked for user->cloud client.
     file_name -- input file F
     output_name -- new file store tags
     blocksize -- size(bytes) of the block
     mode -- 0 for symmtric key, 1 for public key
     server_sock -- socket
    """
    file_name, output_name, block_size, mode, server_sock = args # interface between user and client
    # generate tag and key, then store them
    try:
        gen_metadata(file_name, output_name, block_size, mode)
    except IOError, e:
        print 'Error while generating metadata:', e
    # send the file expected to store on the cloud
    try:
        sendto_cloud(file_name, block_size, server_sock)
    except IOError, e:
        print 'Error while sending data to cloud:', e
    # wait for the cloud's respond
    wait_ack(server_sock)

def sendto_cloud(file_name, blocksize, server_sock):
    """send 'file_name', file size and file named 'file_name' to the cloud(server_sock)
       128 bytes, 4 bytes for file name, file size
       blocksize bytes for block each time
    argument is same as above
    block_count -- global variable
    """
    with open(file_name, 'rb') as fp:
        # send blocksize first and the number of blocks second
        file_info = struct.pack('128sL', file_name, os.stat(file_name).st_size) # may have bug without htonl
        server_sock.send(file_info)
        #send each block one by one
        while(True):
            data = fp.read(blocksize)
            if not data: break
            server_sock.send(data)

def wait_ack(server_sock):
    """send 'Done' tell cloud no data sent any more
       and the cloud should reply 'All Received'"""
    try:
        server_sock.send('Done')
        reply = server_sock.recv(BUFF_SIZE)
    except socket.errno, e:
        print 'Cloud No React', e

    if reply == 'All Received!':
        print 'Everything Seems Right'
    else:
        print 'Get Wrong React From Cloud'

def gen_metadata(file_name, output_name, blocksize = BLOCKSIZE, mode = 0):
    """divide file named 'file_name' into blocks, then calculate tags and
       save tags in a new file named 'output_name'"""
    key = gen_key(KEY_LEN)
    tag_key = get_tag_key(key)
    if not tag_key:
        print 'Failure in key generation'
        return False
    tag_list = gen_file_tag(file_name, blocksize, tag_key)
    store_file_tag(tag_list, output_name, blocksize)
    store_key(key, KEY_FILE)

def gen_file_tag(file_name, blocksize, key, hash_func = SHA256):
    """generate the tag(list) for each block of file named 'file_name'
    'key' is the key used for tag generating"""
    global block_count 
    tag_list = []
    with open(file_name, 'rb') as fp:
        while(True):
            block = fp.read(blocksize)
            if not block: break
            tag = gen_tag(block, key, hash_func)
            tag_list.append(tag)
    block_count = len(tag_list)
    return tag_list

def store_file_tag(tag_list, output_name, blocksize):
    """store block size, tag length and all tags in file named 'output_name'
    output file structure: blocksize-TAG_LEN-tag1-tag2-...-tagn
    tag_list -- all tags in list
    """
    with open(output_name, 'wb') as fp:
        fp.write(struct.pack('i', blocksize))
        fp.write(struct.pack('i', TAG_LEN))
        for tag in tag_list:
            fp.write(tag)

def gen_tag(block, key, hash_func = SHA256):
    """generate a tag for 'block' with 'key', return the tag in bytes
    key -- cryptografic key
    hash_func -- hash algorithm
    """
    key = random.long_to_bytes(key)
    Mac = HMAC.new(key, block, hash_func)
    tag = Mac.digest()
    return tag
################ PDP Setup Phase END ################

################ Request Service ################

def request_serve(*args):
    """ request LC geolocation user's data, and wait for the result
        invoked by user<->LC client
    file_name -- the name of file to be located
    key_file -- the file storing the key
    tag_file -- the file storing blocksize, TAG_LEN and tags
    cloud_ip -- cloud ip address
    server_sock -- socket
    """
    file_name, key_file, tag_file, cloud_ip, server_sock = args
    try:
        key = get_tag_key(retrieve_key(key_file))
    except IOError, e:
        print 'Error while reading key from disk', e
    try:
        blocksize, tag_size, tag_list = read_tags(tag_file)
    except IOError, e:
        print 'Error while reading tags', e
    try:
        send_info(file_name, key, blocksize, cloud_ip, server_sock)
    except socket.error, e:
        print 'Error while sending key', e
    try:
        send_tags(tag_size, tag_list, server_sock)
    except socket.error, e:
        print 'Error while send tags', e
    try:
        wait_good_news(server_sock)
    except socket.error, e:
        print 'Oh! Worst News.\n', e

def send_info(file_name, key, blocksize, cloud_ip, server_sock):
    """ send the file name and key which generate tags to LC; 
        128 bytes for file name, 4 bytes for key-length, 32 bytes for key
        4 bytes for blocksize, and 4 bytes for cloud ip address
    file_name -- name of the file
    key -- the key mentioned above
    server_sock -- socket
    """
    key_inbytes = random.long_to_bytes(key)
    key_len = len(key_inbytes)
    file_name = struct.pack('128s', file_name)
    server_sock.send(file_name)
    server_sock.send(uint2str(key_len))
    server_sock.send(key_inbytes)
    server_sock.send(uint2str(blocksize))
    server_sock.send(ip2net(cloud_ip))

def read_tags(tag_file):
    """ read blocksize, tag_size, and tags from disk, and return them
    tag_file -- name of the file storing datas mentioned above
    """
    tag_list = []
    with open(tag_file, 'rb') as fp:
        blocksize = struct.unpack('i', fp.read(4))[0]
        tag_size = struct.unpack('i', fp.read(4))[0] / 8
        while True:
            tag = fp.read(tag_size)
            if not tag:
                break
            tag_list.append(tag)
    return (blocksize, tag_size, tag_list)

def send_tags(tag_size, tag_list, server_sock):
    """ send blocksize, tag_size and tags to LC
        4 bytes, 4 bytes for tag_size, tag_count and
        tag_size bytes for tag each time(tag_count times)
    arguments is the same as functions' above
    """
    tag_count = len(tag_list)
    server_sock.send(uint2str(tag_size))
    server_sock.send(uint2str(tag_count))
    for tag in tag_list:
        server_sock.send(tag)

def wait_good_news(server_sock):
    """ wait LC return the result of geolocation
    server_sock -- socket
    """
    server_sock.send('So, where is it?')
    good_news = server_sock.recv(BUFF_SIZE)
    print good_news
    server_sock.close()

################ Request Service END ################