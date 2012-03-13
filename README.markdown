
DFA Builder
===========

This allows building a DFA representing a simple game.


## TODO

### UI work

+ Disallow setting start state as 'end'
+ Disallow creating transitions out of an end state?
+ Disallow setting a state as ending if it has transitions out of it?
+ Show file name in title bar
+ Show the text of the "to" state in a tooltip when creating
  transitions 
+ Fix line wrapping for state text
+ Reduce number of 'changes' from state text

### Logic work

+ Create logic to check for errors
  + Unreachable states
  + Inescapable loops / dead-ends 
  
+ Create undo / redo logic
  + Should be efficient with regards to text updates
  + Add redo logic
  
