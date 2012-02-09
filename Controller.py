
from states import *

class Controller:
    ''' Handles connection between the 
    view and the model '''

    def __init__(self, graph=None):
        if graph is None:
            graph = Graph()
        self.graph = graph

    
