from client import set_client
from user import pdp_setup, request_serve

Baggins = ('115.28.188.42', 7777) # the bravest hobbits
witch_King = ('127.0.0.1', 8888) # witch-King of Angmar, the lead of Nazgul, the most powerful servant of Sauron

print('1. Give Rings to Baggins.    2. Geolocate these rings.\
       3. Give up.')
while True:
    option = raw_input('Enter: ')
    if option == '1':
        # Sauron wants to store his rings in Baggins' Bag End 
        set_client(Baggins[0], Baggins[1], pdp_setup, 'Rings', 'Orcs', 4096, 0)
        # Sauron wants to find his rings now
    elif option == '2': 
        set_client(witch_King[0], witch_King[1], request_serve, 'Rings', 'key', 'Orcs')
    else:
        # Sauron knows he can't see his rings anymore
        raw_input('Enter any key to continue.')
        break
