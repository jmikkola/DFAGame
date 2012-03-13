
DFA Builder
===========

This allows building a DFA representing a simple game.


## TODO

### UI work

+ Show the text of the "to" state in a tooltip when creating
  transitions 
+ Fix line wrapping for state text
+ Reduce number of 'changes' from state text
+ Disallow creating transitions out of an end state?
+ Disallow setting a state as ending if it has transitions out of it?

### Logic work

+ Create logic to check for errors
  + Unreachable states
  + Inescapable loops / dead-ends 
  
+ Create undo / redo logic
  + Should be efficient with regards to text updates
  + Add redo logic
  
