# -*- coding: utf-8 -*-
# key modular: key generation, store/retrieve key on/from disk, get encrypt key from key abstraction
# key abstraction: key is a tuple, whose elem should be got by the function defined below
# created by YuanDa 2017-11
from Crypto.Random import random

################# Key Generation #################

def gen_key(key_len, mode = 0):
    """ key generation, return key or False
    mode -- 0 for symmetric key, 1 for public key
    key_len -- key length(bits)
    """
    if mode == 0:
        key = random.getrandbits(key_len)
        return (key,)
    elif mode == 1:
        pass
    else:
        print 'Wrong mode, 0 or 1'
        return False

def get_tag_key(key, mode = 0):
    """retrieve key from gen_key(), return key in bytes"""
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

def store_key(key, file_name):
    """ store the key in file named 'file_name' """
    with open(file_name, 'wb') as fp:
        for item in key:
            fp.write(random.long_to_bytes(item))

def retrieve_key(file_name):
    """ read the key from the disk
    file_name -- name of file storing the key
    """
    with open(file_name, 'rb') as fp:
        key = random.bytes_to_long(fp.read())
    return (key,)