from client import set_client
from server import set_server, test_func
from user import pdp_setup

#set_server('127.0.0.1', 8888, 10, test_func, 'Hi, client')
set_client('127.0.0.1', 8888, pdp_setup, 'in.txt', 'out.txt', 4096, 0)
