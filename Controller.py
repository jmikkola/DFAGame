
from os import path

from Model import *
from View import *

class Controller:
    ''' Handles connection between the 
    view and the model, and keeps some
    state for the UI. '''

    def __init__(self, graph=None):
        # Graph display values
        self.maxXdist = 0
        self.maxYdist = 0
        self.space = 50
        self.nPositions = 0
        # Set up default graph to show
        if graph is None:
            graph = Graph()
            state = graph.addState('Start state')
            self.setPosition(state)
        self.graph = graph
        # UI-related values
        self.selection = 0
        self.fileOpen = None
        self.unsavedChanges = False
        self.notifying = False
        self.isPlaying = False
        # Set up listeners
        self.listeners = []

    def main(self):
        ''' This method starts the program '''
        self.window = BuilderWindow(self)
        # Transfer control to GTK event loop
        gtk.main()

    def exit(self, event):
        ''' Exit the program '''
        if self.checkClose():
            gtk.main_quit()

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
        #print json.dumps(self.graph.toSerializable(), indent=4)
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
        self.setPosition(state)
        # Notify change
        self.notifyListeners()

    def selectStateListener(self, widget):
        self.selectState(widget.get_active())

    def selectState(self, index):
        if index >= 0 and index != self.selection:
            oldSelection = self.selection
            self.selection = index
            self.notifyListeners()

    def removeState(self, widget):
        if self.selection is 0: return
        self.unsavedChanges = True
        self.graph.removeState(self.selection)
        self.selection -= 1
        self.recalcPositions()
        self.notifyListeners()

    def updateStateText(self, widget):
        self.unsavedChanges = True
        text = widget.get_text(widget.get_start_iter(), \
                               widget.get_end_iter())
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


    # ----------------------------------
    # Functions for file handling
    # ----------------------------------

    def saveGame(self, menu):
        # Get file name
        filename = self.fileOpen
        if filename is None or menu == 'file.saveas':
            filename = fileDialog(save=True)
        if filename:
            # Check for overwriting existing file
            if self.fileOpen is None and path.exists(filename):
                if not askYesNO('Overwrite existing file?'):
                    return False
            # Save file
            saveGraph(self.graph, filename)
            self.unsavedChanges = False
            return True
        return False

    def openGame(self, menu):
        # Check for unsaved changes
        if self.unsavedChanges and not self.checkClose(False):
            return
        # Open the file
        filename = fileDialog()
        if filename:
            self.loadGraph(filename)

    def loadGraph(self, filename):
        ''' Handles loading a graph '''
        self.graph = loadGraph(filename)
        self.unsavedChanges = False
        self.fileOpen = filename
        for state in self.graph.states:
            self.setPosition(state)
        self.selection = 0
        self.notifyListeners()

    def checkClose(self, quitting=True):
        ''' Called before closing the program or file
        to ensure no unsaved changes are lost. Returns
        True is the close should still be performed, 
        or False to indicate that the operation should 
        be canceled. '''
        if self.unsavedChanges is False:
            return True
        answer = askUnsavedChanges(quitting)
        if answer is 2:
            return False
        if answer is 1:
            if not self.saveGame('quit'):
                return False
        return True

    def setEndingState(self, widget):
        ''' Changes whether the selected state is an ending 
        (accept/final) state '''
        isEnding = widget.get_active()
        state = self.getCurrentState()
        old_isEnding = True if state.getAttribute('end') else False
        if isEnding != old_isEnding:
            self.unsavedChanges = True
            state.addAttribute('end', isEnding)
            self.notifyListeners()
        

    # ----------------------------------
    # Functions for graph display
    # ----------------------------------

    def getPosition(self, stateNo):
        ''' Gives the position of the given state '''
        state = self.graph.getState(stateNo)
        attrs = state.attributes
        return int(attrs['x']), int(attrs['y'])

    def getNextPosition(self):
        ''' Computes and available position for 
        placing the node. '''
        xd, yd = self.maxXdist, self.maxYdist
        sp = self.space
        if xd < yd: return (xd + sp, sp)
        else:       return (sp, yd + sp)

    def nextDefaultPosition(self):
        ''' Gets the next position under the old 
        position algorithm '''
        i = self.nPositions
        self.nPositions += 1
        sp = self.space
        return (sp + sp*(i%10), sp + sp*(i/10))

    def moveState(self, stateNo, position):
        self.unsavedChanges = True
        state = self.graph.getState(stateNo)
        self.setStatePosition(state, position)
        self.notifyListeners()

    def setStatePosition(self, state, position):
        ''' Updates or sets the position of a state '''
        x,y = position
        state.attributes['x'] = x
        state.attributes['y'] = y
        self.maxXdist = max(self.maxXdist, x)
        self.maxYdist = max(self.maxYdist, y)

    def recalcPositions(self):
        ''' Recalculates the dimensions after 
        a removal '''
        xmax, ymax = 0, 0 # assuming positions are positive
        for state in self.graph.states:
            attrs = state.attributes
            xmax = max(xmax, int(attrs['x']))
            ymax = max(ymax, int(attrs['y']))
        self.maxXdist = xmax
        self.maxYdist = ymax

    def setPosition(self, state):
        ''' Sets up the position of a newly added state '''
        attrs = state.attributes
        if ('x' not in attrs) or ('y' not in attrs):
            self.setStatePosition(state, self.nextDefaultPosition())
        else:
            self.maxXdist = max(self.maxXdist, attrs['x'])
            self.maxYdist = max(self.maxYdist, attrs['y'])
        

    # ----------------------------------
    # Functions for demoing the game
    # ----------------------------------

    def startGame(self, menu):
        # Don't allow to instances at once
        if self.isPlaying:
            return
        self.isPlaying = True
        # isPlaying gets set back to False by PlayWindow.delete_event()
        
        # Unless the game will start from the selected
        # state, move to the start state
        if menu != 'play.startfrom':
            self.selection = 0
            self.notifyListeners()

        # Show window
        PlayWindow(self)
        
