from sockaddr import get_host_ip, query_port, query_ip
from server import set_server
from landmark import follow_lc

if __name__ == '__main__':
    self_ip = get_host_ip()
    self_ip = query_ip('Nazgul')[0] # delete this line when deploy
    grs = query_port('grs')
    shire = query_ip('Baggins')
    drs = query_port('drs')
    for Baggins in shire:
        # Nazgul is to follow Witch-King's order. Chase Baggins!
        set_server(self_ip, grs, 1, follow_lc, Baggins, drs)
    raw_input('Nazgul die.')