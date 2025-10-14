import numpy as np
import csv
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
import uuid
import networkx as nx
import json
import geopandas as gpd
from shapely.geometry import Polygon, Point
import random
from itertools import cycle
from random import sample
from lib.decoder import Decoder

#import unicode

#https://bl.ocks.org/mbostock/3014589

folder_data = 'data/'
folder_simulations = 'simulations/'
        
class Location:
    
    def __init__(self, filename, area_name, equal_density = False, density=5, from_file=False, plot=True):

        # BASIC COMPONENTS        
        self.data = gpd.read_file(folder_data+filename, encoding='utf-8')
        self.id = filename[:-8] + '-' + str(uuid.uuid4())[0:4]
        self.filename = filename
        self.area_name = area_name
        self.density = density

        # HABITANTS
        self.equal_density = equal_density
        self.subloc_habitants = {}
        self.habitants_subloc = {}        
        self.habitants_position = {}
        self.habitants_weight = {}
        self.n_habitants = 0   
        self.setup_habitants()       

        if not from_file:
            # NETWORK
            self.network = None
            self.setup_default_network()

            # PROPAGATION RELATED
            #self.habitants_seed = {}
            self.seeds_id = None
            self.set_empty_seeds()

            #self.habitants_vaccinated = {}
            self.vaccinated_id = None        
            self.set_empty_vaccinated()
            
            # Export
            self.export(plot)
                     
    ###############################
    ### SETUP FUNCTIONS                
    def setup_habitants(self):

        for subloc_id, row in self.data.iterrows():
            population = self.n_habitants_subloc(row)
            self.subloc_habitants[subloc_id] = self.generate_habitants(subloc_id, row['geometry'], population)

    def n_habitants_subloc(self, row):
        
        if self.equal_density:
            #population = int((row[self.area_name]*self.density))
            population = int(random.uniform(1, self.density))         
        else:
            population = int(row['POPULATION']/1000)
        
        return population

    def generate_habitants(self, subloc_index, polygon, size):
        min_x, min_y, max_x, max_y = polygon.bounds
        habitants_subloc = []
        while len(habitants_subloc) < size:
            random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
            if (random_point.within(polygon)):
                x_y = (random_point.x, random_point.y)
                self.subloc_habitants[subloc_index] = self.n_habitants
                self.habitants_subloc[self.n_habitants] = subloc_index
                self.habitants_position[self.n_habitants] = x_y 
                habitants_subloc.append(self.n_habitants)
                #self.habitants_seed[self.n_habitants] = False
                self.habitants_weight[self.n_habitants] = 0.5
                self.n_habitants += 1

        return habitants_subloc

    def setup_default_network(self):
        #p_dist = lambda r: r**(-1)
        #w = {i: random.expovariate(0.5) for i in range(self.n_habitants)}
        #self.network = nx.geographical_threshold_graph(self.n_habitants, -0.05, pos=self.habitants_position, p_dist=p_dist, weight=self.habitants_weight)
        #self.network = nx.geographical_threshold_graph(self.n_habitants, 350, pos=self.habitants_position) # ICA
        #self.network = nx.geographical_threshold_graph(self.n_habitants, 650, pos=self.habitants_position) # BIOBIO
        #self.network = nx.geographical_threshold_graph(self.n_habitants, 450, pos=self.habitants_position) # ZACATECAS
        #self.network = nx.geographical_threshold_graph(self.n_habitants, 650, pos=self.habitants_position) # TOLIMA
        #self.network = nx.geographical_threshold_graph(self.n_habitants, 70, pos=self.habitants_position) # RONDONIA
        self.network = nx.geographical_threshold_graph(self.n_habitants, 10, pos=self.habitants_position) # GRID
        for n in self.network.nodes:
            weight = self.network.nodes[n]['weight']
            self.habitants_weight[n] = weight
        #nx.set_node_attributes(self.network, self.habitants_seed, 'seed')

    def link_sublocs(self, links):
        for (ori, des) in links:
            ratio = 0.8
            n_links_ori = int(len(self.subloc_habitants[ori]) * ratio)
            n_links_des = int(len(self.subloc_habitants[des]) * ratio)
            n_links = min(n_links_ori, n_links_des)
            ori_sample = sample(self.subloc_habitants[ori], n_links)
            des_sample = sample(self.subloc_habitants[des], n_links)
            for idx, hab in enumerate(ori_sample):
                self.network.add_edge(ori_sample[idx], des_sample[idx])

    
    ###############################
    ### PLOTING    
    def plot(self, show = True, save_image = True, seeds = None):
        fig, ax = plt.subplots(figsize=(20, 20))
        self.data.plot(column='POPULATION', color='#f7fbff', linewidth=1, edgecolor='#000000', figsize=(12, 12), ax=ax)
        cycol = cycle('bgrcmk')

        for index, row in self.data.iterrows():
            color = []
            positions = list(map(lambda x: self.habitants_position[x], self.subloc_habitants[index]))
            if(len(positions) != 0):
                x,y = zip(*positions)
                for h in self.subloc_habitants[index]:
                    if self.network.node[h]['seed'] == True:
                        color.append('#e41a1c')
                    else:
                        color.append('#4daf4a')
                ax.scatter(x, y, s=15, marker='o', c=color)
            ax.annotate(s=index, xy=(row['centroid_x'], row['centroid_y']), horizontalalignment='center')
        
        for e in self.network.edges():
            ori = self.habitants_position[e[0]]
            des = self.habitants_position[e[1]]
            ax.plot([ori[0], des[0]], [ori[1], des[1]], '-', c='gray', alpha=0.1)

        if save_image:
            filename = 'simulations/location_' + self.id
            if seeds is not None:
                filename += '_seeds_' + seeds
            fig.savefig(filename + '.pdf')

        if show:
            plt.show()
    
    ###############################
    ### EXPORT/IMPORT   
    def export(self, plot):
        # ALL INFO
        with open(folder_simulations + 'location_' + self.id + '_allinfo.json', 'w') as json_file:
            all_info = {}
            all_info['filename'] = self.filename
            all_info['area_name'] = self.area_name
            all_info['density'] = self.density
            all_info['equal_density'] = self.equal_density
            all_info['subloc_habitants'] = self.subloc_habitants
            all_info['habitants_subloc'] = self.habitants_subloc            
            all_info['habitants_position'] = self.habitants_position            
            all_info['habitants_weight'] = self.habitants_weight
            # TODO: REMOVE SEEDS AS PART OF COUNTRY, IT SHOULD ALWAYS START EMPTY
            #all_info['habitants_seed'] = self.habitants_seed            
            all_info['n_habitants'] = self.n_habitants
            json.dump(all_info, json_file)
        
        # EDGES
        with open(folder_simulations + 'location_' + self.id + '_edges.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['n1', 'n2'])            
            for e in self.network.edges():
                writer.writerow([e[0], e[1]])
        
        if plot:
            self.plot(show=False)
    
    @classmethod
    def from_identifier(cls, identifier):
        with open(folder_simulations + 'location_' + identifier + '_allinfo.json', 'r') as json_file:
            # TODO: NOT SURE IF THE DECODER IS USEFUL GIVEN TRANSFORMATION LATER
            data = json.load(json_file, cls=Decoder)
        location = cls(data['filename'], data['area_name'], data['equal_density'], data['density'], from_file=True, plot=False)
        location.id = identifier
        location.subloc_habitants = {int(k):v for k,v in data['subloc_habitants'].items()} 
        location.habitants_subloc = {int(k):v for k,v in data['habitants_subloc'].items()} 
        location.habitants_position = {int(k):v for k,v in data['habitants_position'].items()} 
        location.habitants_weight = {int(k):v for k,v in data['habitants_weight'].items()} 
        location.n_habitants = data['n_habitants']
        location.load_network_from_file(identifier, data)
        
        # Locations always start with no seeds
        location.set_empty_seeds()
        location.set_empty_vaccinated()
        return location
    
    def load_network_from_file(self, identifier, data):
        network = nx.Graph()
        network.add_nodes_from(range(0, self.n_habitants))
        nx.set_node_attributes(network, self.habitants_weight, 'weight')
        nx.set_node_attributes(network, self.habitants_position, 'pos')
        #nx.set_node_attributes(network, self.habitants_seed, 'seed')         
                    
        with open(folder_simulations + 'location_' + identifier + '_edges.csv', mode='r') as file:
            reader = csv.reader(file, delimiter=',')
            header = next(reader)
            for row in reader:
                network.add_edge(int(row[0]), int(row[1]))
                
        self.network = network

    ###############################
    ### PROPAGATION RELATED    
    def create_seeds_config(self, loc_idxs, ratio, plot = True):
        seeds_id = str(uuid.uuid4())[0:4]  
        with open(folder_simulations + 'location_' + self.id + '_seeds_' + seeds_id + '.csv', 'w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['node_id'])
            for idx in loc_idxs:
                subloc_habitants = self.subloc_habitants[idx]
                subloc_n_habitants = len(subloc_habitants)
                sample_size = int(subloc_n_habitants*ratio)
                subloc_sample = sample(subloc_habitants,sample_size)
                for s in subloc_sample:
                    #self.habitants_seed[s] = True
                    self.network.node[s]['seed'] = True
                    writer.writerow([s])
        if plot:
            self.plot(show=False, save_image=True, seeds=seeds_id)
        self.seeds_id = seeds_id

    def load_seeds_config(self, identifier):
        self.set_empty_seeds()
        self.seeds_id = identifier
        with open(folder_simulations + 'location_' + self.id + '_seeds_' + identifier + '.csv', mode='r') as file:
            reader = csv.reader(file, delimiter=',')
            header = next(reader)
            for row in reader:
                node = int(row[0])
                #self.habitants_seed[node] = True
                self.network.node[node]['seed'] = True

    def set_empty_seeds(self):
        #print('set empty seed')
        self.seeds_id = None
        habitants_seed = {}
        for node in range(0, self.n_habitants):
            habitants_seed[node] = False
            #self.network.node[node]['seed'] = False
        nx.set_node_attributes(self.network, habitants_seed, 'seed')    

    def set_empty_vaccinated(self):
        #print('set empty vaccinated')
        self.vaccinated_id = None
        habitants_vaccinated = {}
        for node in range(0, self.n_habitants):
            habitants_vaccinated[node] = False
            #self.network.node[node]['vaccinated'] = False
            #vaccinated.append(False)
        nx.set_node_attributes(self.network, habitants_vaccinated, 'vaccinated')    

    def vaccinate(self, sublocs):
        self.set_empty_vaccinated()
        for sl in sublocs:
            for node in self.subloc_habitants[sl]:
                #self.habitants_vaccinated[node] = True
                self.network.node[node]['vaccinated'] = True

    
