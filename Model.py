#!/usr/bin/env python

import json
from Queue import Queue

class State:
    ''' This class represents a single state
    and its transitions '''
    def __init__(self, text, transitions=None, x=0, y=0, end=False):
        self.text = text
        self.transitions = transitions if transitions else dict()
        self.x = x
        self.y = y
        self.end = end

    def setText(self, text):
        ''' Sets the text, returning the previous value '''
        old = self.text
        self.text = text
        return old

    def getPosition(self):
        return (self.x, self.y)

    def setPosition(self, x, y):
        ''' Sets the position of the state, returning the 
        previous position '''
        prev = (self.x, self.y)
        self.x = x
        self.y = y
        return prev

    def addTransition(self, command, state):
        ''' Adds a transition to State object in
        state with the command text from command '''
        self.transitions[command] = state

    def getTransition(self, command):
        ''' Returns the transition taken from
        that command '''
        return self.transitions[command]

    def listTransitions(self):
        ''' Returns a list of all transition commands and states '''
        return [(k,v) for (k,v) in self.transitions.iteritems()]

    def removeTransition(self, command):
        ''' Removes a transition with the given command '''
        del self.transitions[command]

    def removeConnections(self, state):
        ''' Removes all transition to a given state '''
        toRemove = []
        for cmd, s in self.transitions.iteritems():
            if s == state: toRemove.append(cmd)
        for cmd in toRemove:
            del self.transitions[cmd]
        return toRemove
                
    def __str__(self):
        s = self.text + "@" + str(x) + ',' + str(y) + " : {"
        for k,v in self.transitions.iteritems():
            s += repr(k) + ": " + repr(v.text) + ", "
        return s + "}"

class Graph:
    ''' This class stores an entire transition graph made
    out of State objects.'''
    def __init__(self, serialized=None):
        if serialized:
            self._readSerialized(serialized)
        else:
            self.states = []

    def _readSerialized(self, serialized):
        ''' Reads in the graph from a serialized format '''
        self.states = []

        # Read in states with text and attirbutes
        for st in serialized:
            state = State(st['state'], None, st['x'], st['y'], st['end'])
            self.states.append(state)

        # Add transitions between states
        for i,st in enumerate(serialized):
            start = self.states[i]
            for (cmd,j) in st['transitions'].iteritems():
                self.addTransition(start, self.states[j], cmd)

    def numStates(self):
        ''' Returns the number of states '''
        return len(self.states)

    def getState(self, index):
        ''' Gets the state at the given index '''
        return self.states[index]

    def getIndex(self, state):
        ''' Returns the index of the state '''
        return self.states.index(state)

    def addState(self, text='', x=0, y=0):
        ''' Adds a State object with the given text to the 
        graph, and returns the new state object '''
        state = State(text, None, x, y, False)
        self.states.append(state)
        return state

    def removeState(self, index):
        ''' Removes a state by index from the graph.
        Returns a history tuple of the format
        (index, 'removed', serializedState, incoming)
        where incoming is a list of tuples of the form
        (fromIndex, command)
        '''
        state = self.states[index]
        srlState = self.serializeState(index)
        incoming = []
        for (i, s) in enumerate(self.states):
            if i == index: 
                continue
            commands = s.removeConnections(state)
            for c in commands:
                incoming.append( (i, c) )
        self.states.pop(index)
        return (index, 'removed', srlState, incoming)
            

    def addTransition(self, start, end, command):
        ''' Adds a transition from the start state to the
        end state on the given command '''
        start.addTransition(command, end)
        
    def removeTransition(self, startNo, command):
        ''' Removes a transition starting at start with
        the given command '''
        start = self.getState(startNo)
        to = start.getTransition(command)
        if to:
            start.removeTransition(command)
            toind = self.getIndex(to)
            return (startNo, 'rmtr', command, toind)
        return None

    def toSerializable(self):
        ''' Converts graph into a format that can be
        serialized into JSON '''
        return map(self.serializeState, xrange(self.numStates()))

    def serializeState(self, stateNo):
        state = self.states[stateNo]
        transitions = dict()
        for (cmd, to) in state.transitions.iteritems():
            transitions[cmd] = self.getIndex(to)
        return {
            'state': state.text,
            'x': state.x, 'y': state.y,
            'end': state.end,
            'transitions': transitions }

    def getEndingStates(self):
        ''' Returns a list of all ending states '''
        return [i for i,st in enumerate(self.states) if st.end]

    def getUnreachable(self):
        ''' Returns a list of any unreachable states '''
        # Perform a breadth-first search
        reached = set()
        queue = Queue()
        start = self.states[0]
        queue.put(start)
        reached.add(start)
        while not queue.empty():
            state = queue.get()
            for (_, st) in state.listTransitions():
                if not st in reached:
                    reached.add(st)
                    queue.put(st)
        return self.listNotIncluded(reached)

    def getInescapable(self):
        ''' Returns a list of inescapable states 
        (those from which an ending state cannot be reached) '''
        reachEnd = set(st for st in self.states if st.end)
        updated = True
        while updated:
            updated = False
            for state in self.states:
                if state in reachEnd:
                    continue
                for (_, st) in state.listTransitions():
                    if st in reachEnd:
                        reachEnd.add(state)
                        updated = True
                        break
        return self.listNotIncluded(reachEnd)

    def listNotIncluded(self, states):
        ''' Takes a set of states and returns a 
        list of the indcies of states not in that set '''
        unreached = []
        for i in xrange(self.numStates()):
            if not self.states[i] in states:
                unreached.append(i)
        return unreached
        

def saveGraph(graph, filename):
    ''' Saves the graph to the given file name '''
    with open(filename, 'w') as outf:
        json.dump(graph.toSerializable(), outf)

def loadGraph(filename):
    ''' Loads a graph from a file '''
    with open(filename) as inf:
        j = json.load(inf)
    return Graph(serialized=j)
