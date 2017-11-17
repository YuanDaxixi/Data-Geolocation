# -*- coding: utf-8 -*-
# user module
# created by YuanDa 2017-11

from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from Crypto import Random

# PDP GenKey phase, mode = 0 means symmetric key, 1 for public key
# key_len is key length
def gen_key(key_len, mode = 0):
    if mode == 0:
        key = Random.random.getrandbits(key_len)
        return (key)
    elif mode == 1:
        pass
    else:
        print 'Wrong mode,0 or 1'
        return False

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

# divide the file named 'file_name' into blocks in 'blocksize' size
# return [block1, block2, ..., block] 
def divide_file(file_name, blocksize = 4096):
    with open(file_name, 'rb') as fp:
        block_list = []
        while(True):
            block = fp.read(blocksize)
            if not block:
                break
            block_list.append(block)
    return block_list[:]

# use 'key' to generate tag for 'block'
def gen_tag(block, key):
    secret_key = get_secret_key(key)
    Mac = HMAC.new(secret_key, block, SHA256)
    tag = Mac.digest() 
    return tag