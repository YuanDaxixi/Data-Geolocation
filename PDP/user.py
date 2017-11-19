# -*- coding: utf-8 -*-
# user module
# created by YuanDa 2017-11
import Crypto
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from Crypto.Random import random
import socket

TAG_LEN = 256

# PDP GenKey phase, 'mode' = 0 means symmetric key, 1 for public key
# 'key_len' is key length
def gen_key(key_len, mode = 0):
    if mode == 0:
        key = random.getrandbits(key_len)
        return (key,)
    elif mode == 1:
        pass
    else:
        print 'Wrong mode,0 or 1'
        return False

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
    if len(key) == 1 and type(key) == long:
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

# PDP Divide file F into blocks

# divide file named 'file_name' into blocks, then calculate tag
# for each block and attach tag to block, and save them in a new
# file named 'output_name';
# new file structure: block1-tag1-block2-tag2-...-blockn-tagn
# 'blocksize' is the size of the block
# 'mode' is 0 for symmtric key, 1 for public key
# the function return the key used to generate tag, or False
def gen_metadata(file_name, output_name, blocksize = 4096, mode = 0):
    tag_key = get_tag_key(gen_key(TAG_LEN))
    if not tag_key:
        print 'Failure in key generation'
        return False
    with open(file_name, 'rb') as fp_in, open(output_name, 'wb') as fp_out:
        while(True):
            block = fp_in.read(blocksize)
            if not block: break
            tag = gen_tag(block, tag_key)
            fp_out.write(block + tag)
    return tag_key

# use 'key' to generate tag for 'block'
# 'key' should be cryptografic key
# 'hash_func' is hash algorithm
# return the tag
def gen_tag(block, key, hash_func = SHA256):
    Mac = HMAC.new(tag_key, block, hash_func)
    tag = Mac.digest()
    return tag

# input file F, generate metadata, save it, and send new file to cloud
# invoked for user-cloud client 
# 'file_name' is input file F
# 'output_name' is new file
# 'blocksize' is the size of the block
# 'mode' is 0 for symmtric key, 1 for public key
# 'server_sock' is the socket
# return the key used to generate tag, or False 
def trade_cloud(*args):
    file_name, output_name, block_size, mode, server_sock = args # interface between user and client
    tag_key = gen_metadata(file_name, output_name, block_size, mode)
    if not tag_key:
        return False
    with open(output_name, 'rb') as fp:
        while(True):
            data = fp.read(block_size + TAG_LEN)
            if not data: break
            server_sock.send(data)

    server_sock.settimeout(20)
    try:
        reply = server_sock.recv()
    except socket.errno, e:
        print 'Cloud No React', e
    if reply == 'All Received!':
        print 'Everything Seems Right'
    else:
        print 'Get Wrong React From Cloud'
    return tag_key
