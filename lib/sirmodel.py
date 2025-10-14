from epydemic import *

class SIRModel(CompartmentedModel):
    # the possible dynamics states of a node for SIR dynamics
    SUSCEPTIBLE = 'S'
    INFECTED = 'I'
    REMOVED = 'R'

    VACCINATED = 'V'
    
    # the model parameters
    P_INFECTED = 'pInfected'
    P_INFECT = 'pInfect'
    P_REMOVE = 'pRemove'
    
    # the edges at which dynamics can occur
    SI = 'SI'
    
    def build( self, params ):
        pInfected = params[self.P_INFECTED]
        pInfect = params[self.P_INFECT]
        pRemove = params[self.P_REMOVE]

        self.addCompartment(self.INFECTED, pInfected)
        self.addCompartment(self.REMOVED, 0.0)
        self.addCompartment(self.SUSCEPTIBLE, 1 - pInfected)
        self.addCompartment(self.VACCINATED, 0.0)

        self.trackNodesInCompartment(self.INFECTED)
        self.trackEdgesBetweenCompartments(self.SUSCEPTIBLE, self.INFECTED, name=self.SI)

        self.addEventPerElement(self.SI, pInfect, self.infect)
        self.addEventPerElement(self.INFECTED, pRemove, self.remove)
    
    def infect( self, t, e ):
        (n, m) = e
        if self.network().node[n]['compartment'] != 'VACCINATED':
            self.changeCompartment(n, self.INFECTED)
        self.markOccupied(e, t)

    def remove( self, t, n ):
        self.changeCompartment(n, self.REMOVED)
        
    def initialCompartments( self ):
        g = self.network()
        for n in g.nodes():
            # put here removed nodes
            if g.node[n]['seed']:
                self.changeCompartment(n, self.INFECTED)
            elif g.node[n]['vaccinated']:
                self.changeCompartment(n, self.VACCINATED)
            else:
                self.changeCompartment(n, self.SUSCEPTIBLE)
        