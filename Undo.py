#!/usr/bin/env python

class Undo:
    ''' Stores the undo history of the editing session '''

    def __init__(self):
        # Number of unsaved changes
        self.undo_depth = 0
        # Storage for change history
        self.undo_stack = []

    def stateSaved(self):
        ''' Store the fact that the file was saved '''
        self.undo_depth = 0
        self.undo_stack = []

    def unsavedChanges(self):
        ''' Returns True if there are unsaved changes '''
        return self.undo_depth != 0

    def pushHistory(self, item):
        ''' Store the data to reverse a change '''
        self.undo_stack.append(item)
        self.undo_depth += 1

    def undo(self):
        ''' Undo a change. Returns the stored state. '''
        if self.unsavedChanges():
            item = self.undo_stack.pop()
            self.undo_depth -= 1
            return item
        return None


    
