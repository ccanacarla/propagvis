import numpy as np
from random import sample

class GridLocation:
    
    def __init__(self):
        self.habitants = []
        self.n_habitants = 0
        self.x_limits = [0, 0]
        self.y_limits = [0, 0]
    
    def set_x_limits(self, x0, x1):
        self.x_limits = [x0, x1]
        
    def set_y_limits(self, y0, y1):
        self.y_limits = [y0, y1]
        
    def add_habitant(self, h):
        self.habitants.append(h)
        self.n_habitants += 1
        
    def get_random_position(self):
        x = np.random.randint(self.x_limits[0], self.x_limits[1])
        y = np.random.randint(self.y_limits[0], self.y_limits[1])
        return (x, y)
        
    def width(self):
        return self.x_limits[1]-self.x_limits[0]

    def height(self):
        return self.y_limits[1]-self.y_limits[0]
    
    def area(self):
        return self.width() * self.height()
    
    def population_sample(self, size):
        return sample(self.habitants,size)