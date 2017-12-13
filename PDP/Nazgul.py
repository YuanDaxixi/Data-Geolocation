from server import set_server
from landmark import follow_lc

self = ('127.0.0.1', 9999)
Baggins = [('115.28.188.42', 7778)]

set_server(self[0], self[1], 1, follow_lc, Baggins[0], Baggins[1])
