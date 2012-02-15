
from Model import *

class Controller:
    ''' Handles connection between the 
    view and the model, and keeps some
    state for the UI. '''

    def __init__(self, graph=None):
        # Set up default graph to show
        if graph is None:
            graph = Graph()
            graph.addState('Start state', {'start':True})
            s0 = graph.getState(0)
            graph.addTransition(s0, s0, 'loop')
        self.graph = graph
        self.selection = 0
        self.fileOpen = None
        self.unsavedChanges = False
        # Set up listeners
        self.listeners = []

    # ----------------------------------
    # Functions regarding updating state
    # (i.e. observer pattern)
    # ----------------------------------


    def registerListener(self, function):
        if function in self.listeners:
            return False
        self.listeners.append(function)
        return True

    def notifyListeners(self):
        print self.graph.toSerializable()
        for function in self.listeners:
            function()

    # ----------------------------------
    # Functions for getting state
    # ----------------------------------

    def getCurrentState(self):
        ''' Returns the state object currently selected '''
        return self.graph.getState(self.selection)

    # ----------------------------------
    # 
    # ----------------------------------

    def createState(self, widget):
        self.unsavedChanges = True
        state = self.graph.addState()
        self.selection = self.graph.numStates() - 1
        self.notifyListeners()

    
