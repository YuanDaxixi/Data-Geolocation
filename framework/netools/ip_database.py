# -*- coding: utf-8 -*-

import sys, socket, struct, os, cPickle
reload(sys)
sys.setdefaultencoding("utf-8")

from ipip import IP

#path = u'G:\\programmer yuan\\学位论文\\data\\17monipdb\\'
IP.load(os.path.abspath("./resources/17monipdb.dat"))
#path = path + u'电信' + os.sep
#dirs = [path + name + os.sep + 'ip.txt' for name in os.listdir(path)]

def query_location(ip):
    result = IP.find(ip)
    if (result != 'N/A'):
        return result

def query_test(fn):
    with open(fn, 'a') as out_fp:
        for file in dirs:
            fp =  open(file, 'r')
            ips = fp.readlines()
            for ip in ips:
                result = IP.find(ip)
                if (result != 'N/A'):
                    out_fp.write(ip.strip() + '\t' + result + '\n')
                    print ip.strip() + result + '\n'
            fp.close()

def text2binary(fn = 'trust ip.txt'):
    """convert ip-city from text to binary(dictionary) stored on disk"""
    output_name = 'ip2city.cPickle'
    try:    
        fp = open(fn, 'r')
    except IOError, e:
        print 'Failing in opening', fn
        raise
    dic = {}
    lines = [line.split() for line in fp.readlines()]
    fp.close()
    for line in lines:
        dic[line[0]] = line[-1]
    with open(output_name, 'wb') as fp:
        cPickle.dump(dic, fp)
        print output_name, 'generated.'

def load_ip2city(fn = 'ip2city.cPickle'):
    """load ip-city dictionary, and return it"""
    try:    
        fp = open(fn, 'rb')
    except IOError, e:
        text2binary()
        raise
    dic = cPickle.load(fp)
    fp.close()
    return dic

if __name__ == '__main__':
    text2binary()
    dic = load_ip2city()
    print dic['116.255.209.251'].decode('utf-8')