
from Model import *

class Controller:
    ''' Handles connection between the 
    view and the model '''

    def __init__(self, graph=None):
        # Set up default graph to show
        if graph is None:
            graph = Graph()
            graph.addState('Start state', {'start':True})
            s0 = graph.getState(0)
            graph.addTransition(s0, s0, 'loop')
        self.graph = graph
        # Set up listeners
        self.listeners = []
        

    def registerListener(self, function):
        if function in self.listeners:
            return False
        self.listeners.append(function)
        return True

    def notifyListeners(self):
        for function in self.listeners:
            function()

    
