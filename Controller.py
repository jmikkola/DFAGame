
from os import path

from Model import *
from Undo import *
from View import *
from PlayWindow import *

class Controller:
    ''' Handles connection between the 
    view and the model, and keeps some
    state for the UI. '''

    def __init__(self):
        # Set up default graph to show
        self.resetGraph()
        # UI-related values
        self.notifying = False
        self.isPlaying = False
        # Set up listeners
        self.listeners = set()
        self.fileListeners = set()

    def resetGraph(self):
        ''' Reset to a new graph '''
        # Graph display values
        self.maxXdist = 0
        self.maxYdist = 0
        self.space = 50
        self.nPositions = 0
        self.selection = 0
        # File state
        self.fileOpen = None
        self.unsavedChanges = False
        # Undo state
        self.history = Undo()
        # Graph
        self.graph = Graph()
        state = self.graph.addState('Start state')
        self.setPosition(state)



    def main(self):
        ''' This method starts the program '''
        self.builderWindow = BuilderWindow(self)
        # Transfer control to GTK event loop
        gtk.main()

    def exit(self, menu, data=None):
        ''' Exit the program '''
        if self.checkClose():
            gtk.main_quit()

    # ----------------------------------
    # Functions regarding updating state
    # (i.e. observer pattern)
    # ----------------------------------

    def registerListener(self, function, fileUpdates=False):
        ''' Adds a listener function (which should ahve no 
        arguments) to the list that will be updated. Set 
        fileUpdates to True to get updates on file state. '''
        self.listeners.add(function)
        if fileUpdates:
            self.fileListeners.add(function)

    def notifyListeners(self, updateGraph=True):
        ''' Notifies the listeners that had registered. 
        If no kinds are specified, all listeners are notified. '''

        # Don't notify recursively:
        if self.notifying: return
        self.notifying = True

        # Select who to notify
        if updateGraph:
            listeners = self.listeners
        else:
            listeners = self.fileListeners

        # Notify all selected
        for function in listeners:
            function()

        # Allow notifications again
        self.notifying = False

    # ----------------------------------
    # Functions for getting state
    # ----------------------------------

    def getCurrentState(self):
        ''' Returns the state object currently selected '''
        return self.graph.getState(self.selection)

    def getFile(self):
        ''' Returns the file name of the currently open file, 
        or an empty string if there is none '''
        if self.fileOpen:
            return path.basename(self.fileOpen)
        return ''

    # ----------------------------------
    # Functions for UI events
    # ----------------------------------

    def createState(self, widget, *args):
        ''' Creates a new state and selects it '''
        self.unsavedChanges = True
        # Make change
        state = self.graph.addState()
        self.selection = self.graph.numStates() - 1
        # Store undo history
        hist = (self.selection, 'added')
        self.history.pushHistory(hist)
        # Update
        self.setPosition(state)
        self.notifyListeners()

    def selectStateListener(self, widget):
        ''' Call back for widgets that change the 
        selection '''
        self.selectState(widget.get_active())

    def selectState(self, index):
        ''' Changes the current selection '''
        if index >= 0 and index != self.selection:
            oldSelection = self.selection
            self.selection = index
            self.notifyListeners()

    def removeState(self, widget):
        ''' Removes the selected state (if it is not the 
        state state) '''
        num = self.selection
        graph = self.graph
        if num is 0: return
        self.unsavedChanges = True
        # Make change
        serialized = graph.serializeState(num)
        removed = graph.removeState(num)
        self.selection -= 1
        #  undo history
        hist = (num, 'removed', serialized, removed)
        self.history.pushHistory(hist)
        # Update
        self.recalcPositions()
        self.notifyListeners()

    def updateStateText(self, widget):
        ''' Changes the text of the current state '''
        self.unsavedChanges = True
        # Store undo history
        state = self.getCurrentState()
        hist = (self.selection, 'text', state.text)
        self.history.pushHistory(hist)
        # Make change
        text = widget.get_text(widget.get_start_iter(), \
                               widget.get_end_iter())
        state.text = text
        # No re-draw needed, just 'saved' state
        self.notifyListeners(False)

    def createTransition(self, widget, data=None):
        ''' Creates a new transition from the current state '''
        # Get info
        command, endNo = data
        start = self.getCurrentState()
        # disallow overwriting transitions
        if command in start.transitions:
            return False
        self.unsavedChanges = True
        end = self.graph.getState(endNo)
        # Store undo history
        hist = (self.selection, 'addtr', command)
        self.history.pushHistory(hist)
        # Make change & update
        self.graph.addTransition(start, end, command)
        self.notifyListeners()
        return True

    def removeTransition(self, widget, command):
        ''' Removes a transition from the selected state '''
        self.unsavedChanges = True
        start = self.getCurrentState()
        # Store undo history
        to = self.graph.getIndex(start.getTransition(command))
        hist = (self.selection, 'rmtr', command, to)
        self.history.pushHistory(hist)
        # Make change & update
        self.graph.removeTransition(start, command)
        self.notifyListeners()

    def setEndingState(self, widget):
        ''' Changes whether the selected state is an ending 
        (accept/final) state '''
        # Get info
        isEnding = widget.get_active()
        state = self.getCurrentState()
        old_isEnding = state.end
        # Only update if different
        if isEnding != old_isEnding:
            self.unsavedChanges = True
            # Store undo history
            hist = (self.selection, 'end', old_isEnding)
            self.history.pushHistory(hist)
            # Make change & update
            state.end = isEnding
            self.notifyListeners()

    def undo(self, menu, data=None):
        # Get the undo history
        item = self.history.undo()
        if item is None:
            return
        
        num = item[0]
        kind = item[1]
        graph = self.graph

        # Undo the right kind of action:
        if kind == 'added':
            graph.removeState(num)
            if self.selection == num:
                self.selection -= 1
            self.recalcPositions()
        elif kind == 'removed':
            s = item[2]
            state = State(s['state'], None, s['x'], s['y'], s['end'])
            graph.states.insert(num, state)
            for cmd, n in s['transitions'].iteritems():
                state.addTransition(cmd, graph.getState(n))
            incoming = item[3]
            for n, cmd in incoming:
                graph.getState(n).addTransition(cmd, state)
        elif kind == 'text':
            state = graph.getState(num)
            state.text = item[2]
        elif kind == 'addtr':
            state = graph.getState(num)
            command = item[2]
            state.removeTransition(command)
        elif kind == 'rmtr':
            state = graph.getState(num)
            command = item[2]
            to = graph.getState(item[3])
            state.addTransition(command, to)
        elif kind == 'end':
            state = graph.getState(num)
            state.end = item[2]
        elif kind == 'move':
            state = graph.getState(num)
            x, y = item[2]
            state.setPosition(x, y)

        # Update
        self.unsavedChanges = self.history.unsavedChanges()
        self.notifyListeners()
            

    def redo(self, menu, data=None):
        print menu


    # ----------------------------------
    # Functions for file handling
    # ----------------------------------

    def saveGame(self, menu, data=None):
        # Get file name
        filename = self.fileOpen
        # Save or save as?
        if filename is None or menu == 1:
            filename = fileDialog(save=True)
        if filename:
            # Check for overwriting existing file
            if self.fileOpen is None and path.exists(filename):
                if not askYesNO('Overwrite existing file?'):
                    return False
            # Save file
            saveGraph(self.graph, filename)
            self.unsavedChanges = False
            self.history.stateSaved()
            self.notifyListeners(False)
            return True
        return False

    def newGame(self, menu, data=None):
        if not self.checkClose(False):
            return
        self.resetGraph()
        self.notifyListeners()

    def openGame(self, menu, data=None):
        # Check for unsaved changes
        if not self.checkClose(False):
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
        self.undo = Undo()
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
        

    # ----------------------------------
    # Functions for graph display
    # ----------------------------------

    def getNextPosition(self):
        ''' Computes and available position for 
        placing the node. '''
        xd, yd = self.maxXdist, self.maxYdist
        sp = self.space
        if xd < yd: return (xd + sp, sp)
        else:       return (sp, yd + sp)

    def moveState(self, stateNo, position):
        ''' Moves a state (use for UI events) '''
        self.unsavedChanges = True
        state = self.graph.getState(stateNo)
        # Store undo history
        hist = (stateNo, 'move', state.getPosition())
        self.history.pushHistory(hist)
        # Make change & update
        self.setStatePosition(state, position)
        self.notifyListeners()

    def setStatePosition(self, state, position):
        ''' Updates or sets the position of a state 
        (Don't use directly)'''
        # Make change
        x, y = position
        state.setPosition(x, y)
        # Update dimensions
        self.recalcPositions()

    def recalcPositions(self):
        ''' Recalculates the dimensions after a removal '''
        xmax, ymax = 0, 0 # assuming positions are positive
        for state in self.graph.states:
            x, y = state.getPosition()
            xmax = max(xmax, x)
            ymax = max(ymax, y)
        self.maxXdist = xmax
        self.maxYdist = ymax

    def setPosition(self, state):
        ''' Sets up the position of a newly added state '''
        x, y = state.getPosition()
        if not x or not y:
            self.setStatePosition(state, self.getNextPosition())
        else:
            self.maxXdist = max(self.maxXdist, x)
            self.maxYdist = max(self.maxYdist, y)
        

    # ----------------------------------
    # Functions for demoing the game
    # ----------------------------------

    def startGame(self, menu, data=None):
        # Don't allow to instances at once
        if self.isPlaying:
            return
        self.isPlaying = True
        # isPlaying gets set back to False by PlayWindow.delete_event()
        self.builderWindow.vb.set_sensitive(False)
        
        # Unless the game will start from the selected
        # state, move to the start state
        if menu != 1:
            self.selection = 0
            self.notifyListeners()

        # Show window
        PlayWindow(self)

    def stopGame(self):
        self.isPlaying = False
        self.builderWindow.vb.set_sensitive(True)
        
