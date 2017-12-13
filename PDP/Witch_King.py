from server import set_server
from LC import locate_data

self = ('127.0.0.1', 8888)
Nazgul = [('127.0.0.1', 9999)] # the nine black riders owning nine rings

set_server(self[0], self[1], 1, locate_data, Nazgul)
