# -*- coding: utf-8 -*-
# user module
# created by YuanDa 2017-11

import socket, struct, timeit, random, time

def retrieve_block(index, blocksize):
    """return the file(pointed by fp) block according to 'index'"""
    a = time.clock()
    fp = open('test', 'rb')
    offset = index * blocksize
    fp.seek(offset)
    block = fp.read(blocksize)
    b = time.clock()
    print (b - a) * 1000, 'ms'
    return block

def test_time(func):
    time = timeit.timeit(func, 'from __main__ import retrieve_block')
    print time

#test_time('retrieve_block(0, 4096)')
a = time.clock()
retrieve_block(0, 4096)
b = time.clock()
print (b - a) * 1000, 'ms'