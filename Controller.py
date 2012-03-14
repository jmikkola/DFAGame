
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
        # Graph
        self.graph = Graph()
        state = self.graph.addState('Start state')
        self.setPosition(state)
        # Undo state
        self.history = Undo(self, self.graph)


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
        listeners = self.listeners if updateGraph else self.fileListeners

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
        self.history.pushHistory((self.selection, 'added'))
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
        history = graph.removeState(num)
        self.selection -= 1
        #  undo history
        self.history.pushHistory(history)
        # Update
        self.recalcPositions()
        self.notifyListeners()

    def updateStateText(self, widget):
        ''' Changes the text of the current state '''
        self.unsavedChanges = True
        # Make change
        state = self.getCurrentState()
        text = widget.get_text(widget.get_start_iter(), \
                               widget.get_end_iter())
        old = state.setText(text)
        # Store undo history
        hist = (self.selection, 'text', old)
        self.history.pushHistory(hist)
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
        # Make change & update
        history = self.graph.removeTransition(self.selection, command)
        # Store undo history
        self.history.pushHistory(history)
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
        # Undo the action
        self.history.undo()
        # Update
        self.unsavedChanges = self.history.unsavedChanges()
        self.notifyListeners()
            
    def redo(self, menu, data=None):
        # Get the redo history
        self.history.redo()
        # Update
        self.unsavedChanges = self.history.unsavedChanges()
        self.notifyListeners()

    def checkGame(self, menu, data=None):
        problems = []
        warnings = []
        g = self.graph

        # Check for states with no text
        for i in xrange(g.numStates()):
            st = g.getState(i)
            if not st.text.strip():
                warnings.append('State #' + str(i) + ' has no text.')

        # Ensure there are ending states
        endingStates = g.getEndingStates()
        if not endingStates:
            problems.append('There are no ending states.')

        # Check for transitions out of ending states
        for i in endingStates:
            endst = g.getState(i)
            if endst.transitions:
                problems.append('End state #' + str(i) + ' has exiting transitions.')

        # Check for unreachable states
        if g.getUnreachable():
            problems.append('There are unreachable states.')

        # Check for states that cannot reach an ending state
        inescapable = g.getInescapable()
        for i in inescapable:
            problems.append('State #' + str(i) + ' cannot reach an end state.')
        
        # Output results
        message = str(len(problems)) + ' problems\n'
        message += '\n'.join(problems) + '\n\n'
        message += str(len(warnings)) + ' warnings\n'
        message += '\n'.join(warnings)
        showMessage(message, 'Results of checking for errors')


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
        self.history = Undo(self, self.graph)
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
        
