# -*- coding: utf-8 -*-

import socket, cPickle
from framework.netools.inet_detect import ip2int, int2ip, class_a, class_b, class_c


class RouteTable():
    """build a route table which saves the ips along the traces,
    it counts these ips' weights on cities of each target ip, e.g,
    if ip A appears in B's trace and C's trace, then ip A's weight
    on B's city and C's city are both 1."""

    def __init__(self, fn, src, begin = 8):
        self.table = {}
        self.src = src
        self.begin = begin
        self.fn = fn

    def _check_ip(self, ip):
        """return True if ip is a public ip"""
        if ip == ip2int('0.0.0.0') or \
           ip >= class_a[0] and ip <= class_a[1] or \
           ip >= class_b[0] and ip <= class_b[1] or \
           ip >= class_c[0] and ip <= class_c[1]:
            return False
        return True

    def build(self):
        """build this table, which is a dict of dict,
        first dict key is ip, second is city, value is weight"""
        try:
            fp = open(self.fn, 'r')
            self.traces = [line.split() for line in fp.readlines()]
            fp.close()
        except IOError, e:
            print e
            raise 

        for trace in self.traces:
            if len(trace) < self.begin: continue    # trace is too short
            city = trace[0].decode('utf-8')
            for idx in range(2, self.begin):
                ip = ip2int(trace[idx]) # this is source city's router)
                if city == u'郑州' or not self._check_ip(ip): continue
                if self.table.has_key(ip):
                    if self.table[ip].has_key(self.src):
                        self.table[ip][self.src] += 1
                    else:
                        self.table[ip][self.src] = 1;
                else:
                    self.table[ip] = {self.src: 1}
            # count weights on cities of each ip
            for ip in trace[self.begin: -1]:
                ip = ip2int(ip)
                if not self._check_ip(ip): continue
                if self.table.has_key(ip):
                    if self.table[ip].has_key(city):
                        self.table[ip][city] += 1
                    else:
                        self.table[ip][city] = 1
                else:
                    self.table[ip] = {city: 1}

    def store(self, fn = 'route_table.cPickle'):
        """store route table in binary on disk"""
        with open(fn, 'wb') as fp:
            cPickle.dump(self.table, fp)
        print 'The route table has been stored in file:', fn

    def load(self, fn = 'route_table.cPickle'):
        """load route table in binary from disk"""
        try:
           fp = open(fn, 'rb')
           self.table = cPickle.load(fp)
           print 'Reading completed.'
        except IOError, e:
            self.table = {}

    def visual_store(self, fn = 'route table.txt'):
        """store route table in text on disk"""
        fp = open(fn, 'w')
        for ip, dic in self.table.items():
            ip = int2ip(ip)
            fp.write('\n' + ip + '\t')
            for city, weight in dic.items():
                fp.write(city + '\t' + str(weight) + '\t')
        fp.close()

    def has_ip(self, ip):
        """return True if ip in route table"""
        ip = ip2int(ip)
        return self.table.has_key(ip)

    def weight(self, ip):
        """return weights of each city of ip, list of tuple
        [(city1, weight1), (city2, weight2), ...]"""
        if self.has_ip(ip):
            ip = ip2int(ip)
            return [item for item in self.table[ip].items()]
        else:
            return []

if __name__ == '__main__':
    lst = [u'西安', u'青岛', u'北京', u'上海', u'深圳', u'杭州', u'成都',
           u'广州', u'苏州', u'沈阳']
    begins = [8, 9, 11, 11, 11, 11, 10, 10, 11, 7]
    for i, city in enumerate(lst):
        rt = RouteTable('route\\' + city + '.txt', city, begins[i])
        rt.build()
        rt.store(city + '.route')
        rt.visual_store(city + 'route' + '.txt')
    #weights = rt.weight('2.2.0.1')
    #rt.load()
    #rt.visual_store(u'西安.txt')