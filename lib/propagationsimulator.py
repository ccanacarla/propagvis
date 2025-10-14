from lib.sirmodel import SIRModel
import networkx as nx

from lib.historystochasticdynamics import HistoryStochasticDynamics
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import json

from lib.propagationcountryanimator import PropagationCountryAnimator
import uuid
import pandas as pd

# TODO: SETUP CONFIG FILE THAT REMOVES THIS REPEATED CODE
folder_simulations = 'simulations/'

class PropagationSimulator:
    
    def __init__(self, country):
        self.params = self.init_params()
        self.country = country
        self.history = None
        self.results = None
        self.id = str(uuid.uuid4())[0:4] 
        
    def init_params(self):
        # TODO: FIX THIS COUPLED CODE
        param = dict()
        param[SIRModel.P_INFECT] = 0.01
        param[SIRModel.P_REMOVE] = 0.1
        param[SIRModel.P_INFECTED] = 0.05
        return param
    
    def set_params(self, p_infect, p_remove, p_infected):
        param = dict()
        param[SIRModel.P_INFECT] = p_infect
        param[SIRModel.P_REMOVE] = p_remove
        param[SIRModel.P_INFECTED] = p_infected
        self.params = param

    def get_params_id(self):
        export_id = str(self.params[SIRModel.P_INFECT]) + '-' 
        export_id += str(self.params[SIRModel.P_REMOVE]) + '-'
        export_id += str(self.params[SIRModel.P_INFECTED])
        return export_id
         
    def run(self):
        m = SIRModel()  
        f = HistoryStochasticDynamics(self.id, self.country.id, self.country.seeds_id, m, self.country.network)
        rc = f.set(self.params).run()
        self.results = rc
        self.export_results()
    
    def export_results(self):
        filename = folder_simulations + 'sim_' + self.id + '_country_' + self.country.id + '_seeds_' + self.country.seeds_id + '_results.json'
        with open(filename, 'w') as json_file:
            json.dump(self.results, json_file, default=str)
        self.export_history(0.5)
        self.plot()

    def export_history(self, interval, n_times=35):
        # LOAD DATA 
        filename = folder_simulations + 'sim_' + self.id + '_country_' + self.country.id + '_seeds_' + self.country.seeds_id + '_history.csv'
        data = pd.read_csv(filename)
        # SETUP INITIAL VARIABLES
        history = {}
        time_steps = {}
        last_idx_all = (data.iloc[-1:]).index.tolist()[0]

        # ALWAYS ADD FIRST TIME
        time = 0
        first = list(data.iloc[0,:])
        history[time] = self.compute_snapshot(first[1:])
        time_steps[time] = 0
        data = data.loc[1:, :]
        time += 1
        
        
        while(True):
            if time == 35:
                break
            subset = data[(data['time'] >= interval*time) & (data['time'] < interval*(time+1))]
            # TODO: THIS SHOULD NOT HAPPEN
            if subset.empty:
                history[time] = history[time-1]
                time_steps[time] = interval*time
            else:
                this_bin = self.summarize_bin(subset)
                last_idx = (subset.iloc[-1:]).index.values.tolist()[0]
                history[time] = self.compute_snapshot(this_bin[1:])
                time_steps[time] = interval*time      
                if last_idx == last_idx_all:
                    break
            time += 1

        filename = folder_simulations + 'sim_' + self.id + '_country_' + self.country.id + '_seeds_' + self.country.seeds_id + '_processedhistory.json'
        with open(filename, 'w') as json_file:
            json.dump(history, json_file, default=str)

    def summarize_bin(self, data):
        result = []
        for c in data:
            subset_column = data[c]
            n_infected = subset_column[subset_column == "I"].count()
            if n_infected > 0:
                result.append("I")
            else:
                result.append("S")
        return result

    
    def compute_snapshot(self, nodes_status): 
        sublocs_idx = self.country.data.index.values.tolist()         
        snapshot = {}
        for idx in sublocs_idx:
            snapshot[idx] = 0
        for index, status in enumerate(nodes_status):
            pos = self.country.habitants_subloc[index]
            if status == 'I':
                snapshot[pos] += 1
                #self.max_infected = max(self.max_infected, snapshot[pos])
                #self.max_subloc[pos] = max(self.max_subloc[pos], snapshot[pos])
        return snapshot
                
    def animation(self, interval):         
        animation = PropagationCountryAnimator(self.id, self.country, interval)
        return animation.play()

    def plot(self):
        fig, ax = plt.subplots(figsize=(10, 10))
        filename = folder_simulations + 'sim_' + self.id + '_country_' + self.country.id + '_seeds_' + self.country.seeds_id + '_history.csv'
        data = pd.read_csv(filename)
        x = []
        y_i = []
        y_s = []
        y_r = []
        for index, row in data.iterrows():
            x.append(row['time'])

            n_infected = len(list(filter(lambda x: x == 'I', row[1:])))
            y_i.append(n_infected)

            n_susceptible = len(list(filter(lambda x: x == 'S', row[1:])))
            y_s.append(n_susceptible)

            n_removed = len(list(filter(lambda x: x == 'R', row[1:])))
            y_r.append(n_removed)
        plt.plot(x, y_i, color='#e41a1c', label='Infected')
        plt.plot(x, y_s, color='#4daf4a', label='Susceptible')
        plt.plot(x, y_r, color='#377eb8', label='Recovered/Removed')
        plt.xlabel('Time')
        plt.ylabel('Number of people')
        plt.legend()
        plt.show()

        filename = 'simulations/sim_' + self.id + '_country_' + self.country.id + '_seeds_' + self.country.seeds_id
        fig.savefig(filename + '.pdf')
            

    
    
   

        
    