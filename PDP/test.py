from client import set_client
from server import set_server, test_func
from user import trade_cloud

#set_server('127.0.0.1', 8888, 10, test_func, 'Hi, client')
set_client('127.0.0.1', 8888, trade_cloud, 'in.txt', 'out.txt', 4096, 0)
