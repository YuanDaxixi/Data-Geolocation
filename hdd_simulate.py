import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from collections import defaultdict

def read_total_time(path, filename, sector = 512, start = 512, end = 1048576):
    dic = {}
    try:
        fp = open(path + filename, 'r')
    except IOError, e:
        print 'Failing in opening %s', path + filename
        raise
    while start <= end:
        a = fp.readline()
        b = fp.readline()
        rtts = fp.readline()
        d = fp.readline()
        dic[start] = rtts.split()
        start *= 2
    return dic

def read_net_time(path, filename):
    try:
        fp = open(path + filename, 'r')
    except IOError, e:
        print 'Failing in opening %s', path + filename
        raise
    data = [line.split() for line in fp.readlines()]
    rtts = [line[0] for line in data if line[0] != 'None']
    rtts.sort()
    return rtts

def read_hdd_time(path, filename, start = 512, end = 1048576, factor = 2):
    try:
        fp = open(path + filename, 'r')
    except IOError, e:
        print 'Failing in opening %s', path + filename
        raise
    raw_data = [line.split() for line in fp.readlines()]
    dic = {}
    for line in raw_data:
        if start > end:
            print 'Error %d' % start
            break
        rtts = [round(float(rtt), 3) for rtt in line]
        rtts.sort()
        dic[start] = rtts
        start *= 2
        print 'average %f' % (sum(rtts) / len(rtts))
    return hdd_time

def gen_hdd_time(total_time, rtts):
    hdd_time = {}
    hdd_time = defaultdict(list)
    rtts.reverse()
    for blocksize, delays in total_time.iteritems():
        for delay in delays:
            for rtt in rtts:
                diff = float(delay) - float(rtt)
                if diff > 0:
                    hdd_time[blocksize].append(round(diff,3))
                    break
        print 'blocksize: %d\t avr_rtt: %f\n' % (blocksize, sum(hdd_time[blocksize]) / len(hdd_time[blocksize]))
    return hdd_time

def write_csv(hdd_time, filename, length = 300):
    for key in hdd_time.keys():
        l = len(hdd_time[key])
        if l < length:
            hdd_time[key] += [-1] * (length - l)
    output = pd.DataFrame(hdd_time)
    output.to_csv(filename, index=False)

def read_csv(path, filename):
    return pd.read_csv(path + filename)

def gen_cdf(hdd_time, blocksize):
    x_vals = sorted(list(hdd_time[blocksize]))
    y_vals = np.arange(len(x_vals)) / float(len(x_vals) - 1)
    return (x_vals, y_vals)

def gen_blocksizes(start, end, factor = 2):
    res = []
    while start <= end:
        res.append(str(start))
        start *= factor
    return res

def plot_cdf(hdd_time, blocksizes):
    plt.figure('ECS HDD RANDOM READ')
    ax = plt.gca()
    ax.set_xlabel('delay(ms)')
    ax.set_ylabel('probability')
    plt.title('CDF of hdd random read delays for different blocksizes')
    for blocksize in blocksizes:
        xy_vals = gen_cdf(hdd_time, blocksize)
        ax.plot(xy_vals[0], xy_vals[1], label=blocksize+' bytes', linewidth=1.5)
    ax.margins(0.01)
    ax.legend(loc='lower right')
    plt.show()
    return True

if __name__ == '__main__':
    #total_time = read_total_time('./', 'hdd-test-120.77.175.38 VM.txt')
    #rtts = read_net_time('./', '120.77.175.38 VM.txt')
    #hdd_time = gen_hdd_time(total_time, rtts)
    #write_csv(hdd_time, 'ecs_hdd.csv')
    hdd_time = read_csv('./', 'ecs_hdd.csv')    
    plot_cdf(hdd_time, gen_blocksizes(512, 8192, 2))

