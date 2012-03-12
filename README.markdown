
DFA Builder
===========

This allows building a DFA representing a simple game.


## TODO

### Graph rendering

+ Display vertices
  + Display state numbers on the state?
  
### UI work

+ Create menu bar
  + Game menu: play, play from selected, check for errors
  
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

### Logic work

+ Create logic to check for errors
  + Unreachable states
  + Inescapable loops
  
+ Connect actions in view to logic
  + Undoing
  + Redoing

+ Create undo / redo logic
  + Must update state of unsavedChanges.  
	Mark a undo entry as the one representing what is saved on disk?
  + Should be efficient with regards to text updates
  
