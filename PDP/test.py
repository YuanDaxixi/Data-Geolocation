from client import set_client, test_func
from server import set_server
from user import pdp_setup, request_serve
from cloud import serve_user, response
from LC import locate_data
from landmark import follow_lc
#set_server('127.0.0.1', 7777, 5, serve_user, 'Hi, client') # cloud
#set_client('127.0.0.1', 7777, pdp_setup, 'in.txt', 'out.txt', 4096, 0) # user

#set_server('127.0.0.1', 8888, 5, test_func, 'Hi, client') # LC
#set_client('127.0.0.1', 8888, request_serve, 'in.txt', 'key', 'out.txt') # user

#set_server('127.0.0.1', 7777, 5, response, 'Hi, client') # cloud
#set_client('127.0.0.1', 7777, test_func, 'in.txt', 4096) # landmarks

#set_server('127.0.0.1', 8888, 5, locate_data, 'Hi, client') # LC
#set_client('127.0.0.1', 8888, request_serve, 'in.txt', 'key', 'out.txt') # user
set_server('127.0.0.1', 9999, 5, follow_lc, '127.0.0.1', 7777) # landmarks
#set_server('127.0.0.1', 7777, 5, response, 'Hi, client') # cloud