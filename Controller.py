
from os import path

from Model import *
from View import *

class Controller:
    ''' Handles connection between the 
    view and the model, and keeps some
    state for the UI. '''

    def __init__(self, graph=None):
        # Set up default graph to show
        if graph is None:
            graph = Graph()
            graph.addState('Start state', {'start':True})
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
        print json.dumps(self.graph.toSerializable(), indent=4)
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
        if self.selection is 0: return
        self.unsavedChanges = True
        self.graph.removeState(self.selection)
        self.selection -= 1
        self.notifyListeners()

    def updateStateText(self, widget):
        self.unsavedChanges = True
        text = widget.get_text(widget.get_start_iter(), widget.get_end_iter())
        self.graph.getState(self.selection).text = text
        # No re-draw needed

    def createTransition(self, widget, data):
        self.unsavedChanges = True
        command, endNo = data
        start = self.getCurrentState()
        end = self.graph.getState(endNo)
        self.graph.addTransition(start, end, command)
        self.notifyListeners()

    def removeTransition(self, widget, command):
        self.unsavedChanges = True
        start = self.getCurrentState()
        self.graph.removeTransition(start, command)
        self.notifyListeners()
        
    def saveGame(self, menu):
        # Get file name
        filename = self.fileOpen
        if filename is None or menu == 'file.saveas':
            filename = fileDialog(save=True)
        if filename:
            # Check for overwriting existing file
            if path.exists(filename) and not \
                    askYesNO('Overwrite existing file?'):
                return
            # Save file
            saveGraph(self.graph, filename)
            self.unsavedChanges = False

    def openGame(self, menu):
        # Check for unsaved changes
        if self.unsavedChanges and not \
                askYesNO('There are unsaved changes. Open the file anyway?'): 
            return
        # Open the file
        filename = fileDialog()
        if filename:
            self.graph = loadGraph(filename)
            self.unsavedChanges = False
            self.fileOpen = filename
            self.notifyListeners()
