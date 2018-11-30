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
    cut = 0
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
        if len(rtts) <= 5:
            dic[start] = [rtts[0]]
        else:
            dic[start] = rtts[cut: len(rtts) - cut]
        print 'average %f' % (sum(dic[start]) / len(dic[start]))
        start *= factor
    return dic

def gen_avr_time_report(path, prefix, mode, start = 512, end = 1048576, factor = 2):
    msb, cut = start, 0
    res = {}
    while msb <= end:
        filename = mode % (prefix, msb)
        dic = read_hdd_time(path, filename)
        res[msb] = {}
        for blocksize, rtts in dic.items():
            length = max(1, len(rtts) - cut)
            try:
                avr = sum(rtts[cut : length]) / len(rtts[cut : length])
            except Exception:
                avr = sum(rtts[0 : length]) / len(rtts[0 : length])
            res[msb][blocksize] = round(avr, 2)
        msb *= factor
    output = pd.DataFrame(res)
    filename = "%s-avr-random-read.csv" % prefix
    output.to_csv(path + filename, sep = '\t')


def gen_pdp_time_report(path, prefix, mode, start = 2, end = 10, step = 1):
    block_num, cut = start, 0
    res = {}
    while block_num <= end:
        filename = mode % (prefix, block_num)
        dic = read_hdd_time(path, filename, 512, 1048576, 2)
        res[block_num] = {}
        for blocksize, delays in dic.items():
            ecut = len(delays)
            avr = sum(delays[cut : ecut]) / len(delays[cut : ecut])
            res[block_num][blocksize] = round(avr, 2)
        block_num += step
    output = pd.DataFrame(res)
    filename = "%s-avr-random-read.csv" % prefix
    output.to_csv(path + filename, sep = '\t')


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
        hdd_time[blocksize].sort()
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
    x_vals = sorted([delay for delay in hdd_time[blocksize] if delay > 0])
    y_vals = np.arange(len(x_vals)) / float(len(x_vals) - 1)
    return (x_vals, y_vals)

def gen_blocksizes(start, end, factor = 2):
    res = []
    while start <= end:
        res.append(str(start))
        start *= factor
    return res

def plot_cdf(hdd_time, blocksizes):
    plt.figure('HDD RANDOM READ')
    ax = plt.gca()
    ax.set_xlabel('Delay(ms)')
    ax.set_ylabel('Probability')
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

    #hdd_time = read_hdd_time('./hdd-test/', 'WD-8192MB-random-read.txt')
    #write_csv(hdd_time, 'WD-hdd.csv', 300)
    #hdd_time = read_hdd_time('./hdd-test/', 'ALi-8192MB-random-read.txt')
    #write_csv(hdd_time, 'ALi-hdd.csv', 300)
    #hdd_time = read_hdd_time('./hdd-test/', 'TX-8192MB-random-read.txt')
    #write_csv(hdd_time, 'TX-hdd.csv', 300)
    #hdd_time = read_hdd_time('./hdd-test/', 'SSD-8192MB-random-read.txt')
    #write_csv(hdd_time, 'SSD-hdd.csv', 300)

    path = 'G:\\programmer yuan\\code\\self-study\\Project\\Data Geolocation\\hdd-test\\'
    #gen_avr_time_report(path, 'SSD', "%s-%dMB-random-read.txt", 1, 8192)
    gen_avr_time_report(path, 'ALi', "%s-%dMB-random-read.txt", 1, 8192)
    #gen_avr_time_report(path, 'TX', "%s-%dMB-random-read.txt", 1, 8192)
    #gen_avr_time_report(path, 'WD', "%s-%dMB-random-read.txt", 1, 8192)

    #hdd_time = read_hdd_time('./PDP/', 'WD-6-E-PDP.txt')
    #write_csv(hdd_time, 'WD-E-PDP.csv', 100)
    
    #path = 'G:\\programmer yuan\\code\\self-study\\Project\\Data Geolocation\\PDP\\'
    #gen_pdp_time_report(path, 'WD', "%s-%d-E-PDP.txt", 2, 10, step = 1)
    #gen_pdp_time_report(path, 'ALi', "%s-%d-E-PDP.txt", 2, 10, step = 1)

    #hdd_time = read_csv('./', 'WD-hdd.csv')
    #plot_cdf(hdd_time, gen_blocksizes(512, 8192, 2))
    #hdd_time = read_csv('./', 'ALi-hdd.csv')
    #plot_cdf(hdd_time, gen_blocksizes(512, 8192, 2))
    #hdd_time = read_csv('./', 'TX-hdd.csv')
    #plot_cdf(hdd_time, gen_blocksizes(512, 8192, 2))
    #hdd_time = read_csv('./', 'SSD-hdd.csv')
    #plot_cdf(hdd_time, gen_blocksizes(512, 8192, 2))

