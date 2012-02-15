#!/usr/bin/env python

import json

class State:
    ''' This class represents a single state
    and its transitions '''
    def __init__(self, text, transitions=None, attributes=None):
        self.text = text
        self.transitions = transitions if transitions else dict()
        self.attributes = attributes if attributes else dict()

    def getAttribute(self, key):
        ''' Returns the value of the attribute '''
        if key in self.attributes:
            return self.attributes[key]
        return None

    def addAttribute(self, key, value):
        ''' Sets the value of the attribute '''
        self.attributes[key] = value

    def removeAttribute(self, key):
        ''' Removes the attribute from the state '''
        if key in self.attributes:
            del self.attributes[key]

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
                
    def __str__(self):
        s = self.text + " : {"
        for k,v in self.transitions.iteritems():
            s += repr(k) + ": " + repr(v.text) + ", "
        return s + "}"

class Graph:
    ''' This class stores an entire transition graph made
    out of State objects.'''
    def __init__(self, serialized=None):
        self.states = []
        if serialized:
            self._readSerialized(serialized)

    def _readSerialized(self, serialized):
        ''' Reads in the graph from a serialized format '''
        for i,v in serialized.iteritems():
            assert(i == len(self.states))
            state = State(v['state'], attributes=v['attributes'])
            self.states.append(state)
        for i,v in serialized.iteritems():
            start = self.states[i]
            transitions = v['transitions']
            for cmd,j in transitions.iteritems():
                end = self.states[j]
                self.addTransition(start, end, cmd)

    def numStates(self):
        ''' Returns the number of states '''
        return len(self.states)

    def getState(self, index):
        ''' Gets the state at the given index '''
        return self.states[index]

    def getIndex(self, state):
        ''' Returns the index of the state '''
        return self.states.index(state)
        
    def addState(self, text='', attributes=None):
        ''' Adds a State object with the given text to the 
        graph, and returns the new state object '''
        state = State(text, attributes=attributes)
        self.states.append(state)
        return state

    def removeState(self, index):
        ''' Removes a state by index from the graph '''
        state = self.states.pop(index)
        for s in self.states:
            s.removeConnections(state)

    def addTransition(self, start, end, command):
        ''' Adds a transition from the start state to the
        end state on the given command '''
        start.addTransition(command, end)
        
    def removeTransition(self, start, command):
        ''' Removes a transition starting at start with
        the given command '''
        start.removeTransition(command)

    def toSerializable(self):
        ''' Converts graph into a format that can be
        serialized into JSON '''
        numbers = dict((v,i) for (i,v) in enumerate(self.states))
        out = dict()
        for i,v in enumerate(self.states):
            trns = dict((cmd,numbers[st]) for (cmd,st) \
                            in v.transitions.iteritems())
            out[i] = {'state': v.text, 
                      'transitions': trns,
                      'attributes': v.attributes} 
        return out
        

def saveGraph(graph, filename):
    ''' Saves the graph to the given file name '''
    with open(filename, 'w') as outf:
        json.dump(graph.toSerializable(), outf)

def loadGraph(filename):
    ''' Loads a graph from a file '''
    with open(filename) as inf:
        j = json.load(inf)
    return Graph(serialized=j)

def playGame(graph):
    # TODO: add a method for getting the start state
    state = graph.getState(0)
    while not state.getAttribute('final'):
        print state.text, "\n"
        options = state.listTransitions()
        for i,option in enumerate(options):
            print "\t%2d> %s" % (i+1, option)
        choice = int(raw_input('Select an option: ')) - 1
        state = state.getTransition(options[choice])
        print ""
    print "end of game"

if __name__ == '__main__':
    g = Graph()
    sn1 = g.addState('first state')
    sn1.addAttribute('start', True)
    sn2 = g.addState('another state')
    sn3 = g.addState('third state')
    sn3.addAttribute('final', True)
    g.addTransition(sn1, sn2, 'go up')
    g.addTransition(sn1, sn3, 'pass')
    g.addTransition(sn2, sn1, 'go down')
    g.addTransition(sn2, sn3, 'continue')
    g.addTransition(sn3, sn1, 'back')
    #s = g.toSerializable()
    #print json.dumps(s, indent=2)
    playGame(g)
    
