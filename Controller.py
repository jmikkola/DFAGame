
from Model import *

class Controller:
    ''' Handles connection between the 
    view and the model '''

    def __init__(self, graph=None):
        # Set up default graph to show
        if graph is None:
            graph = Graph()
            graph.addState('', {'start':True})
        self.graph = graph

    
