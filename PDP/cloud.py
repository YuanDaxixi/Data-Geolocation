# -*- coding: utf-8 -*-
# cloud module
# created by YuanDa 2017-11

import socket, struct 
from str2num import *

BUFF_SIZE = 4096
USER_ID = 'YuanDa'
FILE_NAME = '128s'

################ Cloud Storage Service ################

def serve_user(*args):
    """ the cloud provide storage service for user, it 
        receive blocksize, blockcount then begin to receive 
        the file needing stored, once user sending 'Done',
        cloud reply 'All Received', and connection completed
        invoked by cloud<->user server
    whisper -- just a string, no use so far
    user_sock -- socket
    """
    whisper, user_sock = args # interface between cloud and server
    try:
        user_id = authenticate(user_sock)
    except:
        print 'Error while authenticating.'
    try:
        receive_and_store(user_id, user_sock)
    except IOError, e:
        print 'Error while receiving/storing file.', e
    try:
        say_goodbye(user_sock)
    except socket.error, e:
        print 'Error while saying goodbye.\n', e

def authenticate(user_sock):
    """ authenticate the user's identity, return user ID
        customize when needed
    user_sock -- socket
    """
    return USER_ID

def receive_and_store(user_id, user_sock):
    """ cloud receive the file and store it
        cloud need give a good name to the file
    user-id -- user ID
    user_sock -- socket
    """
    # 128 bytes for file name, 4 bytes for file size
    fileinfo_size = struct.calcsize(FILE_NAME+'I')
    file_info = user_sock.recv(fileinfo_size)
    file_name, file_size = struct.unpack(FILE_NAME+'I', file_info)
    new_name = name_file(user_id, file_name.strip('\00'))
    received = 0
    # receive the file
    with open(new_name, 'wb') as fp:
        while(received < file_size):
            unreceived = file_size - received
            if unreceived >= BUFF_SIZE:
                buf = user_sock.recv(BUFF_SIZE)
            else:
                buf = user_sock.recv(unreceived)
            received += len(buf)
            fp.write(buf)

            #print received
        # flush block_buff if not full at last tranfer

def name_file(user_id, file_name):
    """ give a good name to the file """
    return user_id + '-' + file_name

def say_goodbye(user_sock):
    say_goodbye = user_sock.recv(1024)
    if say_goodbye == 'Done':
        user_sock.send('All Received!')
    print 'Connection %s closed' % user_sock.getsockname()[0]
    user_sock.close()

################ Cloud Storage Service END ################

################ Cloud Respond Phase ################

def response(*args):
    """ the cloud generate proofs and send them to landmarks it need
        receive file name, blocksize, block index from landmarks,
        then read the corresponding blocks and transfer them.
        invoked by cloud<->landmark server
    whisper -- just a string, no use so far
    landmark -- socket
    """
    whisper, landmark = args
    try:
        gen_proof(landmark)
    except IOError, e:
        print 'Error while generating proofs', e

def gen_proof(landmark):
    file_name = landmark.recv(struct.calcsize(FILE_NAME))
    file_name = struct.unpack(FILE_NAME, file_name)[0]
    file_name = file_name.strip('\00')
    file_name = name_file(USER_ID, file_name)
    blocksize = str2ulong(landmark.recv(4))

    index = 0
    with open(file_name, 'rb') as fp:
        while True:
            index_net = landmark.recv(4)
            index = str2ulong(index_net)
            if index == 4294967295L:
                break
            block = retrieve_block(index, blocksize, fp)
            landmark.send(index_net)
            landmark.send(block)


def retrieve_block(index, blocksize, fp):
    """return the file(pointed by fp) block according to 'index'"""
    offset = index * blocksize
    fp.seek(offset)
    block = fp.read(blocksize)
    return block

################ Cloud Respond Phase END ################