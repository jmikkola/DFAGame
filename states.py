
class State:
    ''' This class represents a single state
    and its transitions '''
    def __init__(self, text, transitions=None):
        self.text = text
        self.transitions = transitions if transitions else dict()

    def addTransition(self, command, state):
        ''' Adds a transition to State object in
        state with the command text from command '''
        self.transitions[command] = state

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

    def removeConnections(self, state):
        ''' Removes all transition to a given state '''
        for cmd, s in self.transitions:
            if s == state:
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
            self.states.append(State(v['state']))
        for i,v in serialized.iteritems():
            start = self.states[i]
            transitions = v['transitions']
            for cmd,j in transitions.iteritems():
                end = self.states[j]
                self.addTransition(start, end, cmd)
        
    def addState(self, text):
        ''' Adds a State object with the given text to the 
        graph, and returns the new state object '''
        state = State(text)
        self.states.append(state)
        return state

    def removeState(self, state):
        ''' Removes a state from the graph '''
        del self.states[self.states.index(state)]
        for s in self.states:
            state.removeConnections(s)

    def addTransition(self, start, end, command):
        ''' Adds a transition from the start state to the
        end state on the given command '''
        start.addTransition(command, end)
        
    def removeTransition(self, start, command):
        ''' Removes a transition starting at start with
        the given command '''
        start.removeTransition(command)

    def toSerializable(self):
        numbers = dict((v,i) for (i,v) in enumerate(self.states))
        out = dict()
        for i,v in enumerate(self.states):
            trns = dict((cmd,numbers[st]) for (cmd,st) \
                            in v.transitions.iteritems())
            out[i] = {'state': v.text, 'transitions': trns} 
        return out
        

if __name__ == '__main__':
    import json
    g = Graph()
    sn1 = g.addState('first state')
    sn2 = g.addState('another state')
    sn3 = g.addState('third state')
    g.addTransition(sn1, sn2, 'go up')
    g.addTransition(sn1, sn3, 'pass')
    g.addTransition(sn2, sn1, 'go down')
    g.addTransition(sn2, sn3, 'continue')
    g.addTransition(sn3, sn1, 'back')
    s = g.toSerializable()
    print json.dumps(s, indent=2)
    g2 = Graph(s)
    print json.dumps(g2.toSerializable(), indent=2)
