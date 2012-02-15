
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
        self.notifying = False
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
        # Hopefully there won't be two threads
        # trying to hit this at the same time:
        if self.notifying: return
        self.notifying = True
        for function in self.listeners:
            function()
        self.notifying = False

    # ----------------------------------
    # Functions for getting state
    # ----------------------------------

    def getCurrentState(self):
        ''' Returns the state object currently selected '''
        return self.graph.getState(self.selection)

    # ----------------------------------
    # Functions for UI events
    # ----------------------------------

    def createState(self, widget):
        self.unsavedChanges = True
        state = self.graph.addState()
        self.selection = self.graph.numStates() - 1
        self.notifyListeners()

    def selectState(self, widget):
        index = widget.get_active()
        if index >= 0 and index != self.selection:
            oldSelection = self.selection
            self.selection = index
            self.notifyListeners()

    def removeState(self, widget):
        self.unsavedChanges = True
        # TODO: ensure state is not the start state
        self.graph.removeState(self.selection)
        self.selection -= 1
        self.notifyListeners()
