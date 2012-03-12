
DFA Builder
===========

This allows building a DFA representing a simple game.


## TODO

### Graph rendering

+ Display vertices
  + Display state numbers on the state?
  
### UI work

+ Disable game modifications while playing game  
+ 'Add' button to add transitions should not work if there is no
  transition text 
+ Button for removing states should not work if state selected is the
  start state 
+ Button to add transitions should warn on over-writing existing
  transition 
+ Create keyboard shortcuts
+ Show file name in title bar
+ Show the text of the "to" state in a tooltip when creating
  transitions 
+ Fix line wrapping for state text
+ Reduce number of 'changes' from state text

### Logic work

+ Disallow over-writing transitions

+ Create logic to check for errors
  + Unreachable states
  + Inescapable loops
  
+ Create undo / redo logic
  + Should be efficient with regards to text updates
  + Add redo logic
  
