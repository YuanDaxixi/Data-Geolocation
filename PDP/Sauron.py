import socket
from sockaddr import query_port, query_ip
from client import set_client
from user import pdp_setup, request_serve

if __name__ == '__main__':
    shire = query_ip('Baggins') # the bravest hobbits living shire
    Witch_King = (query_ip('Witch_King'), query_port('frs')) # witch-King of Angmar, the lead of Nazgul, the most powerful servant of Sauron
    print('1. Give Rings to Baggins.    2. Geolocate these rings.\
           3. Give up.')
    while True:
        option = raw_input('Enter: ')
        for Baggins in shire:           
            if option == '1':
            # Sauron wants to store his rings in Baggins' Bag End
                try:
                    set_client(Baggins, query_port('krs'), pdp_setup, 'Rings', 'Orcs', 4096, 0)
                except socket.error, e:
                    print 'This Baggins not at home', e
            # Sauron wants to find his rings now
            elif option == '2': 
                try:
                    set_client(Witch_King[0], Witch_King[1], request_serve, 'Rings', 'key', 'Orcs', Baggins)
                except socket.error, e:
                    print 'This Baggins has run', e
            else:
            # Sauron knows he can't see his rings anymore
                break
        raw_input('You entered a dead loop, happy?')
