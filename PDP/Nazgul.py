from sockaddr import get_host_ip, query_port, query_ip
from server import set_server
from landmark import follow_lc

if __name__ == '__main__':
    self_ip = get_host_ip()
    grs = query_port('grs')
    Baggins = (query_ip('Baggins'), query_port('drs'))
    # Nazgul is to follow Witch-King's order. Chase Baggins!
    set_server(self_ip, grs, 1, follow_lc, Baggins[0], Baggins[1])
    raw_input('Nazgul die.')