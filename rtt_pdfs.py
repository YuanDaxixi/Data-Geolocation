# -*- coding: utf-8 -*-
# rtt probability density function database
# created by YuanDa 2017-11

import pandas
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from sklearn.neighbors import KernelDensity

class Rtt_Pdfs():
    """create a 2-d table whose indice are cities, value is pdf of their RTT"""

    def __init__(self, file_list = [], path = './rtt/'):
        """<file_list> contains a list of files which save RTTs"""
        self.files = file_list
        self.path = path
        self._extract_city()

    def _extract_city(self):
        """extract city name from file name"""
        self.cities = []
        for file in self.files:
            self.cities.append(file.split('.')[0])

    def run(self):
        """create a big 2-d table of probability distribution function of
        rtts(src_city-dst_city) by 1-d Kernel Density Estimation"""
        dic = {}
        for city in self.cities:
            dic[city] = {}
        for i, file in enumerate(self.files):
            src_city = self.cities[i]
            try:
                fp = open(self.path + file, 'r')
            except IOError, e:
                print 'Failing in opening', file
                raise
            lines = [line.split() for line in fp.readlines()]
            for line in lines:
                dst_city, rtts = line[0].decode('utf-8'), [[float(line)] for line in line[1:]]
                kde = KernelDensity(bandwidth=1).fit(rtts)
                dic[src_city][dst_city] = kde
        self.pdfs = DataFrame(dic)
        dic.clear()

    def pdf(self, column, index):
        """return pdf[column][index], which is pdf of column-index Rtts"""
        if column in self.pdfs.columns and index in self.pdfs.index:
            return self.pdfs[column][index]
        else:
            return None

    def pri_prob_log(self, src, dst, rtt):
        """return In( P(rtt|dst)) of src, None if not exists"""
        kde = self.pdf(src, dst)
        if kde == None:
            return None
        return kde.score_samples(rtt)

    def plot_pdf(self, src, dst):
        """draw the pdf picture of src-dst's rtt"""
        kde = self.pdf(src, dst)
        if kde:
            min, l, r, n, top, step = 1000, 0, 1000, 200, -9999, 2
            fig, ax = plt.subplots()
            # find a suit interval of rtt
            while l <= r:
                log_dens = kde.score_samples((l))
                if log_dens > top:
                    top = log_dens
                if min > l and log_dens > -7:
                    min = l - step;
                elif l > min and log_dens < -7:
                    break;
                l += step
            if min < 0:
                min = 0
            max, top = l, np.exp(top) + 0.1

            rtts = np.linspace(min, max, n)[:, np.newaxis]
            log_dens = kde.score_samples(rtts)
            ax.plot(rtts[:, 0], np.exp(log_dens), '-', 
                    label="kernel = '{0}'".format('gaussian'))
            ax.text(max-step, top-0.1, "N={0}".format(n))
            ax.legend(loc='upper left')
            ax.set_xlim(min, max)
            ax.set_ylim(0, top)
            plt.show()
        else:
            print 'Nothing to plot.'

    def store(self, fn = 'pdfs.pickle'):
        if not self.pdfs.empty:
            self.pdfs.to_pickle(fn)
            print 'Written to', fn
        else:
            print 'Nothing to write'

    def load(self, fn = 'pdfs.pickle'):
        self.pdfs = pandas.read_pickle(fn)
        print 'read from', fn

if __name__ == '__main__':
    files = [u'西安.rtt.txt']
    pdfs = Rtt_Pdfs(files)
    pdfs.run()
    print pdfs.pri_prob_log(u'西安', u'武汉', 50)
    print pdfs.pri_prob_log(u'西安', u'西安', 50)
    pdfs.plot_pdf(u'西安', u'拉萨')
    #pdfs.store()
    #pdfs.load()
    #print pdfs.pri_prob_log(u'西安', '220.162.197.2', 50)
    #print pdfs.pri_prob_log(u'西安', '220.162.197.555', 50)
    #pdfs.plot_pdf(u'西安', '220.162.197.2')
