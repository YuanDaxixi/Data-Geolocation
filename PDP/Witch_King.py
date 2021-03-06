from sockaddr import get_host_ip, query_port, query_ip
from server import set_server
from LC import locate_data

if __name__ == '__main__':
    self_ip = get_host_ip()
    self_ip = query_ip('Witch_King') # delete this line when deploy
    frs = query_port('frs')
    Nazgul_ip = query_ip('Nazgul')
    Nazgul_port = [query_port('grs')] * len(Nazgul_ip)
    Nazgul = zip(Nazgul_ip, Nazgul_port) # the nine(maybe more in cloud) black riders owning nine rings
    # Witch_King is leading Nazgul to track rings
    set_server(self_ip, frs, 1, locate_data, Nazgul)
    raw_input('Witch-King killed.')