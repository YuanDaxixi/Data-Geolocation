from server import set_server
from cloud import serve_user, response

MAX_ENEMY = 10
keep_ring_service = ('115.28.188.42', 7777)
destroy_ring_service = ('115.28.188.42', 7778)

print('1. Take Rings from Sauron.    2. Take rings to escape.\
       3. Eat something.')
while True:
    option = raw_input('Enter: ')
    if option == '1':
        # Baggins store rings in Bag End 
        set_server(keep_ring_service[0], keep_ring_service[1], 1, serve_user, 'Hi, Sauron')
        # Now Baggins must escape from Shier with rings
    elif option == '2': 
        set_server(destroy_ring_service[0], destroy_ring_service[1], MAX_ENEMY, response, 'Morning, black rider')# Nazgûl(Black Riders), the terror owning the nine rings.
    else:
        # Baggins think it's food time
        raw_input('Baggins got home.')
        break