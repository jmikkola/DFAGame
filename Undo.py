#!/usr/bin/env python

from Model import *

class Undo:
    ''' Stores the undo history of the editing session '''

    def __init__(self, controller, graph):
        self.controller = controller
        self.graph = graph
        # Number of unsaved changes
        self.last_save = 0
        # Storage for change history
        self.undo_stack = []
        self.redo_stack = []

    def stateSaved(self):
        ''' Store the fact that the file was saved '''
        self.last_save = 0
        self.undo_stack = []

    def unsavedChanges(self):
        ''' Returns True if there are unsaved changes '''
        return self.last_save != 0

    def pushHistory(self, item):
        ''' Store the data to reverse a change '''
        self.undo_stack.append(item)
        self.last_save += 1

    def pushRedo(self, item):
        ''' Store the data to redo a change 
        after an undo '''
        self.redo_stack.append(item)
        

    def undo(self):
        ''' Undo a change. Returns the stored state. '''
        if self.undo_stack:
            item = self.undo_stack.pop()
            self.last_save -= 1
            rev = self.reverse_action(item)
            self.redo_stack.append(rev)

    def redo(self):
        ''' Redo a change. Returns the stored state. '''
        if self.redo_stack:
            item = self.redo_stack.pop()
            self.last_save += 1
            rev = self.reverse_action(item)
            self.undo_stack.append(rev)

    def reverse_action(self, item):
        ''' Reverse a previous action (whether undo or redo), 
        and returns the details to undo the change it makes ''' 
        num = item[0]
        kind = item[1]
        graph = self.graph

        # Undo an addition of a state
        if kind == 'added':
            history = graph.removeState(num)
            if self.controller.selection == num:
                self.controller.selection -= 1
            self.controller.recalcPositions()
            return history

        # Undo a removal of a state
        if kind == 'removed':
            # Build state & insert it back into the list
            s = item[2]
            state = State(s['state'], None, s['x'], s['y'], s['end'])
            graph.states.insert(num, state)
            # Add outgoing transitions
            for cmd, n in s['transitions'].iteritems():
                state.addTransition(cmd, graph.getState(n))
            # Add incoming transitions
            incoming = item[3]
            for n, cmd in incoming:
                graph.getState(n).addTransition(cmd, state)
            history = (num, 'added')

        # Undo a change of state text
        elif kind == 'text':
            state = graph.getState(num)
            old = state.setText(item[2])
            history = (num, 'text', old)

        # Undo an addition of a transition
        elif kind == 'addtr':
            command = item[2]
            history = graph.removeTransition(num, command)

        # Undo a removal of a transition
        elif kind == 'rmtr':
            state = graph.getState(num)
            to = graph.getState(item[3])
            command = item[2]
            state.addTransition(command, to)
            history = (num, 'addtr', command)

        # Undo a toggle of the 'end' value
        elif kind == 'end':
            state = graph.getState(num)
            history = (num, 'end', state.end)
            state.end = item[2]

        # Undo a repositioning of a state
        elif kind == 'move':
            state = graph.getState(num)
            history = (num, 'move', state.getPosition())
            x, y = item[2]
            state.setPosition(x, y)

        # The 'huh?' case
        else:
            raise Exception('Unknown action type: ' + kind)

        # All undos except an addition select the 
        # related state
        self.controller.selection = num

        return history


    def __str__(self):
        return 'Undo: ' + str(self.undo_stack) + \
               '\nRedo: ' + str(self.redo_stack) + \
               '\nLast save: ' + str(self.last_save)


    
