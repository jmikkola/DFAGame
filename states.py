
class State:
    ''' This class represents a single state
    and its transitions '''
    def __init__(self, number, text):
        self.number = number
        self.text = text
        self.transitions = dict()

    def addTransition(self, command, state):
        ''' Adds a transition to State object in
        state with the command text from command '''
        self.transitions[command] = state.number

    def getTransition(self, command):
        ''' Returns the transition taken from
        that command '''
        return self.transitions[command]

    def listTransitions(self):
        ''' Returns a list of all transition commands '''
        return [k for (k,v) in self.transitions.iteritems()]

    def removeTransition(self, command):
        ''' Removes a transition with the given command '''
        del self.transitions[command]

    def removeConnections(self, stateNo):
        ''' Removes all transition to a given state number '''
        for cmd, n in self.transitions:
            if n == stateNo:
                del self.transitions[cmd]

class Graph:
    ''' This class stores an entire transion graph made
    out of State objects.'''
    def __init__(self):
        self.states = dict()
        self._noIssued = 0
        
    def addState(text):
        ''' Adds a State object with the given text to the 
        graph, and returns the state number at which it is stored '''
        stateNo = self._noIssued
        self._noIssued += 1
        self.states[stateNo] = State(stateNo, text)
        return stateNo

    def removeState(num):
        ''' Removes a state (by number) from the graph '''
        del self.state[num]
        for n, state in self.states.iteritems():
            state.removeConnections(num)

    def addTransition(state1, state2, command):
        ''' Adds a transition from the state with number 
        state1 to the state with number state2 '''
        s1 = self.states[state1]
        s2 = self.states[state2]
        s1.addTransition(command, s2)
        
    def removeTransition(state1, command):
        ''' Removes a transition starting at state1 with
        the given command '''
        s1 = self.states[state1]
        s1.removeTransition(command)
        
