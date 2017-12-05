from client import set_client, test_func
from server import set_server
from user import pdp_setup, request_serve
from cloud import serve_user, response

#set_server('127.0.0.1', 8888, 5, serve_user, 'Hi, client')
#set_client('127.0.0.1', 8888, pdp_setup, 'in.txt', 'out.txt', 4096, 0)
#set_server('127.0.0.1', 8888, 5, test_func, 'Hi, client')
#set_client('127.0.0.1', 8888, request_serve, 'in.txt', 'key', 'out.txt')
#set_server('127.0.0.1', 8888, 5, response, 'Hi, client')
#set_client('127.0.0.1', 8888, test_func, 'in.txt', 4096)