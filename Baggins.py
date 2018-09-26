# -*- coding: utf-8 -*-

from framework.sockaddr import get_host_ip, query_port, query_ip
from framework.server import set_server
from framework.cloud import serve_user, response

MAX_ENEMY = 10

if __name__ == '__main__':
    self_ip = get_host_ip()
    import os
    #os.chdir('G:\\programmer yuan\\学位论文\\code\\the king of the ring'.decode('utf-8'))
    krs = query_port('krs')
    drs = query_port('drs')
    print('1. Take Rings from Sauron.    2. Take rings to escape.\
           3. Eat something.')
    while True:
        option = raw_input('Enter: ')
        if option == '1':
            # Baggins store rings in Bag End 
            set_server(self_ip, krs, 1, serve_user, 'Hi, Sauron')
            # Now Baggins must escape from Shier with rings
        elif option == '2': 
            set_server(self_ip, drs, MAX_ENEMY, response, 'Morning, black rider')
        else:
            # Baggins think it's food time
            raw_input('Baggins got home.')
            break