# -*- coding: utf-8 -*-

import math, cPickle
from training import Training
from core_route import RouteTable
from framework.netools.ip_database import load_ip2city
from framework.netools.inet_detect import ip2int
from collections import defaultdict

class Simulation():
    """"""
    MAX_TEST = 60
    MAX_HOP = 2

    def __init__(self):
        pass

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
            if rft[ecs]._check_ip(ip2int(router_ip)):
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

    def pp_prob_log(self, city):
        return 0

    def weight_prob_log(self, geo_info):
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
            population = self.pp_prob_log(city)
            weight = self.weight_prob_log(geo_info)
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

    def padding(self, test_rtt):
        """Some <ip-city> RTTs are not enough(<60), make it full."""
        for ip in test_rtt:
            for ecs, rtts in test_rtt[ip].items():
                if rtts:
                    for i in range(self.MAX_TEST - len(rtts)):
                        avr = round(sum(rtts) / len(rtts), 2)
                        rtts.append(avr)

    def locate(self, rtt_path, route_path):
        """"""
        ecs_list = self.select_ecs(0xffff)
        test_rtt = self.read_test_data('test.rtt', rtt_path)
        test_route = self.read_test_data('test.route', route_path)
        ip2city = load_ip2city('./resources/ip2city.pickle')
        pdfs = Training()
        pdfs.load('pdfs.pickle')
        rft = self.read_rft(ecs_list)
        self.padding(test_rtt)

        target_cities = pdfs.pdfs.index
        avr_city_rate = {}.fromkeys(target_cities, 0)
        num_ip_of_city = {}.fromkeys(target_cities, 0)
        suc_rate = defaultdict(int)
        good, bad = 0, 0
        for ip in test_rtt.iterkeys():
            valid_ecs = [ecs for ecs in ecs_list if test_rtt[ip][ecs] != []]
            # if the ip just response to 3 less landmarks, ignore it.
            if len(valid_ecs) < 3:
                bad += 1
                print 'Bad IP:', ip
                continue
            real_city = ip2city[ip].decode('utf-8')               
            num_ip_of_city[real_city] += 1 # total number of valid ip to real_city
            for i in range(self.MAX_TEST):
                geo_info = {}.fromkeys(valid_ecs)
                for ecs in valid_ecs:
                    latency = test_rtt[ip][ecs][i]
                    trace = test_route[ip].get(ecs, None)
                    geo_info[ecs] = self.gen_geo_info(ecs, latency, trace, rft)
                estimated_city = self.classifier(valid_ecs, pdfs, geo_info)
                if estimated_city == real_city:
                    suc_rate[ip] += 1.0
            suc_rate[ip] /= self.MAX_TEST
            avr_city_rate[real_city] += suc_rate[ip] #average succeed rate for each city!
            good += 1

        for city in avr_city_rate.keys():
            avr_city_rate[city] /= num_ip_of_city[city]
        print 'good:', good
        print 'bad :', bad
        return (avr_city_rate, suc_rate)

if __name__ == '__main__':
    simulate = Simulation()
    avr_city_rate, suc_rate = simulate.locate('./resources/', './resources/route/')
    fp = open('city_rate.txt', 'w')
    for city in avr_city_rate.keys():
        succeed_rate = avr_city_rate[city]
        print city, succeed_rate
        output = '\t'.join([city.encode('utf-8'), str(succeed_rate)]) + '\n'
        fp.write(output)
    fp.close()
    fp = open('ip_rate.txt', 'w')
    for ip, rate in suc_rate.items():
        output = '\t'.join([ip, str(rate)]) + '\n'
        fp.write(output)
    fp.close()
