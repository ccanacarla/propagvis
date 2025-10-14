import matplotlib.pyplot as plt
from matplotlib import animation
from numpy import random 
from IPython.display import HTML
from lib.sirmodel import SIRModel 
import csv
import numpy as np
import matplotlib as mpl
from descartes.patch import PolygonPatch
from matplotlib.collections import PatchCollection
import pandas as pd

class PropagationCountryAnimator:
       
    def __init__(self, identifier, country, interval):
        # INIT INSTANCE VARIABLES
        self.max_infected = 0
        self.max_subloc = {}
        for loc in country.subloc_habitants.keys():
            self.max_subloc[loc] = 0
        self.id = identifier
        self.country = country
        self.fig, self.ax = plt.subplots(figsize=(20, 20))
        self.ax.set_aspect('equal')
        self.history = {}
        self.time_steps = {}
        self.frame_num = 0
        Writer = animation.writers['ffmpeg']
        self.writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        self.loc_collection = None
        self.interval = interval

        # PLOT ELEMENTS
        self.loc_collection = None
        self.time_stamp = None
        
        # SETUP FUNCTIONS
        self.load_data()
        
    def load_data(self):        
        folder = 'simulations/'
        filename = folder + 'sim_' + self.id + '_country_' + self.country.id + '_seeds_' + self.country.seeds_id + '_history.csv'
        data = pd.read_csv(filename)
        time = 0
        last_idx_all = (data.iloc[-1:]).index.tolist()[0]
        while(True):
            subset = data[(data['time'] >= self.interval*time) & (data['time'] < self.interval*(time+1))]
            if subset.empty:
                self.history[time] = self.history[time-1]
                self.time_steps[time] = self.interval*time
            else:
                last = list(subset.iloc[-1,:])
                last_idx = (subset.iloc[-1:]).index.values.tolist()[0]
                self.history[time] = self.compute_snapshot(last[1:])
                self.time_steps[time] = self.interval*time      
                if last_idx == last_idx_all:
                    break
            time += 1
        self.frame_num = len(self.history)
    
    def compute_snapshot(self, nodes_status): 
        sublocs_idx = self.country.data.index.values.tolist()         
        snapshot = {}
        for idx in sublocs_idx:
            snapshot[idx] = 0
        for index, status in enumerate(nodes_status):
            pos = self.country.habitants_subloc[index]
            if status == 'I':
                snapshot[pos] += 1
                self.max_infected = max(self.max_infected, snapshot[pos])
                self.max_subloc[pos] = max(self.max_subloc[pos], snapshot[pos])
        return snapshot
                
    def init_data(self):
        polygons = []
        cmap = mpl.cm.YlOrRd
        geoms = list(self.country.data['geometry'])
        p = PatchCollection([PolygonPatch(poly) for poly in geoms], cmap=cmap, alpha=1, linewidth=0.5, edgecolor='black')
        self.loc_collection = p
        self.ax.add_collection(p, autolim=True)
        self.ax.autoscale_view()
        self.time_stamp = plt.text(0.9,0.05,'0',verticalalignment='center', horizontalalignment='left', transform=self.ax.transAxes,fontsize=25)
        return self.loc_collection

    def animate(self, time):
        max_habi = self.max_infected       
        colors = []
        for idx, row in self.country.data.iterrows():
                norm = mpl.colors.Normalize(vmin=0, vmax=self.max_subloc[idx])
                n = self.history[time][idx]
                colors.append(norm(n))
        self.loc_collection.set_array(np.array(colors)) # set new color colors
        self.time_stamp.set_text(self.time_steps[time])
        return self.loc_collection,
    
    def play(self):
        anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init_data,
                                       frames=self.frame_num, interval=10, blit=False)
        anim.save('simulations/sim_' + self.id + '_country_' + self.country.id + '_seeds_' + self.country.seeds_id + '.mp4', writer=self.writer)
        return anim