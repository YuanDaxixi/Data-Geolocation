# -*- coding: utf-8 -*-
# cloud module
# created by YuanDa 2017-11

import socket, struct 

BUFF_SIZE = 4096
USER_ID = 'YuanDa'
################ Cloud Storage Service ################

def serve_user(*args):
    """ the cloud provide storage service for user, it 
        receive blocksize, blockcount then begin to receive 
        the file needing stored, once user sending 'Done',
        cloud reply 'All Received', and connection completed
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
    fileinfo_size = struct.calcsize('128sL')
    file_info = user_sock.recv(fileinfo_size)
    file_name, file_size = struct.unpack('128sL', file_info)
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

################ Cloud Storage Service END################

################ Cloud Respond Phase ################

def retrieve_block(index, blocksize, fp):
    """return the file(pointed by fp) block according to 'index'"""
    offset = index * blocksize
    fp.seek(offset)
    block = fp.read(blocksize)
    return block