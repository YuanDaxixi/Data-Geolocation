# -*- coding: utf-8 -*-

import math, cPickle, random
import pandas as pd
from training import Training
from core_route import RouteTable
from framework.netools.ip_database import load_ip2city
from framework.netools.inet_detect import ip2int
from collections import defaultdict

class Simulation():
    """An offline geolocation simulation, all data is real, not imitated"""
    MAX_TEST = 100
    MAX_HOP = 2

    def __init__(self, test_time = 100):
        self.MAX_TEST = test_time

    def select_ecs(self, option):
        """input an option(integer), return a list of ecs"""
        with open('./resources/servers.txt', 'r+') as fp:
        # line[0] is ip, line[1] is city name, line[-1] is status
            temp_list = [line.split()[1].decode('utf-8') for line in fp.readlines()]
            ecs_list, i = [], 0
            ecs_number = len(temp_list)
            while option > 0 and i < ecs_number:
                if option & 0x1 == 1:
                    ecs_list.append(temp_list[i])
                option = option >> 1
                i += 1
        return ecs_list
    
    def read_test_data(self, fn, path = './resources/'):
        """return test RTTs, it's a dict of dict"""
        try:
           fp = open(path + fn, 'rb')
        except IOError, e:
            raise
        return cPickle.load(fp)
    
    def read_rft(self, cities):
        """return a dict of route frequency tables which are dict of dict"""
        rft, path = {}, './resources/route/' 
        for city in cities:
            route_table = RouteTable(None, None)
            filename = path + city + '.route'
            route_table.load(filename)
            rft[city] = route_table
        return rft

    def _read_test_ips(self, path, filename):
        try:
           fp = open(path + filename, 'r')
        except IOError, e:
            raise
        test_ips = [ip.strip() for ip in fp.readlines()]
        return test_ips

    def _read_pop(self, path, filename):
        self.pop_df = pd.read_csv(path + filename, index_col = 0, encoding = 'utf-8')
        self.total_pop = sum(float(pop) for pop in self.pop_df['pop'])

    def gen_geo_info(self, ecs, latency, trace, rft):
        """generate geolocation information--[latency, {city: (hop, weight)} ]"""
        if trace == None:
            return [latency, None]
        geo_info, result, hop, bias = [], {}, 0, 0
        geo_info.append(latency)
        trace = list(reversed(trace))
        # only the router within MAX_HOP hop will be selected
        while hop + bias < self.MAX_HOP + bias:
            router_ip = trace[hop]
            hop += 1
            if router_ip == '0.0.0.0' or rft[ecs]._check_ip(ip2int(router_ip)):
            #{city: (hop, weight)}
                weights = {item[0]: (hop - bias, item[1]) for item in rft[ecs].weight(router_ip)}
                for city, value in weights.items():
                    if city in result.keys():
                        result[city] = (result[city][0], result[city][1] + 0.5 * value[1])
                    else:
                        result[city] = value
            else:
                bias += 1        
        geo_info.append(result)
        return geo_info

    def _pp_prob_log(self, city):
        pop = self.pop_df['pop'][city] # DataFrame[column][row] 
        prob = math.log(pop / self.total_pop)
        return prob 

    def _weight_prob_log(self, geo_info):
        return 0

    def classifier(self, landmarks, pdfs, geo_info):
        """Bayes classifier, at present it uses pdfs of RTTs, frequencey of routes to
        calculate the result. Population and weights are not implemented yet."""
        good_candidates = []
        for each_landmark_view in geo_info.values():
            if each_landmark_view[1]:
                good_candidates += each_landmark_view[1].keys()
        good_candidates = set(good_candidates)
        all_candidates = set(pdfs.pdfs.index)
        good_candidates.intersection_update(all_candidates)
        result = {}
        for city in good_candidates:
            union_prob = sum([pdfs.cnd_prob_log(landmark, city, geo_info[landmark][0])
                              for landmark in landmarks])
            freq_log = 0
            for landmark in landmarks:
                if geo_info[landmark][1] and city in geo_info[landmark][1].keys():
                    hop, freq = geo_info[landmark][1][city]
                    freq_log += math.log(1.0 / hop * freq + math.e) 
            population = self._pp_prob_log(city)
            weight = self._weight_prob_log(geo_info)
            union_prob += freq_log + population + weight
            result[city] = union_prob
        # if good_candidates is empty(no route information), select best from all.
        if result == {}:
            for city in all_candidates:
                union_prob = sum([pdfs.cnd_prob_log(landmark, city, geo_info[landmark][0])
                              for landmark in landmarks])
                result[city] = union_prob
        best_candidate = max(result, key = result.get)

        return best_candidate

    def _padding(self, test_rtt):
        """Some <ip-city> RTTs are not enough(<100), make it full."""
        for ip in test_rtt:
            for ecs, rtts in test_rtt[ip].items():
                if rtts:
                    for i in range(self.MAX_TEST - len(rtts)):
                        avr = round(sum(rtts) / len(rtts), 2)
                        rtts.append(avr)
    
    def _add_latency(self, path, filename, test_rtt, test_type = 0, blocksize = 1024):
        """add rtts and hdd delays(PDP delays as well), and get average of hdd delays
        path -- the path of <filename>
        filename -- hdd delays(PDP delays) filename
        test_type -- test_type of simulation
        blocksize -- file blocksize in simulation"""
        if test_type == 0:
            self.eigenvalue = 0.0
        else:
            extra_df = pd.read_csv(path + filename)
            blocksize = str(blocksize)
            if blocksize not in extra_df.columns:
                print 'Bad blocksize: %s' % blocksize
                return test_rtt
            extra_delays = [float(delay) for delay in extra_df[blocksize] if delay != '-1.0']
            for ip in test_rtt.iterkeys():
                for ecs in test_rtt[ip].keys():
                    test_rtt[ip][ecs] = self._synthetize(test_rtt[ip][ecs], extra_delays)
            self.eigenvalue = sum(extra_delays) / len(extra_delays)
        
    def _synthetize(self, rtts, extra_delays):
        """algorithm about how to add rtts and hdd delays(PDP delays)"""
        num_of_rtts, num_of_delays = len(rtts), len(extra_delays)
        if (num_of_rtts <= num_of_delays):
            magic = random.sample(extra_delays, num_of_rtts)
            for i in range(num_of_rtts):
                rtts[i] += magic[i]
        else:
            for i in range(num_of_rtts):
                magic = random.choice(extra_delays)
                rtts[i] += magic
        return rtts


    def _sample_latency(self, latencies, test_type = 0, index = 0):
        """sample latency for different test, test_type == 0 represents IP geolocation,
        test_type == 1 represents MAC-PDP geolocation, test_type == 2 represents E-PDP.
        latencies -- a list of real latencies
        test_type -- test_type of simulation
        index -- index of <latencies>, only meaningful when test_type == 0"""
        challenges, factor = 40, 3
        if test_type == 0:
            res = latencies[index]
        elif test_type == 1:
            sample = random.sample(latencies, challenges)
            res = sum(sample) / len(sample) - self.eigenvalue
        elif test_type == 2:
            sample = random.sample(latencies, challenges / factor + 1)
            res = sum(sample) / len(sample) - self.eigenvalue
        else:
            res = -1
        return res


    def locate(self, rtt_path, route_path, test_file, pdp_file = 'ecs_hdd.csv', 
               test_type = 0, blocksize = 1024):
        """It loads all the data needed first, then geolocates the test data, 
        return the geolocation results."""
        ecs_list = self.select_ecs(0xffff)
        test_ips = self._read_test_ips(rtt_path, test_file)
        test_rtt = self.read_test_data('test.rtt', rtt_path)
        test_route = self.read_test_data('test.route', route_path)
        ip2city = load_ip2city('./resources/ip2city.pickle')
        pdfs = Training()
        pdfs.load('pdfs.pickle')
        rft = self.read_rft(ecs_list)
        self._read_pop(rtt_path, 'population.csv')
        self._padding(test_rtt)
        self._add_latency(rtt_path, pdp_file, test_rtt, test_type, blocksize)
        print 'Preparation Completed!'
        
        target_cities = pdfs.pdfs.index
        avr_city_rate = {}.fromkeys(target_cities, 0)
        num_ip_of_city = {}.fromkeys(target_cities, 0)
        suc_rate = defaultdict(int)
        failure_geo = defaultdict(list)
        step, total_ips = 0, len(test_ips)
        for ip in test_ips:
            step += 1
            print '%d / %d' % (step, total_ips)
            valid_ecs = [ecs for ecs in ecs_list if test_rtt[ip][ecs] != []]
            # if the ip just response to 3 less landmarks, ignore it.
            if len(valid_ecs) < 3:
                continue
            real_city = ip2city[ip].decode('utf-8')
            num_ip_of_city[real_city] += 1 # total number of valid ip to real_city
            for i in range(self.MAX_TEST):
                geo_info = {}.fromkeys(valid_ecs)
                for ecs in valid_ecs:
                    latency = self._sample_latency(test_rtt[ip][ecs], test_type, i)
                    #latency = test_rtt[ip][ecs][i]
                    trace = test_route[ip].get(ecs, None)
                    geo_info[ecs] = self.gen_geo_info(ecs, latency, trace, rft)
                estimated_city = self.classifier(valid_ecs, pdfs, geo_info)
                if estimated_city == real_city:
                    suc_rate[ip] += 1.0
                else:
                    failure_geo[ip] += [estimated_city]
            suc_rate[ip] /= self.MAX_TEST
            avr_city_rate[real_city] += suc_rate[ip] #average succeed rate for each city!

        for city in avr_city_rate.keys():
            avr_city_rate[city] /= num_ip_of_city[city]
        bad_ips = set(test_ips).difference(set(suc_rate.keys()))
        for ip in failure_geo.keys():
            failure_geo[ip] = [ip2city[ip], str(len(failure_geo[ip]))] + failure_geo[ip]
            
        return (avr_city_rate, suc_rate, bad_ips, failure_geo)


    def reports(self, number, path = './reports/', *args):
        avr_city_rate, suc_rate, bad_ips, failure_geo = args[0]
        filenames = ['city_rate', 'ip_rate', 'failure_ips', 'failure_geo']
        filenames = [path + fn + str(number) + '.txt' for fn in filenames]

        with open(filenames[0], 'w') as fp:
            for city in avr_city_rate.keys():
                succeed_rate = avr_city_rate[city]
                print city, succeed_rate
                output = '\t'.join([city.encode('utf-8'), str(succeed_rate)]) + '\n'
                fp.write(output)

        with open(filenames[1], 'w') as fp:
            for ip, rate in suc_rate.items():
                output = '\t'.join([ip, str(rate)]) + '\n'
                fp.write(output)

        with open(filenames[2], 'w') as fp:
            for ip in bad_ips:
                fp.write(ip + '\n')

        with open(filenames[3], 'w') as fp:
            for ip, value in failure_geo.items():
                output = '\t'.join([ip] + value) + '\n'
                fp.write(output)

if __name__ == '__main__':
    simulate = Simulation(100)
    for i in range(6):
        results = simulate.locate('./resources/', './resources/route/', 'test_ips.txt',
                                 'WD-E-PDP.csv', 2)
        simulate.reports(200 + i, './reports/e-pdp/', results)
        print '%dth Simulation Completed.' % i
