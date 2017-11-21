# -*- coding: utf-8 -*-
# user module
# created by YuanDa 2017-11

import Crypto
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from Crypto.Random import random
import socket, struct

BLOCKSIZE = 4096
TAG_LEN = SHA256.digest_size * 8
KEY_LEN = 256
BUFF_SIZE = 1024

################# Key Generation #################

# key generation
# 'mode' = 0 means symmetric key, 1 for public key
# 'key_len' is key length
def gen_key(key_len, mode = 0):
    if mode == 0:
        key = random.getrandbits(key_len)
        return (key,)
    elif mode == 1:
        pass
    else:
        print 'Wrong mode, 0 or 1'
        return False

# retrieve key from gen_key()
def get_tag_key(key, mode = 0):
    if mode == 0:
        tag_key = get_secret_key(key) # symmtric key implementation
    elif mode == 1:
        tag_key = get_private_key(key) # public key implementation
    else:
        print 'bad mode'
        tag_key = False
    return tag_key

def get_secret_key(key):
    if len(key) == 1 and type(key[0]) == long:
        return key[0]
    else:
        print 'illegal symmtric key'
        return False

def get_public_key(key):
    if len(key) == 2 and type(key[0]) == long:
        return key[0]
    else:
        print 'illegal public key pair'
        return False

def get_private_key(key):
    if len(key) == 2 and type(key[1]) == long:
        return key[1]
    else:
        print 'illegal public key pair'
        return False

# store the key in file named 'file_name'
def store_key(key, file_name):
    with open(file_name, 'wb') as fp:
        for item in key:
            fp.write(random.long_to_bytes(item))


################ PDP Setup Phase ################

# the number of blocks of the file expected handled
block_count = 0

# input file F, generate metadata, save it, and send new file to cloud
# invoked for user->cloud client 
# 'file_name' is input file F
# 'output_name' is new file store tags
# 'blocksize' is the size(bytes) of the block
# 'mode' is 0 for symmtric key, 1 for public key
# 'server_sock' is the socket
def pdp_setup(*args):
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

# send 'blocksize' 'block_count' and file named 'file_name' to the cloud(server_sock)
# blocksize is the size(bytes) of the block of the file
# block_count is global
def sendto_cloud(file_name, blocksize, server_sock):
    global block_count
    with open(file_name, 'rb') as fp:
        # send blocksize first and the number of blocks second
        server_sock.send(struct.pack('i', socket.htonl(blocksize)))
        server_sock.send(struct.pack('i', socket.htonl(block_count)))
        # send each block one by one
        while(True):
            data = fp.read(blocksize)
            if not data: break
            server_sock.send(data)

# send 'Done' tell cloud no data sent any more
# and the cloud should reply 'All Received'
def wait_ack(server_sock):
    try:
        server_sock.send('Done')
        reply = server_sock.recv(BUFF_SIZE)
    except socket.errno, e:
        print 'Cloud No React', e

    if reply == 'All Received!':
        print 'Everything Seems Right'
    else:
        print 'Get Wrong React From Cloud'

# divide file named 'file_name' into blocks, then calculate tags
# save tags in a new file named 'output_name'
def gen_metadata(file_name, output_name, blocksize = BLOCKSIZE, mode = 0):
    key = gen_key(KEY_LEN)
    tag_key = get_tag_key(key)
    if not tag_key:
        print 'Failure in key generation'
        return False
    tag_list = gen_file_tag(file_name, blocksize, tag_key)
    store_file_tag(tag_list, output_name, blocksize)
    store_key(key, 'key')

# generate the tag for each block of file named 'file_name'
# 'key' is the key used for tag generating
def gen_file_tag(file_name, blocksize, key, hash_func = SHA256):
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

# store block size, tag length and all tags in file named 'output_name'
# output file structure: blocksize-TAG_LEN-tag1-tag2-...-tagn
# 'tag_list' is all tags
def store_file_tag(tag_list, output_name, blocksize):
    with open(output_name, 'wb') as fp:
        fp.write(struct.pack('i', blocksize))
        fp.write(struct.pack('i', TAG_LEN))
        for tag in tag_list:
            fp.write(tag)

# generate a tag for 'block' with 'key'
# 'key' should be cryptografic key
# 'hash_func' is hash algorithm
# return the tag
def gen_tag(block, key, hash_func = SHA256):
    key = random.long_to_bytes(key)
    Mac = HMAC.new(key, block, hash_func)
    tag = Mac.digest()
    return tag
