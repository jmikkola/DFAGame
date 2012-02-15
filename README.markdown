
DFA Builder
===========

This allows building a DFA representing a simple game.


## TODO

### Graph rendering

+ Display vertices
  + Make them rounded
  + Set their color
  + Show current selection
  + Show their number?
  + Lay out - force based model?
+ Draw edges
  + Arrows
  + Antialiased
+ Make verices clickable
  
### UI work

+ Create menu bar
  + File menu: open, new, save, save as, close
  + Edit menu: undo, redo
  + Game menu: play, play from selected, check for errors
  
+ 'Add' button to add transitions should not work if there is no transition text
+ Button for removing states should not work if state selected is the start state


### Logic work

+ Create logic to check for errors
  + Unreachable states
  + Inescapable loops
  
+ Connect actions in view to logic
  + Selecting a state via the graph
  + Undoing
  + Redoing
  + Saving
  + Opening
  + Closing
  + Changing state text
  + Adding a transition
  + Removing transitions

+ Connect displays in view to logic
  + Graph
  + State text
  + State selection
  + Transition list
