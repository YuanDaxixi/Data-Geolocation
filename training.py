# -*- coding: utf-8 -*-
# rtt probability density function database
# created by YuanDa 2017-11

import os, pandas, cPickle
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from sklearn.neighbors import KernelDensity
from collections import defaultdict

class Training():
    """create a 2-d table whose indice are cities, value is pdf of their RTT"""

    def __init__(self, path = './resources/'):
        """<file_list> contains a list of files which save RTTs"""
        self.path = path
    
    def _read(self, filename):
        """a inner interface to read cpickle object from <filename>"""
        try:
            fp = open(self.path + filename, 'rb')
        except IOError, e:
            print 'Failing in opening', filename
            raise
        res = cPickle.load(fp)
        return res

    def _write(self, obj, filename):
        """a inner interface to write cpickle object <obj> into <filename>"""
        with open(self.path + filename, 'wb') as fp:
            cPickle.dump(obj, fp)

    def gen_test(self, filename = 'Rtts.rtt'):
        """generates train data from object in <filename>"""
        rtt_map = self._read(filename)
        train_rtt = {}
        src_cities = rtt_map.keys()
        for src_city in src_cities:
            train_rtt[src_city]= {}
            for dst_city, rtts in rtt_map[src_city].items():
                rtts = [float(rtt) for rtt in rtts]
                rtts.sort()
                train_rtt[src_city][dst_city] = rtts[0::2]                
        self._write(train_rtt, 'train.rtt')


    def train(self, train_file):
        """create probability distribution function of Rtts of 
        src_city-dst_city by 1-d Kernel Density Estimation
        train_file -- file's name of training data"""
        pdfs = defaultdict(dict)
        rtt_map = self._read(train_file)
        src_cities = rtt_map.keys()
        for src_city in src_cities:
            pdfs[src_city] = {}
            for dst_city, rtts in rtt_map[src_city].items():
                dst_city, rtts = dst_city, [[float(rtt)] for rtt in rtts]
                kde = KernelDensity(bandwidth = 1).fit(rtts)
                pdfs[src_city][dst_city] = kde
        self.pdfs = DataFrame(pdfs)

    def pdf(self, src, dst):
        """return pdf[src][dst], which is pdf of src-dst Rtts"""
        if src in self.pdfs.columns and dst in self.pdfs.index:
            return self.pdfs[src][dst]
        else:
            return None

    def cnd_prob_log(self, src, dst, rtt):
        """return ln( P(rtt|dst)) of src, None if not exists"""
        kde = self.pdf(src, dst)
        if kde == None:
            return None
        ret = float(kde.score_samples(rtt)[0])
        return ret

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
        """store the trained RTTs pdfs in file named <fn>"""
        if not self.pdfs.empty:
            self.pdfs.to_pickle(self.path + fn)
            print 'Written to', fn
        else:
            print 'Nothing to write'

    def load(self, fn = 'pdfs.pickle'):
        """load the trained RTTs pdfs in file named <fn>"""
        self.pdfs = pandas.read_pickle(self.path + fn)
        print 'read from', fn

if __name__ == '__main__':
    pdfs = Training()
    #pdfs.gen_test()
    #pdfs.train('train.rtt')
    #pdfs.store()
    pdfs.load()
    print pdfs.cnd_prob_log(u'西安', u'武汉', 50)
    print pdfs.cnd_prob_log(u'西安', u'西安', 50)
    pdfs.plot_pdf(u'西安', u'西安')
    pdfs.plot_pdf(u'北京', u'北京')
    pdfs.plot_pdf(u'青岛', u'青岛')


